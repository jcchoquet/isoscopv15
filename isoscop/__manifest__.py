# -*- coding: utf-8 -*-
{
    'name': "isoscop",

    'summary': """
        Ajout prime CEE""",

    'description': """
        Personnalisation report
        Gestion échéancier
        Gestion prime CEE
    """,

    'author': "Oxilia-info",
    'website': "http://www.oxilia-info.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.2',
    "license": "LGPL-3",
    # any module necessary for this one to work correctly
    'depends': ['base','sale','account', 'sale_management'],

    # always loaded
    'data': [
        #data
        'data/ir_sequence_data.xml',
        #security
        'security/ir.model.access.csv',
        'security/security_rule.xml',
        'security/isoscop_security.xml',
        #views
        'views/sale_views.xml',
        'views/invoice_views.xml',
        'views/partner_views.xml',
        'views/product_template.xml',
        'views/ir_qweb_widget_templates.xml',       
        'wizard/res_config_settings_views.xml',
        #report
        'report/report_template.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [],
}
