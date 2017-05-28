# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

def check_digits(number = False):
    if number:
        for res in str(number):
            if ord(res) not in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57):
                return False
    return True

class ResPartner(models.Model):
    _inherit = "res.partner"

    orgnr = fields.Char('Orgnr')

    @api.model_cr
    def init(self):
        """Create Unique constraint allowing Null Values on orgnr column
        """
        try:
            self._cr.execute("""CREATE UNIQUE INDEX  res_partner_orgnr_unique_idx ON res_partner(orgnr) WHERE orgnr IS NOT NULL;""")
        except Exception, e:
            _logger.debug("Unique Constraint Creation error: %s"%(e))
            pass

    @api.model
    def create(self, vals):
        """ Validate Orgnr :
        * Must be Unique & have exactly 10 digits.
        """
        if vals and isinstance(vals, dict):
            orgnr = vals.get('orgnr', False)
            if orgnr:
                if len(str(orgnr)) != 10:
                    raise ValidationError('Orgnr must be 10 digits number.\nYou entered {} digits: {}'.format(len(str(orgnr)), orgnr))

                if not check_digits(str(orgnr)):
                    raise ValidationError('Orgnr must be 10 digits number between 0-9.\nYou entered: {}'.format(orgnr))

                orgnr_search = self.search([('orgnr', '=', orgnr)])
                if orgnr_search:
                    raise ValidationError('Orgnr {} already exists for another company.\nCompany: {}'.format(orgnr, orgnr_search[0].name))
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        """ Validate Orgnr :
        * Must be Unique & have exactly 10 digits.
        """
        if vals and isinstance(vals, dict):
            orgnr = vals.get('orgnr', False)
            if orgnr: 
                if len(str(orgnr)) != 10:
                    raise ValidationError('Orgnr must be 10 digits number.\nYou entered {} digits: {}'.format(len(str(orgnr)), orgnr))

                if not check_digits(str(orgnr)):
                    raise ValidationError('Orgnr must be 10 digits number between 0-9.\nYou entered: {}'.format(orgnr))

                orgnr_search = self.search([('orgnr', '=', orgnr)])
                if orgnr_search and orgnr_search[0].id != self.id:
                    raise ValidationError('Orgnr {} already exists for another company.\nCompany: {}'.format(orgnr, orgnr_search[0].name))
        return super(ResPartner, self).write(vals)

    @api.onchange('orgnr')
    def onchange_orgnr(self):
        """ Validate Orgnr :
        * Must be Unique & have exactly 10 digits.
        """
        if self.orgnr:
            orgnr_search = self.search([('orgnr', '=', self.orgnr)])
            if orgnr_search:
                if self.id and isinstance(self.id, int) and self.id != orgnr_search[0].id:
                    raise ValidationError('Orgnr {} already exists for another company.\nCompany: {}'.format(self.orgnr, orgnr_search[0].name))
            if len(str(self.orgnr)) != 10:
                raise ValidationError('Orgnr must be 10 digits number.\nYou entered {} digits: {}'.format(len(str(self.orgnr)), self.orgnr))
            if not check_digits(str(self.orgnr)):
                raise ValidationError('Orgnr must be 10 digits number between 0-9.\nYou entered: {}'.format(self.orgnr))


    @api.multi
    def action_update_company_info_allabolag(self):

        return True