# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Company - Allabolag',
  'version': '10.0.0.1',
  'category': 'API',
  'summary': 'Search & Update Company contacts',
  'description': """
##############################################################
                Allabolag - Company Contacts Link
##############################################################
  """,
  'author': 'Martin WIlderoth',
  'website': 'www.linserv.se/en/',
  'depends': ['base'],
  'application': False,
  'auto_install': False,
  'installable': True,
  'data': [ 
    'views/ir_config_view.xml',
  	'views/res_partner_view.xml',
    'wizard/res_contact_allabolag.xml',

    'data/ir_config.xml',
    'data/res.country.state.csv',

    'security/ir.model.access.csv',
	],
}
