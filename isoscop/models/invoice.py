# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_is_zero

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    primeCEE = fields.Float('Prime CEE')
    date_prior_visit = fields.Date('Date de visite préalable')
    date_start_work = fields.Date('Date de début des travaux')

    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        return  self.type == 'out_invoice' and self.state == 'draft' and _('Draft Invoice') or \
                self.type == 'out_invoice' and self.state in ('open','in_payment','paid') and _('Invoice - %s - %s') % (self.number, self.partner_id.name) or \
                self.type == 'out_refund' and self.state == 'draft' and _('Credit Note') or \
                self.type == 'out_refund' and _('Credit Note - %s - %s') % (self.number, self.partner_id.name) or \
                self.type == 'in_invoice' and self.state == 'draft' and _('Vendor Bill') or \
                self.type == 'in_invoice' and self.state in ('open','in_payment','paid') and _('Vendor Bill - %s - %s') % (self.number, self.partner_id.name) or \
                self.type == 'in_refund' and self.state == 'draft' and _('Vendor Credit Note') or \
                self.type == 'in_refund' and _('Vendor Credit Note - %s - %s') % (self.number, self.partner_id.name)
                
    @api.onchange('invoice_line_ids')
    def load_section_product(self):
        new_lines = self.env['account.invoice.line']
        for line in self.invoice_line_ids:
            if line.product_id.layout_category and line.display_type not in ('line_section', 'line_note'):
                section_ids = self.invoice_line_ids.filtered(lambda x: x.display_type == 'line_section' and x.name == line.product_id.layout_category)
                if not section_ids:
                    seq = line.sequence - 1
                    datas = {
                            'name': line.product_id.layout_category,
                            'sequence': seq,
                            'display_type': 'line_section'
                        }
                                    
                    new_line = self.env['account.invoice.line'].new(datas)                    
                    new_lines += new_line
            
            self.update({'invoice_line_ids': self.invoice_line_ids | new_lines})
    
    
    @api.model
    def _get_payments_vals_report(self):
        if not self.payment_move_line_ids:
            return []
        payment_vals = []
        currency_id = self.currency_id
        for payment in self.payment_move_line_ids:
            if 'CEE' not in payment.journal_id.name:
                ###on retire les paiements CEE pour l'impression
                payment_currency_id = False
                if self.type in ('out_invoice', 'in_refund'):
                    amount = sum([p.amount for p in payment.matched_debit_ids if p.debit_move_id in self.move_id.line_ids])
                    amount_currency = sum(
                        [p.amount_currency for p in payment.matched_debit_ids if p.debit_move_id in self.move_id.line_ids])
                    if payment.matched_debit_ids:
                        payment_currency_id = all([p.currency_id == payment.matched_debit_ids[0].currency_id for p in
                                                   payment.matched_debit_ids]) and payment.matched_debit_ids[
                                                  0].currency_id or False
                elif self.type in ('in_invoice', 'out_refund'):
                    amount = sum(
                        [p.amount for p in payment.matched_credit_ids if p.credit_move_id in self.move_id.line_ids])
                    amount_currency = sum([p.amount_currency for p in payment.matched_credit_ids if
                                           p.credit_move_id in self.move_id.line_ids])
                    if payment.matched_credit_ids:
                        payment_currency_id = all([p.currency_id == payment.matched_credit_ids[0].currency_id for p in
                                                   payment.matched_credit_ids]) and payment.matched_credit_ids[
                                                  0].currency_id or False
                # get the payment value in invoice currency
                if payment_currency_id and payment_currency_id == self.currency_id:
                    amount_to_show = amount_currency
                else:
                    currency = payment.company_id.currency_id
                    amount_to_show = currency._convert(amount, self.currency_id, payment.company_id, self.date or fields.Date.today())
                if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                    continue
                payment_ref = payment.move_id.name
                if payment.move_id.ref:
                    payment_ref += ' (' + payment.move_id.ref + ')'
                payment_vals.append({
                    'name': payment.name,
                    'journal_name': payment.journal_id.name,
                    'amount': amount_to_show,
                    'currency': currency_id.symbol,
                    'digits': [69, currency_id.decimal_places],
                    'position': currency_id.position,
                    'date': payment.date,
                    'payment_id': payment.id,
                    'account_payment_id': payment.payment_id.id,
                    'invoice_id': payment.invoice_id.id,
                    'move_id': payment.move_id.id,
                    'ref': payment_ref,
                })
        return payment_vals