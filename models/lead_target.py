from odoo import fields, models, _, api


class LeadsTarget(models.Model):
    _name = 'leads.target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'year'
    _description = 'Target'

    year = fields.Integer(string='Year', required=True)
    added_date = fields.Date(string='Added Date', default=fields.Date.today())
    admission_target = fields.Integer(string='Admission Target')
    color = fields.Integer(string='Color Index', help="The color of the channel")
    month = fields.Selection(
        [('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'),
         ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'),
         ('november', 'November'), ('december', 'December')], string="Month", required=True)

    def get_leads_users(self):
        leads_users = self.env.ref('leads.leads_basic_user').users.ids
        if leads_users:
            leads_users.append(self.env.user.id)
            return [('id', 'in', leads_users)]
        else:
            return [('id', 'in', [self.env.user.id])]

    user_id = fields.Many2one('res.users', string='Lead User', domain=get_leads_users)
