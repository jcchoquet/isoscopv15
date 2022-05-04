# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class MoveLIne(models.Model):
    _inherit = 'account.move.line'
    
  
    def import_ecritures_achat_isrc(self):
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
        _logger.info("DEBUT IMPORT ECRITURE ACHAT")   
        
        ## 1427 lignes
        pieceprec = ''
        move_id = False
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE_ISRC where journal in ('ACH') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():
            if pieceprec != row['piece']:
                if move_id:
                    move_id.post()
                    
                partner = False
                #creation de la piece comptables
                values = {
                    'date': datetime.strptime(row['date'],'%d/%m/%Y'),
                    'journal_id': self.env['account.journal'].search([('company_id', '=', company_id),('type','=','purchase')]).id,
                    'company_id': company_id,
                    'ref': row['piece']
                }
                move_id = self.env['account.move'].create(values)
                
            account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compte'])])
            if row['compte'][:3] == '401':
                if row['compteauxi'] and row['compteauxi'] != '':
                    account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compteauxi'])])
                    if not account_id and row['compte'][:3] == '401':
                        vals_compte_comptable = {
                            'code': row['compteauxi'],
                            'name': row['compteauxi'],
                            'user_type_id': self.env['account.account.type'].search([('type','=','payable')],limit=1).id,
                            'reconcile': True,
                            'company_id': company_id,              
                        }
                        account_id = self.env['account.account'].create(vals_compte_comptable)
                
                partner = self.env['res.partner'].search([('supplier','=',True),('property_account_payable_id','=',account_id.id)])
            
            values_line = {
                'account_id': account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'date_maturity': datetime.strptime(row['date'],'%d/%m/%Y'),
                'move_id': move_id.id,                
            }
            # _logger.info("LINE %r",values_line)
            self.env['account.move.line'].with_context(check_move_validity=False).create(values_line)
            
            pieceprec = row['piece']
            
        if move_id:
            move_id.post()
            
        _logger.info("FIN IMPORT ECRITURE ACHAT")
        
    def import_ecritures_VE(self):
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
               
        _logger.info("DEBUT IMPORT ECRITURE VE")   
        ## 3022 lignes
        pieceprec = ''
        move_id = False
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE_ISRC where journal in ('VEN') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():
            if pieceprec != row['piece']:
                if move_id:
                    move_id.post()
                    
                partner = False
                #creation de la piece comptables
                values = {
                    'date': datetime.strptime(row['date'],'%d/%m/%Y'),
                    'journal_id': self.env['account.journal'].search([('company_id', '=', company_id),('code','=','VE')]).id,
                    'company_id': company_id,
                    'ref': row['piece'],
                    'name': row['piece'],
                }
                move_id = self.env['account.move'].create(values)
                
            account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compte'])])
            if not account_id and row['compte'][:1] == '7':
                vals_compte_comptable = {
                    'code': row['compte'],
                    'name': row['compte'],
                    'user_type_id': 14,
                    'reconcile': False,
                    'company_id': company_id,              
                }
                account_id = self.env['account.account'].create(vals_compte_comptable)
            
            if row['compteauxi'] and row['compteauxi'] != '':
                account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compteauxi'])])
                if not account_id and row['compte'][:3] == '411':
                    vals_compte_comptable = {
                        'code': row['compteauxi'],
                        'name': row['compteauxi'],
                        'user_type_id': self.env['account.account.type'].search([('type','=','receivable')],limit=1).id,
                        'reconcile': True,
                        'company_id': company_id,              
                    }
                    account_id = self.env['account.account'].create(vals_compte_comptable)
            
            
            if row['compte'][:3] == '411':
                partner = self.env['res.partner'].search([('company_id', '=', company_id),('customer','=',True),('property_account_receivable_id','=',account_id.id)])
            
            values_line = {
                'account_id': account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'date_maturity': datetime.strptime(row['date'],'%d/%m/%Y'),
                'move_id': move_id.id,
            }
            # _logger.info("LINE %r",values_line)
            self.env['account.move.line'].with_context(check_move_validity=False).create(values_line)
            
            pieceprec = row['piece']
        
        if move_id:
            move_id.post()      
        
        _logger.info("FIN IMPORT ECRITURE VE")
        
    def import_ecritures_OD(self):
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
               
        _logger.info("DEBUT IMPORT ECRITURE OD")   
        ## 3022 lignes
        pieceprec = ''
        move_id = False
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE_ISRC where journal in ('OD','ODI') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():
            if pieceprec != row['piece']:
                if move_id:
                    move_id.post()
                    
                partner = False
                #creation de la piece comptables
                values = {
                    'date': datetime.strptime(row['date'],'%d/%m/%Y'),
                    'journal_id': self.env['account.journal'].search([('company_id', '=', company_id),('code','=','OD')]).id,
                    'company_id': company_id,
                    'ref': row['piece']
                }
                move_id = self.env['account.move'].create(values)
                
            account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compte'])])
            if not account_id and (row['compte'][:1] == '7' or row['compte'][:3] == '445'):
                vals_compte_comptable = {
                    'code': row['compte'],
                    'name': row['compte'],
                    'user_type_id': 14,
                    'reconcile': False,
                    'company_id': company_id,              
                }
                account_id = self.env['account.account'].create(vals_compte_comptable)
            
            
            if row['compteauxi'] and row['compteauxi'] != '':
                account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compteauxi'])])
                if not account_id and row['compte'][:3] == '411':
                    vals_compte_comptable = {
                        'code': row['compteauxi'],
                        'name': row['compteauxi'],
                        'user_type_id': self.env['account.account.type'].search([('type','=','receivable')],limit=1).id,
                        'reconcile': True,
                        'company_id': company_id,              
                    }
                    account_id = self.env['account.account'].create(vals_compte_comptable)
                if not account_id and row['compte'][:3] == '401':
                    vals_compte_comptable = {
                        'code': row['compteauxi'],
                        'name': row['compteauxi'],
                        'user_type_id': self.env['account.account.type'].search([('type','=','payable')],limit=1).id,
                        'reconcile': True,
                        'company_id': company_id,              
                    }
                    account_id = self.env['account.account'].create(vals_compte_comptable)
            
            
            if row['compte'][:3] == '411':
                partner = self.env['res.partner'].search([('company_id', '=', company_id),('customer','=',True),('property_account_receivable_id','=',account_id.id)])
            if row['compte'][:3] == '401':
                partner = self.env['res.partner'].search([('company_id', '=', company_id),('customer','=',True),('property_account_payable_id','=',account_id.id)])
            
            values_line = {
                'account_id': account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'date_maturity': datetime.strptime(row['date'],'%d/%m/%Y'),
                'move_id': move_id.id,
            }
            # _logger.info("LINE %r",values_line)
            self.env['account.move.line'].with_context(check_move_validity=False).create(values_line)
            
            pieceprec = row['piece']
        
        if move_id:
            move_id.post()      
        
        _logger.info("FIN IMPORT ECRITURE OD")
        
    def import_ecritures_banque(self):
        company_id = self.env.user.company_id.id
        user_id = self.env.user.id
        
        _logger.info("DEBUT IMPORT ECRITURE BANQUE")   
        ## 2580 lignes
        pieceprec = ''
        move_id = False
        # création des pieces comptables
        self.env.cr.execute("""select * from IMPORT_ECRITURE_ISRC where journal in ('CM','BP') order by journal,piece;""")
        for row in self.env.cr.dictfetchall():          
            if not row['piece']:
                continue
            if pieceprec != row['piece']:
                if move_id:
                    move_id.post()
                    
                partner = False
                #creation de la piece comptables
                codejournal = row['journal'] == 'BP' and row['journal'] or 'BNK1'
                journal = self.env['account.journal'].search([('company_id', '=', company_id),('code','=',codejournal)])
                
                values = {
                    'date': datetime.strptime(row['date'],'%d/%m/%Y'),
                    'journal_id': journal.id,
                    'company_id': company_id,
                    'ref': row['piece']
                }
                move_id = self.env['account.move'].create(values)
                
            account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compte'])])
            if not account_id and row['compte'][:3] != '411' and row['compte'][:3] != '401':
                vals_compte_comptable = {
                    'code': row['compte'],
                    'name': row['compte'],
                    'user_type_id': 14,
                    'reconcile': False,
                    'company_id': company_id,              
                }
                account_id = self.env['account.account'].create(vals_compte_comptable)
            
            
            if row['compteauxi'] and row['compteauxi'] != '':
                account_id = self.env['account.account'].search([('company_id', '=', company_id),('code','=',row['compteauxi'])])
                if not account_id and row['compte'][:3] == '411':
                    vals_compte_comptable = {
                        'code': row['compteauxi'],
                        'name': row['compteauxi'],
                        'user_type_id': self.env['account.account.type'].search([('type','=','receivable')],limit=1).id,
                        'reconcile': True,
                        'company_id': company_id,              
                    }
                    account_id = self.env['account.account'].create(vals_compte_comptable)
                if not account_id and row['compte'][:3] == '401':
                    vals_compte_comptable = {
                        'code': row['compteauxi'],
                        'name': row['compteauxi'],
                        'user_type_id': self.env['account.account.type'].search([('type','=','payable')],limit=1).id,
                        'reconcile': True,
                        'company_id': company_id,              
                    }
                    account_id = self.env['account.account'].create(vals_compte_comptable)
            
            
            if row['compte'][:3] == '411':
                partner = self.env['res.partner'].search([('company_id', '=', company_id),('customer','=',True),('property_account_receivable_id','=',account_id.id)])
            if row['compte'][:3] == '401':
                partner = self.env['res.partner'].search([('company_id', '=', company_id),('customer','=',True),('property_account_payable_id','=',account_id.id)])
            
            values_line = {
                'account_id': account_id.id,
                'partner_id' : partner and partner.id or False,
                'name': row['libelle'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'date_maturity': datetime.strptime(row['date'],'%d/%m/%Y'),
                'move_id': move_id.id,
            }
            _logger.info("LINE %r",values_line)
            self.env['account.move.line'].with_context(check_move_validity=False).create(values_line)
            
            pieceprec = row['piece']
        
        if move_id:
            move_id.post()
            
        _logger.info("FIN IMPORT ECRITURE BANQUE")
        