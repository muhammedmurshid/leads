from odoo import models, fields, api


class MailInheritActivityLeads(models.Model):
    _inherit = 'mail.activity'

    assign_to = fields.Many2one('hr.employee', string='Assigned To')
    lead_id = fields.Many2one('leads.logic', string='Lead')
    user_id = fields.Many2one('res.users', string='User')

    @api.model
    def default_get(self, fields):
        res = super(MailInheritActivityLeads, self).default_get(fields)
        leads = self.env['leads.logic'].sudo().search([])
        if not fields or 'res_model_id' in fields and res.get('res_model'):
            res['res_model_id'] = self.env['ir.model']._get(res['res_model']).id
            for lead in leads:
                if lead.id == res.get('res_id'):
                    print(lead.leads_assign.name, 'assigned to')
                    if lead.leads_assign:
                        # self.user_id = lead.leads_assign.user_id.id
                        res['lead_id'] = lead.leads_assign.user_id.id
                        res['lead_id'] = lead.id
            # print(res.get('res_id'), 'id')
        return res

