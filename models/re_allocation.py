from odoo import models, fields, api, _


class ReAllocationWizard(models.TransientModel):
    _name = 're_allocation.wizard'
    _description = 'Re Allocation'

    @api.onchange('assign_to')
    def _onchange_leads_users(self):
        users = self.env.ref('leads.leads_basic_user').users
        lead_users = []
        for j in users:
            print(j.name, 'j')
            lead_users.append(j.employee_id.id)
        domain = [('id', 'in', lead_users)]
        return {'domain': {'assign_to': domain}}
    assign_to = fields.Many2one('hr.employee', string='Assigned To', domain=_onchange_leads_users)

    def action_add_assigned_user(self):
        print(self._context['parent_obj'], 'parent_obj')
        # current_rec_id = self.env.context.get('active_id')
        # lead = self.env['leads.logic'].sudo().search([('id', '=', current_rec_id)])
        # lead.leads_assign = self.assign_to.id
        # print(current_rec_id, 'current_rec_id')
        leads = self.env['leads.logic'].sudo().search([('id', '=', self._context['parent_obj'])])
        for rec in leads:
            rec.sudo().write({
                'leads_assign': self.assign_to.id,
                'state': 're_allocated',
                'assigned_date': fields.Datetime.now()
            })

            rec.activity_schedule('leads.activity_lead_re_allocation', user_id=rec.leads_assign.user_id.id,
                                  note=f' You have been assigned new lead.')
