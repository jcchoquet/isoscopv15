# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

DEFAULT_TERM = []
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    primeCEE = fields.Float('Prime CEE')
    date_prior_visit = fields.Date('Date de visite préalable',default=fields.Date.today())
    order_terms = fields.One2many('sale.order.terms', 'order_id', string='Echéances',copy=True, readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    type_heating = fields.Selection([('combustible', 'Combustible'),('electrique','Eléctrique'),('electricite', 'Electricité'),
    ('gaz_naturel','Gaz naturel'),('propane','Propane'), ('fioul','Fioul'), ('bois','Bois'), ('autre','Autre')], string="Type de chauffage")
    livable_area = fields.Integer('Surface habitable')
    type_primeCEE = fields.Selection([('cp_non_precaire', 'Coup de pouce non precaire '),('cp_precarite', 'Coup de pouce precarité'),('cp_grande_precarite', 'Coup de pouce grande précarité '), ('non_precaire','Non precaire'), ('precarite','Précarité'), ('grande_precarite','Grande précarité')],string='Type de prime')
     
    def _prepare_invoice(self):
        invoice_vals = result = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['primeCEE'] = self.primeCEE
        invoice_vals['date_prior_visit'] = self.date_prior_visit
        return invoice_vals

    @api.model
    def default_get(self, fields_list):
        defaults = super(SaleOrder, self).default_get(fields_list)
        vals = False
        if self.env.user.company_id.id != 2:
            vals = [(0, 0, {'name': '30% signature', 'rate': 30}),(0, 0, {'name': '30% mi-chantier', 'rate': 30}),(0, 0, {'name': '30% fin chantier', 'rate': 30}),(0, 0, {'name': '10% réception facture', 'rate': 10})]
        elif  self.env.user.company_id.id == 2:
            vals = [(0, 0, {'name': '30% signature', 'rate': 30}),(0, 0, {'name': '50% mi-chantier', 'rate': 50}),(0, 0, {'name': '20% réception facture', 'rate': 20})]
        defaults.update({'order_terms':vals})
        
        return defaults
        
    
   
class SaleOrderTerm(models.Model):
    _name = 'sale.order.terms'
    _description = 'Sales Order Terms'
    _order = 'sequence, id'
    
    @api.depends('rate', 'order_id.amount_total', 'order_id.primeCEE')
    def _compute_amount(self):
        for line in self:
            mtt_cde = line.order_id.amount_total - line.order_id.primeCEE
            price =  mtt_cde * ((line.rate or 0.0) / 100.0)            
            line.update({
                'price_total': price,                
            })
        
    order_id = fields.Many2one('sale.order', 'Sales Order Reference', ondelete='cascade', index=True)
    name = fields.Text(string='Echéances', required=True)
    rate = fields.Float('Taux', required=True,digits=dp.get_precision('Discount'))
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True, copy=True)
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of optional products.")
    
    def _check_total_term(self):
        total = 0.0
        for term in self:
            total += term.rate
            
        if total > 100:
                return False
        return True

    _constraints = [
        (_check_total_term,'Total des échéances > 100%', []),
    ]
    
class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        if self.description_sale:
            name = self.description_sale
        else:
            name = self.display_name

        return name
        
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    layout_category = fields.Char('Section')
        
class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"
    
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    
class SaleOrderTemplateLine(models.Model):
    _inherit = "sale.order.template.line"
    
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sale.order'))

