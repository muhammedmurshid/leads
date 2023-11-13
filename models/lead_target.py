from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError


class LeadsTarget(models.Model):
    _name = 'leads.target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'year'
    _description = 'Target'

    year = fields.Integer(string='Year', required=True)
    added_date = fields.Date(string='Added Date', default=fields.Date.today())
    color = fields.Integer(string='Color Index', help="The color of the channel")

    def get_leads_users(self):
        leads_users = self.env.ref('leads.leads_basic_user').users.ids
        if leads_users:
            leads_users.append(self.env.user.id)
            return [('id', 'in', leads_users)]
        else:
            return [('id', 'in', [self.env.user.id])]

    user_id = fields.Many2one('res.users', string='Lead User', domain=get_leads_users)
    month_ids = fields.One2many('month.lists.leads.target', 'month_id', string='Month')

    @api.depends('month_ids.target')
    def _amount_target_all(self):
        """
        Compute the total amounts of the SO.
        """
        total = 0
        for order in self.month_ids:
            total += order.target
        self.update({
            'admission_target': total,
        })

    admission_target = fields.Integer(string='Admission Target', compute='_amount_target_all', store=True)

    @api.onchange('user_id')
    def onchange_month(self):
        targets = []
        field_info = self.month_ids.fields_get(['month'])
        keys = [key for key, _ in field_info['month']['selection']]
        unlink_commands = [(3, child.id) for child in self.month_ids]
        self.write({'month_ids': unlink_commands})
        for i in keys:
            print(i, 'i')
            res_list = {
                'month': i,
                'target': 0

            }
            targets.append((0, 0, res_list))
        self.month_ids = targets

    @api.constrains('year', 'user_id')
    def _check_name(self):
        partner_rec = self.env['leads.target'].search(
            [('year', '=', self.year), ('id', '!=', self.id), ('user_id', '=', self.user_id.id)])
        if partner_rec:
            raise UserError(_('Exists ! This User Have Already Added Target'))


class MonthListsLeadTarget(models.Model):
    _name = 'month.lists.leads.target'

    month = fields.Selection(
        [('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'),
         ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'),
         ('november', 'November'), ('december', 'December')], string="Month", required=True
    )
    target = fields.Integer(string='Target')
    month_id = fields.Many2one('leads.target', string='Month', ondelete='cascade')

    # @api.onchange('month')
    # def onchange_month(self):
    #     a = []
    #     field_info = self.fields_get(['month'])
    #     keys = [key for key, _ in field_info['month']['selection']]
    #     # a.append(selection_values.keys())
    #     print(keys, 'all')


