# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)
 
class respartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def default_get(self, fields):
        res = super(respartner, self).default_get(fields)
        res['country_id'] = self.env['res.country'].search([('code', '=', 'FR')], limit=1).id        
        return res
    
    @api.model
    def create(self, vals):
        partner = super(respartner,self).create(vals)
        
        if partner.customer:
            client_code = ''
            if not partner.ref:
                # def du client_code                
                company = vals.get('company_id') or self.env.user.company_id.id
                client_code = self.env['ir.sequence'].with_context(force_company=company).next_by_code('res.partner.ref.sequence')
            else:
                client_code = partner.ref

            cpt = '411' + client_code           
            code_comptable_id = self.env['account.account'].search([('code','ilike',cpt)],order='code desc',limit=1)
            if not code_comptable_id:
                company = vals.get('company_id') or self.env.user.company_id.id
                vals_compte_comptable = {
                    'code': cpt,
                    'name': partner.name,
                    'user_type_id': self.env['account.account.type'].search([('type','=','receivable')],limit=1).id,
                    'reconcile': True,
                    'company_id': company,              
                }
                code_comptable_id = self.env['account.account'].sudo().create(vals_compte_comptable)
            partner.write({
                'ref': client_code.upper(),
                'property_account_receivable_id': code_comptable_id.id,
            })
        if partner.supplier:
            # def du client_code                
            client_code = '401' + partner.name.upper().replace(" ", "").replace("°", "").replace("'", "").replace(".", "").replace("-", "").replace("&", "")[:6]
                
            rech_account_code_ids = self.env['account.account'].search([('code','ilike',client_code)],order='code desc',limit=1)
            
            if rech_account_code_ids:
                last_client_code = rech_account_code_ids.code
                
                client_code = last_client_code[:9]
                if last_client_code[9:] and isinstance(last_client_code[9:], int):
                    i = int(last_client_code[9:]) + 1
                else:
                    i = 2
                
                client_code += str(i)
                
            code_comptable_id = self.env['account.account'].search([('code','ilike',client_code)],order='code desc',limit=1)
            if not code_comptable_id:
                company = vals.get('company_id') or self.env.user.company_id.id
                vals_compte_comptable = {
                    'code': client_code,
                    'name': partner.name,
                    'user_type_id': self.env['account.account.type'].search([('type','=','payable')],limit=1).id,
                    'reconcile': True,
                    'company_id': company,              
                }
                code_comptable_id = self.env['account.account'].sudo().create(vals_compte_comptable)
            partner.write({
                'property_account_payable_id': code_comptable_id.id,
            })
                    
        
        return partner
        
    def import_customer(self):
        tiret = "-";
        space = " ";
        
        def xstr(s):
            if s is None:
                return ''
            return str(s)
        
        _logger.info("DEBUT IMPORT CUSTOMER")   
        
        # création des clients
        self.env.cr.execute("""select * from IMPORT_CLIENT where entreprise = 'O';""")
        for row in self.env.cr.dictfetchall():            
            _logger.info("LINE %r",row)
            # fiche principale            
            phone = xstr(row['phone'])
            if phone != '' and phone[:2] != '33' and phone[:1] != '0':
                phone = '0'+phone
                
            mobile = xstr(row['mobile'])
            if mobile != '' and mobile[:2] != '33' and mobile[:1] != '0':
                mobile = '0'+mobile
                
            dico_partner = {
                'name' : row['nom_client'].upper(),
                'ref' : row['compte_client_compta'],
                'is_company' : True,
                'street' : row['adresse_1'],
                'street2' : row['adresse_2'],
                'city' : row['ville'],
                'zip' : row['cpostal'],
                'country_id' : self.env['res.country'].search([('code','=',row['pays'])]) and self.env['res.country'].search([('code','=',row['pays'])]).id or False,
                'phone' : phone,
                'mobile' : mobile,
                'email' : row['email'],
                'vat' : row['tva'],                
            }
            partner_id = self.env['res.partner'].create(dico_partner)
            
        # fin création des clients        
        _logger.info("FIN IMPORT CUSTOMER")        
        
        return True
        
    def import_contact(self):
        tiret = "-";
        space = " ";
        
        def xstr(s):
            if s is None:
                return ''
            return str(s)
        
        _logger.info("DEBUT IMPORT CONTACT")   
        
        # création des clients
        self.env.cr.execute("""select * from IMPORT_CLIENT where contact = 'O' and compte_client_compta != '';""")
        for row in self.env.cr.dictfetchall():
            _logger.info("LINE %r",row)
            # fiche principale
            partner_id = self.search([('ref','=',row['compte_client_compta'])],limit=1)
                       
            partner_adr_id = self.search([('parent_id','=',partner_id.id),('name','=',row['nom_client'])])
            
            # création adresse si inexistante
            if not partner_adr_id:
                phone = xstr(row['phone'])
                if phone != '' and phone[:2] != '33' and phone[:1] != '0':
                    phone = '0'+phone
                    
                mobile = xstr(row['mobile'])
                if mobile != '' and mobile[:2] != '33' and mobile[:1] != '0':
                    mobile = '0'+mobile
                
                dico_partner = {
                'name' : row['nom_client'].upper(),
                'parent_id' : partner_id.id,
                'type' : 'contact',                
                'street' : row['adresse_1'],
                'street2' : row['adresse_2'],
                'city' : row['ville'],
                'zip' : row['cpostal'],
                'country_id' : self.env['res.country'].search([('code','=',row['pays'])]) and self.env['res.country'].search([('code','=',row['pays'])]).id or False,
                'phone' : phone,
                'mobile' : mobile,
                'email' : row['email'],
                }
                self.env['res.partner'].create(dico_partner)
        
        # fin création des clients        
        _logger.info("FIN IMPORT CONTACT")        
        
        return True