# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class IsoscopAccountMoveReport(models.Model):
    _name = "isoscop.move.report"
    _description = "Isoscop Move Analysis Report"
    _auto = False    
    
    date = fields.Date('Date', readonly=True)
    ventes = fields.Float('Ventes', readonly=True)
    achats = fields.Float('Achats', readonly=True)
    solde = fields.Float('Solde', readonly=True)
    company_id = fields.Many2one('res.company', string='Société', readonly=True)    
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            min(aml.id) as id,
            aml.company_id,
            date,
            SUM(CASE WHEN aa.code like '7%' then credit-debit else 0 end) as ventes,
            SUM(CASE WHEN aa.code like '6%' then debit-credit else 0 end) as achats,
            SUM(CASE WHEN aa.code like '7%' then credit-debit
                    WHEN aa.code like '6%' then -(debit-credit) else 0 end) as solde
        """

        for field in fields.values():
            select_ += field

        from_ = """
                account_move_line aml
                join account_account aa on (aml.account_id = aa.id)
                %s
        """ % from_clause

        groupby_ = """
            aml.company_id,
            date %s
        """ % (groupby)

        return """%s (SELECT %s FROM %s WHERE (aa.code like '7%%' or aa.code like '6%%') GROUP BY %s)""" % (with_, select_, from_, groupby_)
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))