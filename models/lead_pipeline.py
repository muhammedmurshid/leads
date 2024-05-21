from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class LogicPipeline(models.Model):
    _name = 'logic.leads.pipeline'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Leads'
    _rec_name = 'name'
    _order = 'id desc'

    lead_source_id = fields.Many2one('leads.sources', string='Leads Source', required=True)
    name = fields.Char(string='Lead Name', required=True)
    email_address = fields.Char(string='Email Address', widget='mail')
    phone_number = fields.Char(string='Mobile Number', required=True)
    probability = fields.Float(string='Probability')
    date_of_adding = fields.Date(string='Date of Adding', default=fields.Datetime.now)
    last_update_date = fields.Datetime(string='Last Updated Date')
    reference_no = fields.Char(string='Sequence Number', required=True,
                               readonly=True, default=lambda self: _('New'))
    admission_date = fields.Date(string='Admission Date')
    lead_quality = fields.Selection(
        [('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold'),
         ('bad_lead', 'Bad Lead'),
         ('nil', 'Nil')],
        string='Lead Quality', required=True)
    lead_status = fields.Selection(
        [('not_responding', 'Not Responding'),
         ('already_enrolled', 'Already Enrolled'), ('joined_in_another_institute', 'Joined in another institute'),
         ('nil', 'Nil')],
        string='Lead Status',
    )
    remarks_id = fields.Many2one('lead.status', string='Lead Status')
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other'), ('nil', 'Nil')],
                                string='District', required=True)
    phone_number_second = fields.Char(string='Phone Number')
    course_type = fields.Selection(
        [('indian', 'Indian'), ('international', 'International'), ('crash', 'Crash'), ('repeaters', 'Repeaters'),
         ('nil', 'Nil')],
        string='Course Type')
    college_name = fields.Char(string='College/School')
    course_level = fields.Many2one('course.levels', string='Course Level',
                                   domain="[('course_id', '=', course_id)]")
    course_group = fields.Many2one('course.groups', string='Course Group/Part',
                                   domain="[('level_ids', 'in', course_level)]")
    course_papers = fields.Many2many('course.papers', string='Course Papers',
                                     domain="[('group_ids', 'in', course_group)]")
    lead_qualification = fields.Selection(
        [('plus_one_science', 'Plus One Science'), ('plus_two_science', 'Plus Two Science'),
         ('plus_two_commerce', 'Plus Two Commerce'), ('plus_one_commerce', 'Plus One Commerce'),
         ('commerce_degree', 'Commerce Degree'),
         ('other_degree', 'Other Degree'), ('working_professional', 'Working Professional')],
        string='Lead qualification')
    state = fields.Selection(
        [('draft', 'Draft'), ('assigned', 'Assigned'), ('re_allocated', 'Re Assigned'), ('done', 'Done'),
         ('cancel', 'Cancelled')],
        string='State',
        default='draft', tracking=True)
    last_studied_course = fields.Char(string='Last Studied Course')
    incoming_source = fields.Selection(
        [('social_media', 'Social Media'), ('google', 'Google'), ('hoardings', 'Hoardings'), ('tv_ads', 'TV Ads'),
         ('through friends', 'Through Friends'), ('whatsapp', 'WhatsApp'), ('other', 'Other')],
        string='How did you hear about us?')
    incoming_source_checking = fields.Boolean(string='Incoming Source Checking', )
    referred_by = fields.Selection([('staff', 'Staff'), ('student', 'Student'), ('other', 'Other')],
                                   string='Referred By')
    course_id = fields.Many2one('logic.base.courses', string='Preferred Course', required=True,
                                domain=[('state', '=', 'done')])
    branch = fields.Many2one('logic.base.branches', string='Branch', required=1)
    academic_year = fields.Selection(
        [('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'),
         ('2026', '2026'), ('nil', 'Nil')], string='Academic Year', required=True)
    preferred_batch_id = fields.Many2one('logic.base.batch', string='Preferred Batch')
    country = fields.Selection(
        [('india', 'India'), ('germany', 'Germany'), ('canada', 'Canada'), ('usa', 'USA'), ('australia', 'Australia'),
         ('italy', 'Italy'), ('france', 'France'), ('united_kingdom', 'United Kingdom'),
         ('saudi_arabia', 'Saudi Arabia'), ('ukraine', 'Ukraine'), ('united_arab_emirates', 'United Arab Emirates'),
         ('china', 'China'), ('japan', 'Japan'), ('singapore', 'Singapore'), ('indonesia', 'Indonesia'),
         ('russia', 'Russia'), ('oman', 'Oman'), ('nepal', 'Nepal'), ('japan', 'Japan')],
        string='Country', default='india')
    place = fields.Char(string='Place')
    mode_of_study = fields.Selection([('online', 'Online'), ('offline', 'Offline'), ('nil', 'Nil')],
                                     string='Mode of Study',
                                     required=True)
    platform = fields.Selection(
        [('facebook', 'Facebook'), ('instagram', 'Instagram'), ('website', 'Website'), ('just_dial', 'Just Dial'),
         ('other', 'Other')],
        string='Platform')
    lead_owner = fields.Many2one('hr.employee', string='Lead Owner', default=lambda self: self.env.user.employee_id)
    leads_assign = fields.Many2one('hr.employee', string='Assign to', default=lambda self: self.env.user.employee_id)
    assigned_date = fields.Date(string='Assigned Date', readonly=1)
    campaign_name = fields.Char(string='Campaign Name')

    @api.depends('lead_source_id')
    def get_leads_source_name(self):
        for record in self:
            record.lead_source_name = record.lead_source_id.name

    lead_source_name = fields.Char(string='Lead Source Name', compute='get_leads_source_name', store=True)


    @api.model
    def create(self, vals):
        number = vals.get('phone_number')
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'logic.leads.pipeline') or _('New')
        reversed_number = number[-10:]
        print(reversed_number, 'reversed_number')
        reverse_checking = self.search([('phone_number', 'like', f'%{reversed_number}')], limit=1)

        if reverse_checking:
            # Update the existing record with new values
            reverse_checking.write(vals)

            duplicate = self.env['logic.leads.duplicates'].create({'name': vals.get('name'),
                                                                   'phone_number': vals.get('phone_number'),
                                                                   'lead_source_id': vals.get('lead_source_id'),
                                                                   'email_address': vals.get('email_address'),
                                                                   'country': vals.get('country'),
                                                                   'district': vals.get('district'),
                                                                   'place': vals.get('place'),
                                                                   'mode_of_study': vals.get('mode_of_study'),
                                                                   'platform': vals.get('platform'),
                                                                   'lead_qualification': vals.get('lead_qualification'),
                                                                   'last_studied_course': vals.get(
                                                                       'last_studied_course'),
                                                                   # 'remark_id': vals.get('remark_id'),
                                                                   'college_name': vals.get('college_name'),
                                                                   'branch': vals.get('branch'),
                                                                   'course_type': vals.get('course_type'),
                                                                   'academic_year': vals.get('academic_year'),
                                                                   'course_id': vals.get('course_id'),
                                                                   'course_level': vals.get('course_level'),
                                                                   'course_group': vals.get('course_group'),
                                                                   'course_papers': vals.get('course_papers'),
                                                                   'preferred_batch_id': vals.get(
                                                                       'preferred_batch_id'),
                                                                   'lead_status': vals.get('lead_status'),
                                                                   'lead_quality': vals.get('lead_quality'),
                                                                   'probability': vals.get('probability'),
                                                                   'lead_owner': vals.get('lead_owner'),
                                                                   'leads_assign': vals.get('leads_assign'),
                                                                   'assigned_date': vals.get('assigned_date'),
                                                                   'date_of_adding': vals.get('date_of_adding'),
                                                                   'last_update_date': vals.get('last_update_date'),
                                                                   'admission_date': vals.get('admission_date'), })
            return reverse_checking
        else:
            return super(LogicPipeline, self).create(vals)

    def compute_count(self):
        for record in self:
            record.admission_count = self.env['admission.fee.collection'].search_count(
                [('lead_id', '=', record.id)])

    admission_count = fields.Integer(compute='compute_count')

    def get_admission_profile(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Admission',
            'view_mode': 'tree,form',
            'res_model': 'admission.fee.collection',
            'domain': [('lead_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_student_profile(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'view_mode': 'tree,form',
            'res_model': 'logic.students',
            'domain': [('id', '=', self.student_id.id)],
            'context': "{'create': False}"
        }

    def compute_student_count(self):
        for record in self:
            record.student_count = self.env['logic.students'].search_count(
                [('id', '=', self.student_id.id)])

    student_count = fields.Integer(compute='compute_student_count')
    student_id = fields.Many2one('logic.students', string='Student Id')

    def get_duplicate_leads(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'view_mode': 'tree,form',
            'res_model': 'logic.leads.duplicates',
            'domain': [('phone_number', '=', self.phone_number)],
            'context': "{'create': False}"
        }

    def compute_duplicates_leads_count(self):
        for record in self:
            record.duplicates_count = self.env['logic.leads.duplicates'].search_count(
                [('phone_number', '=', self.phone_number)])

    duplicates_count = fields.Integer(compute='compute_duplicates_leads_count')

    @api.constrains('phone_number')
    def _check_name(self):
        for record in self:
            if ' ' in record.phone_number:
                record.phone_number = record.phone_number.replace(' ', '')

    country_code = fields.Char('Country Code', compute='get_country_code', )

    @api.onchange('country')
    def get_country_code(self):
        if self.country == 'india':
            self.phone_number = '+91'
            self.country_code = '+91'
            self.phone_number_second = '+91'
        if self.country == 'germany':
            self.phone_number = '+49'
            self.phone_number_second = '+49'
        if self.country == 'canada':
            self.phone_number = '+1'
            self.phone_number_second = '+1'
        if self.country == 'usa':
            self.phone_number = '+1'
            self.phone_number_second = '+1'
        if self.country == 'australia':
            self.phone_number = '+61'
            self.phone_number_second = '+61'
        if self.country == 'italy':
            self.phone_number = '+39'
            self.phone_number_second = '+39'
        if self.country == 'france':
            self.phone_number = '+33'
        if self.country == 'united_kingdom':
            self.phone_number = '+44'
        if self.country == 'saudi_arabia':
            self.phone_number = '+966'
        if self.country == 'ukraine':
            self.phone_number = '+380'
        if self.country == 'united_arab_emirates':
            self.phone_number = '+971'
        if self.country == 'china':
            self.phone_number = '+86'
        if self.country == 'singapore':
            self.phone_number = '+65'
        if self.country == 'indonesia':
            self.phone_number = '+62'
        if self.country == 'russia':
            self.phone_number = '+7'
        if self.country == 'oman':
            self.phone_number = '+968'
        if self.country == 'nepal':
            self.phone_number = '+977'
        if self.country == 'japan':
            self.phone_number = '+81'

    def get_phone_number_for_whatsapp(self):
        for rec in self:
            # modified_value = "Modified: "
            # rec.sample = 'modified_value'
            if rec.phone_number:
                rec.sample = "https://web.whatsapp.com/send?phone=" + rec.phone_number or "https://api.whatsapp.com/send?phone=" + rec.phone_number
            else:
                rec.sample = ''

    sample = fields.Char(string='Sample', compute='get_phone_number_for_whatsapp')


    def whatsapp_click_button(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Leads Whatsapp",
            'target': 'new',
            'url': self.sample,
        }

    def action_lead_assign(self):
        if not self.leads_assign:
            raise ValidationError(_('Please Enter the Assign Date'))
        else:
            number = self.phone_number
            reversed_number = number[-10:]
            print(reversed_number, 'reversed_number')
            reverse_checking = self.search([('phone_number', 'like', f'%{reversed_number}')], limit=1)
            if reverse_checking:
                print(reverse_checking.name, 'reverse_checking')
            # self.write({'state': 'assigned',
            #             'assigned_date': fields.Datetime.now()})
