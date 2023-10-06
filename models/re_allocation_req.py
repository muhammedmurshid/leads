from odoo import fields, models, api, _


class ReAllocationRequestManager(models.Model):
    _name = 're_allocation.request.leads'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Re Allocation Request'

    leads_source = fields.Many2one('leads.sources', string='Leads Source', required=True)
    name = fields.Char(string='Lead Name', required=True)
    email_address = fields.Char(string='Email Address')
    phone_number = fields.Char(string='Mobile Number', required=True, copy=False)
    probability = fields.Float(string='Probability')
    admission_status = fields.Boolean(string='Admission')
    date_of_adding = fields.Date(string='Date of Adding', default=fields.Date.today())
    last_update_date = fields.Datetime(string='Last Updated Date', )
    base_course_id = fields.Many2one('logic.base.courses', string='Course')
    reference_no = fields.Char(string='Sequence Number', required=True,
                               readonly=True, default=lambda self: _('New'))
    lead_quality = fields.Selection(
        [('Interested', 'Interested'), ('bad_lead', 'Bad Lead'), ('not_interested', 'Not Interested'),
         ('not_responding', 'Not Responding'), ('under_follow_up', 'Under Follow-up'),
         ('slightly_positive', 'Slightly Positive'), ('already_took_admission', 'Already Took Admission')],
        string='Lead Quality', required=True)
    place = fields.Char('Place')
    leads_assign = fields.Many2one('hr.employee', string='Assign to', default=lambda self: self.env.user.employee_id)
    lead_owner = fields.Many2one('hr.employee', string='Lead Owner')
    seminar_lead_id = fields.Integer()
    phone_number_second = fields.Char(string='Phone Number', unique=False)
    sample = fields.Char(string='Sample', compute='get_phone_number_for_whatsapp', store=True)
    field_to_display = fields.Char(string='Field to Display')
    lead_channel = fields.Char(string='Lead Channel')
    last_studied_course = fields.Char(string='Last Studied Course')
    college_name = fields.Char(string='College/School')
    referred_by = fields.Selection([('staff', 'Staff'), ('student', 'Student'), ('other', 'Other')],
                                   string='Referred By')
    referred_by_id = fields.Many2one('hr.employee', string='Referred Person')
    referred_by_name = fields.Char(string='Referred Person')
    referred_by_number = fields.Char(string='Referred Person Number')
    batch_preference = fields.Char(string='Batch Preference')
    branch_id = fields.Many2one('logic.branches', string='Branch')

    lead_qualification = fields.Selection(
        [('plus_one_science', 'Plus One Science'), ('plus_two_science', 'Plus Two Science'),
         ('plus_two_commerce', 'Plus Two Commerce'), ('plus_one_commerce', 'Plus One Commerce'),
         ('commerce_degree', 'Commerce Degree'),
         ('other_degree', 'Other Degree'), ('working_professional', 'Working Professional')],
        string='Lead qualification')
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other')],

                                string='District', required=True)
    remarks = fields.Char(string='Remarks')
    parent_number = fields.Char('Parent Number')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancelled')], string='State',
                             default='draft', tracking=True)
    duplicate_record_id = fields.Integer()

    def action_done(self):
        duplicates = self.env['duplicate.record.seminar'].sudo().search([('id', '=', self.duplicate_record_id)])
        print(duplicates.student_name, 'duplicates')
        if duplicates:
            duplicates.selected_lead = True
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def get_duplicate_records(self):
        duplicates = self.env['leads.logic'].sudo().search([])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Leads',
            'view_mode': 'tree,form',
            'res_model': 'leads.logic',
            'domain': [('phone_number', '=', self.phone_number)],
            'context': "{'create': False}"
        }

    def compute_count(self):
        for record in self:
            record.form_count = self.env['leads.logic'].search_count(
                [('phone_number', '=', self.phone_number)])

    form_count = fields.Integer(compute='compute_count')
