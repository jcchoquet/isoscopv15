# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class MoveLIne(models.Model):
    _inherit = 'account.move.line'
    
    @api.depends('debit', 'credit')
    def _store_balance_isoscop(self):
        for line in self:
            line.balance_isoscop = line.credit - line.debit
    
    balance_isoscop = fields.Float(compute='_store_balance_isoscop', store=True, currency_field='company_currency_id')
    
    def import_ecritures_achat(self):
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
        _logger.info("DEBUT IMPORT ECRITURE ACHAT")   
        
        ##Codejournal,journal,Date,Dateformat,compte,libcompte,Compteauxi,libcompteauxi,Piece,Datepiece,Document,Libelle,Debit,Credit,Montantseul,Montantsens,Sens,Statut,Datelettrage,Lettrage,Partiel,echeance,paiement,Notes,lignedoc,Documents
        ## 5724 lignes
        pieceprec = ''
        move_id = False
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE where codejournal in ('AC','AC2') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():
            if pieceprec != row['piece']:
                if move_id:
                    move_id.post()
                    
                partner = False
                #creation de la piece comptables
                values = {
                    'date': datetime.strptime(row['dateformat'],'%Y%m%d'),
                    'journal_id': self.env['account.journal'].search([('type','=','purchase')]).id,
                    'company_id': company_id,
                    'ref': row['piece']
                }
                move_id = self.env['account.move'].create(values)
                
            account_id = self.env['account.account'].search([('code','=',row['compte'])])
            if row['compte'][:3] == '401':
                partner = self.env['res.partner'].search([('supplier','=',True),('property_account_payable_id','=',account_id.id)])
            
            values_line = {
                'account_id': account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'date_maturity': datetime.strptime(row['dateformat'],'%Y%m%d'),
                'move_id': move_id.id,
                'internal_note': row['lettrage'],
            }
            # _logger.info("LINE %r",values_line)
            self.env['account.move.line'].with_context(check_move_validity=False).create(values_line)
            
            pieceprec = row['piece']
            
        if move_id:
            move_id.post()
            
        _logger.info("FIN IMPORT ECRITURE ACHAT")
        
    def import_ecritures_VEOD(self):
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
               
        _logger.info("DEBUT IMPORT ECRITURE VE_OD")   
        ## 3022 lignes
        pieceprec = ''
        move_id = False
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE where codejournal in ('OD','VE') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():
            if pieceprec != row['piece']:
                if move_id:
                    move_id.post()
                    
                partner = False
                #creation de la piece comptables
                values = {
                    'date': datetime.strptime(row['dateformat'],'%Y%m%d'),
                    'journal_id': self.env['account.journal'].search([('code','=',row['codejournal'])]).id,
                    'company_id': company_id,
                    'ref': row['piece']
                }
                move_id = self.env['account.move'].create(values)
                
            account_id = self.env['account.account'].search([('code','=',row['compte'])])
            if row['compte'][:3] == '401':
                partner = self.env['res.partner'].search([('supplier','=',True),('property_account_payable_id','=',account_id.id)])
            if row['compte'][:3] == '411':
                partner = self.env['res.partner'].search([('customer','=',True),('property_account_receivable_id','=',account_id.id)])
            
            values_line = {
                'account_id': account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'date_maturity': datetime.strptime(row['dateformat'],'%Y%m%d'),
                'move_id': move_id.id,
                'internal_note': row['lettrage'],
            }
            # _logger.info("LINE %r",values_line)
            self.env['account.move.line'].with_context(check_move_validity=False).create(values_line)
            
            pieceprec = row['piece']
        
        if move_id:
            move_id.post()      
        
        _logger.info("FIN IMPORT ECRITURE VE OD")
        
    def import_ecritures_banque(self):
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
        
        _logger.info("DEBUT IMPORT ECRITURE BANQUE")   
        ## 2580 lignes
        pieceprec = ''
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE where codejournal in ('CC','BP1','BT') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():
            journal = self.env['account.journal'].search([('code','=',row['codejournal'])])
        
            if journal.default_debit_account_id.code == row['compte']:
                continue
                
            partner = False
            #creation de la piece comptable
            values = {
                'date': datetime.strptime(row['dateformat'],'%Y%m%d'),
                'journal_id': journal.id,
                'company_id': company_id,
                'ref': row['piece']
            }
            move_id = self.env['account.move'].create(values)
            
            account_id = self.env['account.account'].search([('code','=',row['compte'])])
            if row['compte'][:3] == '401':
                partner = self.env['res.partner'].search([('supplier','=',True),('property_account_payable_id','=',account_id.id)])
            if row['compte'][:3] == '411':
                partner = self.env['res.partner'].search([('customer','=',True),('property_account_receivable_id','=',account_id.id)])
            
            values_line = {
                'account_id': account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'date_maturity': datetime.strptime(row['dateformat'],'%Y%m%d'),
                'move_id': move_id.id,
                'internal_note': row['lettrage'],
            }           
            move_line_id = self.with_context(check_move_validity=False).create(values_line)
            
            values_line = {
                'account_id': journal.default_debit_account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['credit']),
                'credit': float(row['debit']),
                'date_maturity': datetime.strptime(row['dateformat'],'%Y%m%d'),
                'move_id': move_id.id
            }           
            self.with_context(check_move_validity=False).create(values_line)
            move_id.post()
            
        _logger.info("FIN IMPORT ECRITURE BANQUE")
        
        
    def import_ecritures_anouveau(self):
        date_jour = datetime.now().strftime('%Y-%m-%d')
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
        ## 116 lignes
        _logger.info("DEBUT IMPORT ECRITURE A NOUVEAU")   
        
        pieceprec = ''
        total = 0.0
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE where codejournal in ('[AN]') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():
            partner = False            
            if pieceprec == '':
                journal = self.env['account.journal'].search([('code','=',row['codejournal'])])
                
                #creation de la piece comptable
                values = {
                    'date': datetime.strptime(row['dateformat'],'%Y%m%d'),
                    'journal_id': journal.id,
                    'company_id': company_id
                }
                move_id = self.env['account.move'].create(values)
            
            account_id = self.env['account.account'].search([('code','=',row['compte'])])
            if row['compte'][:3] == '401':
                partner = self.env['res.partner'].search([('supplier','=',True),('property_account_payable_id','=',account_id.id)])
            if row['compte'][:3] == '411':
                partner = self.env['res.partner'].search([('customer','=',True),('property_account_receivable_id','=',account_id.id)])
            
            
            name = row['libelle']
            name = name.replace("'","''")
            total += float(row['debit'])
            # values_line = {
                # 'account_id': account_id.id,
                # 'partner_id' : partner and partner.id or False,
                # 'name': row['libelle'],
                # 'debit': float(row['debit']),
                # 'credit': float(row['credit']),
                # 'date_maturity': datetime.strptime(row['dateformat'],'%Y%m%d'),
                # 'move_id': move_id.id
            # }           
            # self.env['account.move.line'].with_context(check_move_validity=False).create(values_line)
            if partner:
                sql_query = """insert into account_move_line(company_id,create_date,create_uid, account_id,partner_id,name,debit,credit,date_maturity,move_id,journal_id,date,ref,internal_note) 
                    values(%s,'%s',%s,%s,%s,'%s',%s,%s,'%s',%s, %s,'%s','%s','%s');""" % (company_id,date_jour,user_id,account_id.id,partner[0].id,name,float(row['debit']),float(row['credit']),datetime.strptime(row['dateformat'],'%Y%m%d'),move_id.id,journal.id,datetime.strptime(row['dateformat'],'%Y%m%d'),row['piece'],row['lettrage'])
            else:
                sql_query = """insert into account_move_line(company_id,create_date,create_uid, account_id,name,debit,credit,date_maturity,move_id,journal_id,date,ref,internal_note) 
                    values(%s,'%s',%s,%s,'%s',%s,%s,'%s',%s, %s,'%s','%s','%s');""" % (company_id,date_jour,user_id,account_id.id,name,float(row['debit']),float(row['credit']),datetime.strptime(row['dateformat'],'%Y%m%d'),move_id.id,journal.id,datetime.strptime(row['dateformat'],'%Y%m%d'),row['piece'],row['lettrage'])
            self.env.cr.execute(sql_query)
            
            pieceprec = row['piece']
        
        self.env.cr.commit()
            
        move_id.write({'amount':total})
        move_id.post()
            
        _logger.info("FIN IMPORT ECRITURE A NOUVEAU")
        
    
    def lettrage_paiement(self):    
        journal = self.env['account.journal'].search([('code','=','CC')])
    
        aml_ids = self.search([('journal_id','=',journal.id), ('internal_note','!=',''), ('reconciled','=', False)])
    
        for aml in aml_ids:            
            ## on effectue le lettrage si besoin
            debit_moves = credit_moves = False
            
            if aml.debit > 0:
                debit_moves = aml
                credit_moves = self.search([('account_id','=',aml.account_id.id),('internal_note','=',aml.internal_note),('credit','>',0), ('reconciled','=', False) ])
            else:
                credit_moves = aml
                debit_moves = self.search([('account_id','=',aml.account_id.id),('internal_note','=',aml.internal_note),('debit','>',0), ('reconciled','=', False) ])
                
            if debit_moves and credit_moves:
                _logger.info("DEBIT %r",debit_moves)
                _logger.info("CREDIT %r",credit_moves)
                res = self._reconcile_lines(debit_moves, credit_moves, 'amount_residual')
                aml.check_full_reconcile()
                if res:
                    _logger.info("LETTRAGE %r",res)