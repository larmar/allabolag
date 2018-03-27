# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields

class ConfigParams(models.Model):
    _inherit = "ir.config_parameter"

    last_saldo = fields.Integer('Last Saldo')
    saldo_request_date = fields.Datetime('Last Request')
    warning = fields.Text('Warning', translate=True)
    