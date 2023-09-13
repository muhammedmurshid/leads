from odoo import models, fields, api


class MailInheritActivityLeads(models.Model):
    _inherit = 'mail.activity'

    assign_to = fields.Many2one('hr.employee', string='Assigned To')
    lead_id = fields.Many2one('leads.logic', string='Lead')

    def _compute_display_name(self):
        for activity in self:
            activity.display_name = activity.activity_type_id.name + ' : ' + activity.res_name

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

                        res.update({'lead_id': lead.id,
                                    'user_id': lead.leads_assign.id})
                        # self.user_id = lead.leads_assign.user_id.id
                        # res['lead_id'] = lead.leads_assign.user_id.id
                        # res['lead_id'] = lead.id

                    #     return lead.leads_assign.user_id.id
                    # else:
                    #     return self.env.user.id

        return res

    # user_id = fields.Many2one(
    #     'res.users', 'Assigned to',
    #     default=default_get,
    #     index=True, required=True)

