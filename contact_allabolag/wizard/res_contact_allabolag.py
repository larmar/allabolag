# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResContactAllabolag(models.TransientModel):
    _name = "res.contact.allabolag"
    _description = "Wizard to show Allabolag Contact Results"

    contact_ids = fields.One2many('res.contact.allabolag.line', 'res_id', 'Contacts')

    @api.multi
    def action_update(self):
        contact_ids, contact_select = [], False
        for contact in self.contact_ids:
            if contact.contact_select is True:
                contact_select = True
                contact_ids.append(contact)
                
        if not contact_select:
            raise ValidationError('Please select Contact Line to update Company Details with.')
        if len(contact_ids) > 1:
            raise ValidationError('Please select only one Contact Line to update Company Detais with.\n\nYou have selected %s Contacts.'%(str(len(contact_ids))))
        
        #update Company record:
        partner_id = self.env.context['active_id']
        partner_ids = self.env['res.partner'].browse([partner_id])

        vals = {
            'name': contact_ids[0].jurnamn,
        }
        
        if contact_ids[0].orgnr: vals['orgnr'] = contact_ids[0].orgnr 
        if contact_ids[0].phone: vals['phone'] = contact_ids[0].phone
        if contact_ids[0].ba_adress: vals['street'] = contact_ids[0].ba_adress
        if contact_ids[0].ba_postort: vals['street2'] = contact_ids[0].ba_postort
        if contact_ids[0].ba_postnr: vals['zip'] = contact_ids[0].ba_postnr
        if contact_ids[0].ba_kommun: vals['city'] = contact_ids[0].ba_kommun

        lang_id = self.env['res.lang'].search([('iso_code','=','sv_SE')])
        if lang_id: vals['lang'] = 'sv_SE'
        
        country_id = self.env['res.country'].search([('code', '=', 'SE')])
        if country_id: vals['country_id'] = country_id.id

        if contact_ids[0].ba_lan:
            state_id = self.env['res.country.state'].search([('name','=',contact_ids[0].ba_lan)])
            if state_id: vals['state_id'] = state_id.id

        partner_ids.write(vals)

        #add/update invoice contact:
        vals = {}
        if contact_ids[0].ua_adress: vals['street'] = contact_ids[0].ua_adress
        if contact_ids[0].ua_postort: vals['city'] = contact_ids[0].ua_postort
        if contact_ids[0].ua_kommun: vals['street2'] = contact_ids[0].ua_kommun
        if contact_ids[0].ua_postnr: vals['zip'] = contact_ids[0].ua_postnr
        if contact_ids[0].ua_lan:
            state_id = self.env['res.country.state'].search([('name','=',contact_ids[0].ua_lan)])
            if state_id: vals['state_id'] = state_id.id
        
        if vals:
            invoice_ids = self.env['res.partner'].search([('parent_id','=',partner_ids.id), ('type','=','invoice')])
            if invoice_ids:
                invoice_ids[0].write(vals)
            else:
                vals['parent_id'] = partner_ids.id
                vals['type'] = 'invoice'
                invoice_ids = self.env['res.partner'].create(vals)
                
        return True

class ResContactAllabolagLine(models.TransientModel):
    _name = "res.contact.allabolag.line"

    res_id = fields.Many2one('res.contact.allabolag', 'Resource')
    jurnamn = fields.Char('Name')
    orgnr = fields.Char('Orgnr')
    phone = fields.Char('Phone')
    ba_adress = fields.Char('Street')
    ba_postnr = fields.Char('Zip')
    ba_postort = fields.Char('Street2')
    ba_kommun = fields.Char('City')
    ba_lan = fields.Char('State')
    
    #Contact - Invoice Address fields:
    ua_adress = fields.Char('Street')
    ua_postnr = fields.Char('Zip')
    ua_postort = fields.Char('City')
    ua_kommun = fields.Char('Street2')
    ua_lan = fields.Char('State')

    contact_select = fields.Boolean('Select')
