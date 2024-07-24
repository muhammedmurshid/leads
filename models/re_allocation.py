from odoo import models, fields, api, _
from datetime import timedelta


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
        today = fields.Date.today()
        after_four_days = today + timedelta(days=4)
        print(after_four_days, 'after_four_days')
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
                'assigned_date': fields.Datetime.now(),
                'over_due': False
            })

            rec.activity_schedule('leads.activity_lead_re_allocation', user_id=rec.leads_assign.user_id.id,
                                  date_deadline=after_four_days,
                                  note=f' You have been assigned new lead.')


class AllocationTeleCallersWizard(models.TransientModel):
    _name = 'allocation.tele_callers.wizard'
    _description = 'Allocation'

    @api.onchange('assign_to')
    def _onchange_leads_users(self):
        users = self.env.ref('leads.lead_tele_callers').users
        lead_users = []
        for j in users:
            print(j.name, 'j')
            lead_users.append(j.id)
        domain = [('id', 'in', lead_users)]
        return {'domain': {'assign_to': domain}}

    assign_to = fields.Many2one('res.users', string='Assigned To', domain=_onchange_leads_users)

    def action_add_assigned_user(self):
        print(self._context['parent_obj'], 'parent_obj')
        # current_rec_id = self.env.context.get('active_id')
        # lead = self.env['leads.logic'].sudo().search([('id', '=', current_rec_id)])
        # lead.leads_assign = self.assign_to.id
        # print(current_rec_id, 'current_rec_id')
        leads = self.env['leads.logic'].sudo().search([('id', '=', self._context['parent_obj'])])
        for rec in leads:
            rec.sudo().write({
                'tele_caller_ids': self.assign_to.id,
                'state': 'tele_caller',
                'lead_quality': 'nil',
                'leads_assign': False,
                'assigned_date': fields.Datetime.now(),
                'over_due': False
            })

            rec.activity_schedule('leads.mail_seminar_leads_done', user_id=rec.tele_caller_ids.id,
                                  note=f' You have been assigned new lead.')

    def action_add_tele_callers_user(self):
        print(self._context['parent_obj'], 'parent_obj')
        # current_rec_id = self.env.context.get('active_id')
        # lead = self.env['leads.logic'].sudo().search([('id', '=', current_rec_id)])
        # lead.leads_assign = self.assign_to.id
        # print(current_rec_id, 'current_rec_id')
        leads = self.env['leads.logic'].sudo().search([('id', '=', self._context['parent_obj'])])
        for rec in leads:
            rec.sudo().write({
                'tele_caller_ids': self.assign_to.id,
                'state': 'tele_caller',
                # 'lead_quality': 'nil',
                'leads_assign': False,
                # 'assigned_date': fields.Datetime.now(),
                # 'over_due': False
            })
