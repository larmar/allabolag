# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import requests
import xml.etree.ElementTree as ET

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
        self._cr.execute("""CREATE UNIQUE INDEX ON res_partner(orgnr) WHERE orgnr IS NOT NULL;""")
        
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
        for partner in self:
            context = dict()

            key = False
            config_param = self.env['ir.config_parameter'].search([('key','=','allabolag.key.saldo')])
            if not config_param:
                raise ValidationError('System Parameter not found with Key "allabolag.key.saldo".\n\n Please make sure it exists with valid Session Key.')
            if config_param:
                if config_param[0].last_saldo < 3:
                    raise ValidationError('Invalid Last Saldo for System Parameter!\n\n%s'%(config_param[0].warning))

                key = config_param[0].value
                #update Last saldo - reducing it by 3
                config_param[0].sudo().write({'last_saldo': config_param[0].last_saldo - 3})
            
            orgnr = partner.orgnr or False
            state_id = partner.state_id and partner.state_id.name or False
            name = partner.name
            
            url = 'http://www.allabolag.se/ws/BIWS/service.php?key=%s&type=fetch'%(key)
            query = '&query=jurnamn:%s'%(name)

            if orgnr:
                query += '%%20AND%%20orgnr:%s'%(str(orgnr))

            #if state_id:
            #    query += '%%20AND%%20ba_postort:%s'%(str(state_id))

            results_range = '&recfrom=1&recto=99' #to limit results in response upto 99

            url = url + query + results_range

            result = requests.post(url)

            data = ET.fromstring(result.text)

            res = {}
            cnt = 0
            tag_head, message = False, ''
            koncernmoder_check = False 
            saldo = False 
            for elem in data.iter():
                if elem.tag == 'saldo':
                    saldo = elem.text
                if elem.tag == 'message':
                    message = elem.text
                if elem.tag == 'record':
                    cnt += 1
                    res['record'+str(cnt)] = {}
                    tag_head = 'record'+str(cnt)
                elif tag_head and elem.text:
                    #ignore data from inside koncernmoder tag
                    if elem.tag == 'koncernmoder':
                        koncernmoder_check = True
                    if elem.tag == 'mgmt':
                        koncernmoder_check = False

                    if koncernmoder_check is False:
                        res[tag_head][str(elem.tag)] = elem.text
            
            context['saldo'] = saldo
            context['params_id'] = config_param[0].id
            if message:
                message = 'Message: ' + str(message)

            if res and res.keys():
                contact_id = self.env['res.contact.allabolag'].create({})
                for record in res:
                    vals = {
                        'jurnamn': res[record].get('jurnamn', False),
                        'orgnr': res[record].get('orgnr', False),
                        'phone': res[record].get('riktnrtelnr', False),
                        'ba_adress': res[record].get('ba_gatuadress', False),
                        'ba_postnr': res[record].get('ba_postnr', False),
                        'ba_postort': res[record].get('ba_postort', False),
                        'ba_kommun': res[record].get('ba_kommun', False),
                        'ba_lan': res[record].get('ba_lan', False),

                        'ua_adress': res[record].get('ua_gatuadress', False),
                        'ua_postort': res[record].get('ua_postort', False),
                        'ua_kommun': res[record].get('ua_kommun', False),
                        'ua_lan': res[record].get('ua_lan', False),
                        'ua_postnr': res[record].get('ua_postnr', False),
                        'res_id': contact_id.id
                        }
                    self.env['res.contact.allabolag.line'].create(vals)
                return {
                    'name': 'Contact - Allabolag',
                    'type': 'ir.actions.act_window',
                    'res_model': 'res.contact.allabolag',
                    'res_id': int(contact_id.id),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': context,
                }
            else:
                raise ValidationError('Company Contact Details not found in Allabolag Directory.\n\n%s'%(message))
        return True