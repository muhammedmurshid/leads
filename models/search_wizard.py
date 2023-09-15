from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SearchLeadsWizard(models.TransientModel):
    _name = 'search.wizard.lead'
    _description = 'Search Lead'

    mobile = fields.Char('Mobile', placeholder="Search")

    def action_search(self):
        leads = self.env['leads.logic'].sudo().search(
            [('phone_number', '=', self.mobile)])
        leads_second = self.env['leads.logic'].sudo().search(
            [('phone_number_second', '=', self.mobile)])
        if leads:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'searched.leads.response',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_owner': 'Lead: ' + leads.name + ' already exists with ' + leads.leads_assign.name},

            }
        elif leads_second:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'searched.leads.response',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_owner': 'Lead: ' + leads_second.name + ' already exists with ' + leads_second.leads_assign.name},

            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'searched.leads.response',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_owner': 'This number does not exist in our records'},

            }


class SearchedLeadsResponse(models.TransientModel):
    _name = 'searched.leads.response'
    _description = 'Searched Leads Response'

    owner = fields.Char(readonly=True, string='Owner')
