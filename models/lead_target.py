from odoo import fields, models, _, api


class LeadsTarget(models.Model):
    _name = 'leads.target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'year'
    _description = 'Target'

    year = fields.Integer(string='Year', required=True)
    admission_target = fields.Integer(string='Admission Target')
    color = fields.Integer(string='Color Index', help="The color of the channel")

    def get_leads_users(self):
        leads_users = self.env.ref('leads.leads_basic_user').users.ids
        if leads_users:
            leads_users.append(self.env.user.id)
            return [('id', 'in', leads_users)]
        else:
            return [('id', 'in', [self.env.user.id])]

    user_id = fields.Many2one('res.users', string='Lead User', domain=get_leads_users)







