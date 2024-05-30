from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class LogicPipelineDuplicates(models.Model):
    _name = 'logic.leads.duplicates'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Leads'
    _rec_name = 'name'
    _order = 'id desc'

    lead_source_id = fields.Many2one('leads.sources', string='Leads Source',)
    name = fields.Char(string='Lead Name')
    email_address = fields.Char(string='Email Address', widget='mail')
    phone_number = fields.Char(string='Mobile Number', )
    probability = fields.Float(string='Probability')
    date_of_adding = fields.Date(string='Date of Adding', default=fields.Datetime.now)
    last_update_date = fields.Datetime(string='Last Updated Date')
    admission_date = fields.Date(string='Admission Date')
    lead_quality = fields.Selection(
        [('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold'),
         ('bad_lead', 'Bad Lead'),
         ('nil', 'Nil')],
        string='Lead Quality', )
    lead_status = fields.Selection(
        [('not_responding', 'Not Responding'),
         ('already_enrolled', 'Already Enrolled'), ('joined_in_another_institute', 'Joined in another institute'),
         ('nil', 'Nil')],
        string='Lead Status',
    )
    remarks_id = fields.Many2one('lead.status', string='Lead Status')
    original_lead_id = fields.Integer()
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other'), ('nil', 'Nil')],
                                string='District', )
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
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('re_allocated', 'Re Assigned'), ('done', 'Done'),
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
    course_id = fields.Many2one('logic.base.courses', string='Preferred Course',
                                domain=[('state', '=', 'done')])
    branch = fields.Many2one('logic.base.branches', string='Branch', required=1)
    academic_year = fields.Selection(
        [('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'),
         ('2026', '2026'), ('nil', 'Nil')], string='Academic Year', )
    preferred_batch_id = fields.Many2one('logic.base.batch', string='Preferred Batch')

    campaign_name = fields.Char(string='Campaign Name')
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
                                     )
    platform = fields.Selection(
        [('facebook', 'Facebook'), ('instagram', 'Instagram'), ('website', 'Website'), ('just_dial', 'Just Dial'),
         ('other', 'Other')],
        string='Platform')
    lead_owner = fields.Many2one('hr.employee', string='Lead Owner')
    leads_assign = fields.Many2one('hr.employee', string='Assign to', default=lambda self: self.env.user.employee_id)
    assigned_date = fields.Date(string='Assigned Date', readonly=1)

