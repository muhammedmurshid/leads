from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class LeadsForm(models.Model):
    _name = 'leads.logic'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Leads'
    _rec_name = 'name'
    _order = 'id desc'

    leads_source = fields.Many2one('leads.sources', string='Leads Source', required=True)
    name = fields.Char(string='Lead Name', required=True)
    email_address = fields.Char(string='Email Address')
    phone_number = fields.Char(string='Mobile Number', required=True)
    probability = fields.Float(string='Probability')
    admission_status = fields.Boolean(string='Admission', readonly=False)
    date_of_adding = fields.Date(string='Date of Adding', default=fields.Datetime.now)
    last_update_date = fields.Datetime(string='Last Updated Date')
    course_id = fields.Char(string='Course')
    reference_no = fields.Char(string='Sequence Number', required=True,
                               readonly=True, default=lambda self: _('New'))
    touch_ids = fields.One2many('leads.own.touch.points', 'touch_id', string='Touch Points')
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
    place = fields.Char('Place')
    leads_assign = fields.Many2one('hr.employee', string='Assign to', default=lambda self: self.env.user.employee_id)
    lead_owner = fields.Many2one('hr.employee', string='Lead Owner')
    seminar_lead_id = fields.Integer()
    phone_number_second = fields.Char(string='Phone Number')
    sample = fields.Char(string='Sample', compute='get_phone_number_for_whatsapp')
    field_to_display = fields.Char(string='Field to Display')
    course_type = fields.Selection(
        [('indian', 'Indian'), ('international', 'International'), ('crash', 'Crash'), ('repeaters', 'Repeaters'),
         ('nil', 'Nil')],
        string='Course Type')
    lead_channel = fields.Char(string='Lead Channel')
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
    college_name = fields.Char(string='College/School')
    lead_referral_staff_id = fields.Many2one('res.users', string='Lead Referral Staff')
    referred_by = fields.Selection([('staff', 'Staff'), ('student', 'Student'), ('other', 'Other')],
                                   string='Referred By')
    campaign_name = fields.Char(string='Campaign Name')
    country = fields.Selection(
        [('india', 'India'), ('germany', 'Germany'), ('canada', 'Canada'), ('usa', 'USA'), ('australia', 'Australia'),
         ('italy', 'Italy'), ('france', 'France'), ('united_kingdom', 'United Kingdom'),
         ('saudi_arabia', 'Saudi Arabia'), ('ukraine', 'Ukraine'), ('united_arab_emirates', 'United Arab Emirates'),
         ('china', 'China'), ('japan', 'Japan'), ('singapore', 'Singapore'), ('indonesia', 'Indonesia'),
         ('russia', 'Russia'), ('oman', 'Oman'), ('nepal', 'Nepal'), ('japan', 'Japan')],
        string='Country', default='india')
    referred_by_id = fields.Many2one('hr.employee', string='Referred Person')
    referred_by_name = fields.Char(string='Referred Person')
    referred_by_number = fields.Char(string='Referred Person Number')
    batch_preference = fields.Char(string='Batch Preference')

    lead_qualification = fields.Selection(
        [('plus_one_science', 'Plus One Science'), ('plus_two_science', 'Plus Two Science'),
         ('plus_two_commerce', 'Plus Two Commerce'), ('plus_one_commerce', 'Plus One Commerce'),
         ('commerce_degree', 'Commerce Degree'),
         ('other_degree', 'Other Degree'), ('working_professional', 'Working Professional')],
        string='Lead qualification')
    adm_id = fields.Integer(string='Admission Id')
    student_id = fields.Many2one('logic.students', string='Student Id')

    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other'), ('nil', 'Nil')],
                                string='District', required=True)
    referred_teacher = fields.Many2one('res.users', string='Referred Teacher')
    over_due = fields.Boolean(string='Over Due')
    remarks = fields.Char(string='Remarks')
    parent_number = fields.Char('Parent Number')
    mode_of_study = fields.Selection([('online', 'Online'), ('offline', 'Offline'), ('nil', 'Nil')],
                                     string='Mode of Study',
                                     required=True)
    assigned_date = fields.Date(string='Assigned Date', readonly=1)
    platform = fields.Selection(
        [('facebook', 'Facebook'), ('instagram', 'Instagram'), ('website', 'Website'), ('just_dial', 'Just Dial'),
         ('other', 'Other')],
        string='Platform')

    admission_date = fields.Date(string='Admission Date', compute='_compute_admission_status', store=True,
                                 readonly=False)
    lead_user_type = fields.Selection(
        [('basic', 'Basic'), ('teacher', 'Teacher'), ('marketing', 'Marketing'), ('other', 'Other')],
        string='Acquisition Channel', default='basic')

    @api.depends('remarks_lead_user_id')
    def _check_remarks(self):
        for rec in self:
            re = ''
            if rec.remarks_lead_user_id:
                re += rec.remarks_lead_user_id.name
            rec.lead_status_name = re

    lead_status_name = fields.Char(string='Lead Status Name', compute="_check_remarks", store=True)

    @api.onchange('lead_source_name')
    def check_lead_source_incoming(self):
        for rec in self:
            if rec.lead_source_name:
                if "Incoming Calls" in rec.lead_source_name:
                    rec.incoming_source_checking = True
                    print('ya')
                elif "Walk In" in rec.lead_source_name:
                    rec.incoming_source_checking = True
                elif "WhatsApp" == rec.lead_source_name:
                    rec.incoming_source_checking = True
                else:
                    rec.incoming_source_checking = False
                    print('na')

    @api.onchange('tele_caller_ids', 'name')
    def get_tele_callers_in_domain(self):
        users = self.env.ref('leads.lead_tele_callers').users
        lead_users = []
        for j in users:
            print(j.name, 'j')
            lead_users.append(j.id)
        domain = [('id', 'in', lead_users)]
        return {'domain': {'tele_caller_ids': domain}}
    tele_caller_ids = fields.Many2many('res.users', string='Tele Caller', domain=get_tele_callers_in_domain)
    course_level = fields.Many2one('course.levels', string='Course Level',
                                   domain="[('course_id', '=', base_course_id)]")
    level_name = fields.Char(string='Level Name', compute='get_course_groups', store=True)
    academic_year = fields.Selection(
        [('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'),
         ('2026', '2026'), ('nil', 'Nil')], string='Academic Year', required=True)

    @api.onchange('branch', 'preferred_batch_id', 'course_level', 'course_group', 'course_type', 'academic_year')
    def get_branch_inside_batches(self):
        print('oooops')
        ids = []
        for j in self:
            group = self.env['logic.base.batch'].search([('branch_id', '=', j.branch.id)])
            for rec in group:
                if j.academic_year:
                    if j.academic_year == rec.academic_year:
                        ids.append(rec.id)
                else:
                    print(rec.id, 'gr')
                    ids.append(rec.id)
        if self.branch:
            print('kkkkk')
            domain = [('id', 'in', ids)]
        else:
            print('naaaa')
            domain = []
        return {'domain': {'preferred_batch_id': domain}}

    preferred_batch_id = fields.Many2one('logic.base.batch', string='Preferred Batch')
    branch_true_or_false = fields.Boolean(string='Branch Check')

    @api.onchange('branch')
    def get_branch(self):
        if self.branch:
            self.branch_true_or_false = True
        else:
            self.branch_true_or_false = False

    @api.depends('make_visible')
    def get_user(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('leads.leads_admin'):
            self.make_visible = True
        else:
            self.make_visible = False

    make_visible = fields.Boolean(string="User", default=True, compute='get_user')

    # @api.onchange('course_level', 'course_group', 'course_type', 'course_papers_ids', 'preferred_batch_id')
    # def get_course_groups(self):
    #     for j in self:
    #         j.level_name = j.course_level.name
    #         ids = []
    #         if not j.level_name == 'Nil':
    #             # ids.append(self.base_course_id.course_levels.ids)
    #             group = self.env['course.groups'].search([('level_ids', '=', j.course_level.id)])
    #             for rec in group:
    #                 print(rec.id, 'gr')
    #                 ids.append(rec.id)
    #             domain = [('id', 'in', ids)]
    #             return {'domain': {'course_group': domain}}
    #         else:
    #             group = self.env['course.groups'].sudo().search([])
    #             for rec in group:
    #                 print(rec.id, 'gr')
    #                 ids.append(rec.id)
    #             domain = [('id', 'in', ids)]
    #             return {'domain': {'course_group': domain}}

    course_group = fields.Many2one('course.groups', string='Course Group/Part',
                                   domain="[('level_ids', 'in', course_level)]")

    def action_add_lead_user_type(self):
        leads = self.env['leads.logic'].sudo().search([])
        for i in leads:
            if i.lead_source_name == 'Seminar' or i.lead_source_name == 'Seminar Data':
                if i.seminar_id != 0:
                    i.lead_user_type = 'marketing'

    # @api.onchange('course_group', 'course_type', 'course_level', 'preferred_batch_id')
    # def get_course_papers(self):
    #     ids = []
    #     # ids.append(self.base_course_id.course_levels.ids)
    #     group = self.env['course.papers'].search([('group_ids', '=', self.course_group.id)])
    #     for rec in group:
    #         print(rec.id, 'gr')
    #         ids.append(rec.id)
    #     domain = [('id', 'in', ids)]
    #     return {'domain': {'course_papers': domain}}

    course_papers = fields.Many2many('course.papers', string='Course Papers',
                                     domain="[('group_ids', 'in', course_group)]")

    # touch_points

    count_of_total_touch_points = fields.Integer(compute='get_count_of_total_touch_points', store=True)
    source_seminar_or_not = fields.Boolean(string='Source Seminar or Not')
    title = fields.Char(string='Title')
    referral_staff_id = fields.Many2one('res.users', string='Referral Staff')
    college_type_listed = fields.Selection(string='College', selection=[('listed', 'Listed'), ('unlisted', 'Unlisted')],
                                           default='unlisted')
    lead_source_ids = fields.Many2many('leads.sources', string='Lead Sources')
    list_id = fields.Char(string='List')

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

    def action_bulk_lead_re_allocation(self):
        active_ids = self.env.context.get('active_ids', [])
        print(active_ids, 'current rec')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Re Allocation',
            'res_model': 're_allocation.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'parent_obj': active_ids}

        }

    def old_states_changing_adm_counts(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['leads.logic'].browse(selected_ids)

        for i in selected_records:
            if i.admission_status == True:
                if i.admission_count == 0:
                    student = self.env['logic.students'].create({
                        'name': i.name,
                        'lead_id': i.id,
                    })

    def add_admission_fee_collection_data(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['leads.logic'].browse(selected_ids)

        for i in selected_records:

            if i.admission_status == True:
                if i.admission_count == 0:
                    domain = self.env['logic.students'].search([('lead_id', '=', i.id)])
                    for j in domain:
                        print(j.name, 'oops')
                        fee = self.env['admission.fee.collection'].create({
                            'name': j.id,
                            'lead_id': j.lead_id,
                        })

    def compute_count(self):
        for record in self:
            record.admission_count = self.env['admission.fee.collection'].search_count(
                [('lead_id', '=', record.id)])

    admission_count = fields.Integer(compute='compute_count')

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

    def action_re_allocation_wizard(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Re Allocation',
            'view_mode': 'form',
            'res_model': 're_allocation.wizard',
            'target': 'new',
            'context': {'parent_obj': self.id}
        }

    def compute_student_count(self):
        for record in self:
            record.student_count = self.env['logic.students'].search_count(
                [('id', '=', self.student_id.id)])

    student_count = fields.Integer(compute='compute_student_count')

    @api.onchange('leads_source', 'lead_source_name')
    def get_source_seminar_or_not(self):
        for record in self:
            if record.lead_source_name == 'Seminar':
                record.source_seminar_or_not = True

            elif record.lead_source_name == 'Seminar Data':
                record.source_seminar_or_not = True
            elif record.lead_source_name == 'Webinar':
                record.source_seminar_or_not = True
            else:
                record.source_seminar_or_not = False

    def action_cron_job_activity_for_after_4_days(self):
        print('working')
        rec = self.env['leads.logic'].sudo().search([])
        today = fields.Date.today()
        for record in rec:
            if record.lead_user_type != 'teacher':
                if not record.activity_ids:
                    if record.assigned_date:
                        delta = today - record.assigned_date
                        if delta.days > 4:
                            if record.state == 'confirm' or record.state == 're_allocated':
                                print('yaaaaaaaa', record.admission_status, record.id)
                                if record.admission_status != True:
                                    if record.lead_quality != 'bad_lead':
                                        record.over_due = True
                                        print('yes', record.id)
                                        record.activity_schedule(
                                            'leads.mail_seminar_leads_done', user_id=record.leads_assign.user_id.id,
                                            note=f'Please update status for the lead assigned four days ago.'),

            else:
                print('no', record.id)

    def action_cancel_cron_for_bad_leads(self):
        lead = self.env['leads.logic'].sudo().search([])
        today = fields.Date.today()
        for rec in lead:
            if rec.assigned_date:
                delta = today - rec.assigned_date
                if delta.days > 4:
                    if rec.state == 'confirm':
                        if rec.lead_quality == 'bad_lead' or rec.admission_status == True:
                            activity_id = self.env['mail.activity'].search(
                                [('res_id', '=', rec.id), (
                                    'activity_type_id', '=',
                                    self.env.ref('leads.mail_seminar_leads_done').id)])
                            if activity_id:
                                activity_id.action_feedback(feedback=f'Done.')

    def action_cron_job_for_over_due_leads(self):
        print('over_due_checking')
        lead = self.env['leads.logic'].sudo().search([])
        today = fields.Date.today()
        for rec in lead:
            if rec.assigned_date:
                delta = today - rec.assigned_date
                if delta.days > 4:
                    if rec.state == 'confirm' or rec.state == 're_allocated':
                        if rec.lead_quality != 'bad_lead':
                            rec.over_due = True
                        else:
                            rec.over_due = False
                    else:
                        rec.over_due = False
                else:
                    rec.over_due = False

    def action_created_records_states_changing(self):
        lead = self.env['leads.logic'].sudo().search([])
        for rec in lead:
            if rec.leads_assign:
                if rec.state == 'draft':
                    print(rec.create_date, 'res date')
                    rec.assigned_date = rec.create_date
                    rec.state = 'confirm'

    @api.onchange('course_type', 'base_course_id')
    def onchange_course_id_domain(self):
        if self.course_type:
            course = self.env['logic.base.courses'].search([('type', '=', self.course_type)])
            courses = []
            for rec in course:
                if rec.state == 'done':
                    courses.append(rec.id)
            domain = [('id', 'in', courses)]
            print(courses, 'nn')
            return {'domain': {'base_course_id': domain}}

    base_course_id = fields.Many2one('logic.base.courses', string='Preferred Course', required=True,
                                     domain=[('state', '=', 'done')])

    branch = fields.Many2one('logic.base.branches', string='Branch', required=1)

    def get_old_branch_to_new_branch(self):
        rec = self.env['leads.logic'].sudo().search([])
        for record in rec:
            if record.branch_id:
                if record.branch_id.branch_name == 'Kottayam Campus':
                    record.branch = 3
                if record.branch_id.branch_name == 'Corporate Office & City Campus':
                    record.branch = 1
                if record.branch_id.branch_name == 'Cochin Campus':
                    record.branch = 1
                if record.branch_id.branch_name == 'Trivandrum Campus':
                    record.branch = 6
                if record.branch_id.branch_name == 'Calicut Campus':
                    record.branch = 4
                if record.branch_id.branch_name == 'Malappuram Campus':
                    record.branch = 9
                if record.branch_id.branch_name == 'Palakkad Campus':
                    record.branch = 7

                if record.branch_id.branch_name == 'Online Campus':
                    record.branch = 10

    @api.depends('leads_source')
    def get_leads_source_name(self):
        for record in self:
            record.lead_source_name = record.leads_source.name

    lead_source_name = fields.Char(string='Lead Source Name', compute='get_leads_source_name', store=True)

    @api.depends('touch_ids')
    def get_count_of_total_touch_points(self):
        for record in self:
            self.count_of_total_touch_points = len(record.touch_ids)

    finished_touch_points = fields.Integer(compute='get_finished_touch_points', store=True)
    touch_status = fields.Selection(
        [('draft', 'Draft'), ('touch_one', 'Touch One'), ('touch_two', 'Touch Two'), ('touch_three', 'Touch Three'),
         ('touch_two', 'Touch Two'), ('touch_four', 'Touch Four'), ('touch_five', 'Touch Five'),
         ('touch_six', 'Touch Six'), ('touch_seven', 'Touch Seven'), ('touch_eight', 'Touch Eight'),
         ('touch_nine', 'Touch Nine'), ('touch_ten', 'Touch Ten'), ('finished', 'Finished')], default='draft',
        string='Touch Status')

    @api.onchange('count_of_total_touch_points', 'finished_touch_points')
    def get_touch_status(self):
        for record in self:
            if record.count_of_total_touch_points == record.finished_touch_points:
                record.touch_status = 'finished'
            elif record.finished_touch_points == 0:
                record.touch_status = 'draft'
            elif record.finished_touch_points == 1:
                record.touch_status = 'touch_one'
            elif record.finished_touch_points == 2:
                record.touch_status = 'touch_two'
            elif record.finished_touch_points == 3:
                record.touch_status = 'touch_three'
            elif record.finished_touch_points == 4:
                record.touch_status = 'touch_four'
            elif record.finished_touch_points == 5:
                record.touch_status = 'touch_five'
            elif record.finished_touch_points == 6:
                record.touch_status = 'touch_six'
            elif record.finished_touch_points == 7:
                record.touch_status = 'touch_seven'
            elif record.finished_touch_points == 8:
                record.touch_status = 'touch_eight'
            elif record.finished_touch_points == 9:
                record.touch_status = 'touch_nine'
            elif record.finished_touch_points == 10:
                record.touch_status = 'touch_ten'

    @api.depends('touch_ids')
    def get_finished_touch_points(self):
        for record in self:
            record.finished_touch_points = len(record.touch_ids.filtered(lambda x: x.finished == True))

    finished_points = fields.Char('Finished Touch Points')

    def action_print_activity_date(self):
        if self.activity_ids:
            print(self.activity_ids.create_date.date(), 'date')
        else:
            print('no activity')

    @api.onchange('touch_ids', 'count_of_total_touch_points', 'finished_touch_points')
    def get_finished_count(self):
        for i in self:
            print(str(i.count_of_total_touch_points) + '/' + str(i.finished_touch_points), '[[[')
            i.finished_points = str(i.count_of_total_touch_points) + '/' + str(i.finished_touch_points)

    @api.onchange('country')
    def get_country_code(self):
        if self.country == 'india':
            self.phone_number = '+91'
        if self.country == 'germany':
            self.phone_number = '+49'
        if self.country == 'canada':
            self.phone_number = '+1'
        if self.country == 'usa':
            self.phone_number = '+1'
        if self.country == 'australia':
            self.phone_number = '+61'
        if self.country == 'italy':
            self.phone_number = '+39'
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

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'leads.logic') or _('New')
        #
        number = vals.get('phone_number')
        second_number = vals.get('phone_number_second')

        reversed_number = number[-10:]
        print(reversed_number, 'reversed_number')
        reverse_checking = self.search(
            [('phone_number', 'like', f'%{reversed_number}')], limit=1)

        current_rec = self.env['leads.logic'].search([('phone_number', 'ilike', number)], limit=1)
        print(current_rec, 'reveeeee')

        if reverse_checking:
            # Update the existing record with new values
            # reverse_checking.write(vals)

            duplicate = self.env['logic.leads.duplicates'].create({'name': vals.get('name'),
                                                                   'phone_number': vals.get('phone_number'),
                                                                   'lead_source_id': vals.get('leads_source'),
                                                                   'email_address': vals.get('email_address'),
                                                                   'country': vals.get('country'),
                                                                   'district': vals.get('district'),
                                                                   'place': vals.get('place'),
                                                                   'mode_of_study': vals.get('mode_of_study'),
                                                                   'platform': vals.get('platform'),
                                                                   'lead_qualification': vals.get('lead_qualification'),
                                                                   'last_studied_course': vals.get(
                                                                       'last_studied_course'),
                                                                   'original_lead_id': current_rec.id,
                                                                   # 'remark_id': vals.get('remark_id'),
                                                                   'college_name': vals.get('college_name'),
                                                                   'branch': vals.get('branch'),
                                                                   'course_type': vals.get('course_type'),
                                                                   'academic_year': vals.get('academic_year'),
                                                                   'course_id': vals.get('base_course_id'),
                                                                   'course_level': vals.get('course_level'),
                                                                   'course_group': vals.get('course_group'),
                                                                   'course_papers': vals.get('course_papers'),
                                                                   'preferred_batch_id': vals.get(
                                                                       'preferred_batch_id'),
                                                                   'lead_status': vals.get('lead_status'),
                                                                   'lead_quality': vals.get('lead_quality'),
                                                                   'probability': vals.get('probability'),
                                                                   'lead_owner': self.env.user.employee_id.id,
                                                                   'leads_assign': vals.get('leads_assign'),
                                                                   'assigned_date': vals.get('assigned_date'),
                                                                   'date_of_adding': vals.get('date_of_adding'),
                                                                   'last_update_date': vals.get('last_update_date'),
                                                                   'admission_date': vals.get('admission_date')})
            return reverse_checking
        if second_number:
            second_reverse = second_number[-10:]
            print(second_reverse, 'second_reverse testt')
            second_number_checking = self.search(
                [('phone_number', 'like', f'%{second_reverse}')], limit=1)
            sec_lead_id = self.env['leads.logic'].sudo().search([('phone_number', 'ilike', second_number)], limit=1)

            if second_number_checking:
                duplicate = self.env['logic.leads.duplicates'].create({'name': vals.get('name'),
                                                                       'phone_number': vals.get('phone_number'),
                                                                       'lead_source_id': vals.get('leads_source'),
                                                                       'email_address': vals.get('email_address'),
                                                                       'country': vals.get('country'),
                                                                       'district': vals.get('district'),
                                                                       'place': vals.get('place'),
                                                                       'mode_of_study': vals.get('mode_of_study'),
                                                                       'platform': vals.get('platform'),
                                                                       'lead_qualification': vals.get(
                                                                           'lead_qualification'),
                                                                       'last_studied_course': vals.get(
                                                                           'last_studied_course'),
                                                                       'original_lead_id': sec_lead_id.id,
                                                                       # 'remark_id': vals.get('remark_id'),
                                                                       'college_name': vals.get('college_name'),
                                                                       'branch': vals.get('branch'),
                                                                       'course_type': vals.get('course_type'),
                                                                       'academic_year': vals.get('academic_year'),
                                                                       'course_id': vals.get('base_course_id'),
                                                                       'course_level': vals.get('course_level'),
                                                                       'course_group': vals.get('course_group'),
                                                                       'course_papers': vals.get('course_papers'),
                                                                       'preferred_batch_id': vals.get(
                                                                           'preferred_batch_id'),
                                                                       'lead_status': vals.get('lead_status'),
                                                                       'lead_quality': vals.get('lead_quality'),
                                                                       'probability': vals.get('probability'),
                                                                       'lead_owner': self.env.user.employee_id.id,
                                                                       'leads_assign': vals.get('leads_assign'),
                                                                       'assigned_date': vals.get('assigned_date'),
                                                                       'date_of_adding': vals.get('date_of_adding'),
                                                                       'last_update_date': vals.get('last_update_date'),
                                                                       'admission_date': vals.get('admission_date')})
                return second_number_checking
        else:
            return super(LeadsForm, self).create(vals)

    def add_touches(self):
        touch_points = self.env['leads.touch.points'].sudo().search([])
        for touch in touch_points:
            print(touch.name, 'toches')
            points = []
            res_list = {
                'name': touch.id,
            }
            points.append((0, 0, res_list))
            self.touch_ids = points

    def action_done(self):
        # for i in self.activity_ids:
        #     i.action_feedback(feedback='done')
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('leads.mail_seminar_leads_done').id)])
        if activity_id:
            activity_id.action_feedback(feedback=f'lead status is done.')

        self.state = 'done'

    def get_duplicate_leads(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Duplicate',
            'view_mode': 'tree,form',
            'res_model': 'logic.leads.duplicates',
            'domain': [('original_lead_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_duplicates_leads_count(self):
        number = self.phone_number
        reversed_number = number[-10:]
        for record in self:
            record.duplicates_count = self.env['logic.leads.duplicates'].search_count(
                [('original_lead_id', '=', self.id)])

    duplicates_count = fields.Integer(compute='compute_duplicates_leads_count')

    # @api.constrains('phone_number_second')
    # def check_number_duplicate(self):
    #     for record in self:
    #         if record.phone_number_second:
    #             duplicate_records = self.search(
    #                 [('phone_number_second', '=', record.phone_number_second), ('id', '!=', record.id)])
    #             if duplicate_records:
    #                 raise ValidationError(
    #                     'This number already exists in the records created by ' + record.create_uid.name + ' ' + 'number is ' + str(
    #                         record.phone_number_second))

    # @api.constrains('phone_number')
    # def check_number_duplicate_mobile_number(self):
    #     for record in self:
    #         if record.phone_number:
    #             duplicate_records = self.search(
    #                 [('phone_number', '=', record.phone_number), ('id', '!=', record.id)])
    #             if duplicate_records:
    #                 raise ValidationError(
    #                     'This number already exists in the records created by ' + record.create_uid.name + ' ' + 'number is ' + str(
    #                         record.phone_number))

    def reset_to_draft(self):
        self.state = 'draft'

    @api.depends('sample')
    def _compute_display_value(self):
        for record in self:
            if record.sample:
                # Modify the display value as needed based on the original field's value
                modified_value = "Modified: "
                record.sample = modified_value

    def get_phone_number_for_whatsapp(self):
        for rec in self:
            # modified_value = "Modified: "
            # rec.sample = 'modified_value'
            if rec.phone_number:
                rec.sample = "https://web.whatsapp.com/send?phone=" + rec.phone_number or "https://api.whatsapp.com/send?phone=" + rec.phone_number
            else:
                rec.sample = ''

    def whatsapp_click_button(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Leads Whatsapp",
            'target': 'new',
            'url': self.sample,
        }

    def multiple_leads_assigning(self):

        active_ids = self.env.context.get('active_ids', [])
        # sales = sale_obj.browse(active_ids)
        print(active_ids, 'current rec')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Leads Owner',
            'res_model': 'leads.assigning.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'parent_obj': active_ids}

        }

    def multiple_leads_change_state(self):
        active_ids = self.env.context.get('active_ids', [])
        # sales = sale_obj.browse(active_ids)
        print(active_ids, 'current rec')
        leads = self.env['leads.logic'].sudo().search([('id', 'in', active_ids)])
        for rec in leads:
            print(rec, 'rec')
            rec.state = 'confirm'
            rec.assigned_date = fields.Datetime.now()

    # @api.onchange('admission_status')
    # def _onchange_admission_status(self):
    #     print('booooooooooooooo')
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Assign Leads Owner',
    #         'res_model': 'add.to.student.list',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'target': 'new',
    #         # 'context': {'parent_obj': active_ids}
    #
    #     }

    def confirm(self):
        touch_points = self.env['leads.touch.points'].sudo().search([])
        for touch in touch_points:
            print(touch.name, 'touches')
            points = []
            res_list = {
                'name': touch.id,

            }
            points.append((0, 0, res_list))
            self.touch_ids = points
        # self.activity_schedule('leads.mail_seminar_leads_done',
        #                        user_id=self.leads_assign.user_id.id)
        # print('agsfdsdshdasgda')
        # for i in self.activity_ids:
        #     i.action_feedback(feedback='confirmed')

        self.state = 'confirm'
        self.assigned_date = datetime.now()

    def activity_remove_in_leads(self):
        activity = self.env['mail.activity'].sudo().search(
            [('res_model', '=', 'leads.logic'),
             ('activity_type_id', '=', self.env.ref('leads.mail_seminar_leads_done').id)])
        for i in activity:
            i.unlink()
            print(i.res_model, 'activity')
        # activity.unlink()

    # @api.onchange('admission_status')
    # def _onchange_admission_status(self):
    #     print('kh;hfhdphodgs')
    #
    @api.depends('admission_status')
    def _compute_admission_status(self):
        for i in self:
            if i.admission_status == True:
                i.admission_date = datetime.now()
            else:
                i.admission_date = False

    @api.onchange('admission_status')
    def _onchange_admission_status(self):
        print('hi', self.seminar_lead_id)
        ss = self.env['seminar.students'].search([('id', '=', self.seminar_lead_id)])
        print(ss.whatsapp_number, 'jfhsdjfhgfaweyuwe')

        if self.admission_status == True:
            ss.admission_status = 'yes'
            # self.admission_date = datetime.now()
        if self.admission_status == False:
            self.admission_date = False

    def action_admission(self):
        print(self.id, 'admission')

        # admission wizard codes
        return {
            'type': 'ir.actions.act_window',
            'name': 'Admission Form',
            'res_model': 'add.to.student.list',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_mode_of_study': self.mode_of_study, 'default_course_type': self.course_type,
                        'default_email': self.email_address,
                        'default_mobile_number': self.phone_number, 'default_batch_id': self.preferred_batch_id.id,
                        'default_current_rec': self.id, 'default_student_name': self.name,
                        'default_course_id': self.base_course_id.id, 'default_branch_id': self.branch.id,
                        'default_course_level_id': self.course_level.id,
                        'default_course_group_id': self.course_group.id,
                        'default_course_papers_ids': self.course_papers.ids,
                        'default_academic_year': self.academic_year,
                        }

        }
        self.write({
            'admission_status': True,
            'state': 'done'
        })

    sales_person_id = fields.Many2one('res.users', string='Sales person')
    seminar_id = fields.Integer(string='Seminar')

    def perf_leads_users_open_action(self):
        user = []
        users = self.env.ref('leads.lead_staff_referral').users
        for i in users:
            user.append(i.id)
        print(user, 'user')
        print(self.env.user.id, 'user')
        if self.env.user.id in user:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Leads',
                'res_model': 'staff.reference.leads',
                'view_mode': 'tree,form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Leads',
                'res_model': 'leads.logic',
                'view_mode': 'tree,form,activity,pivot',
                'target': 'current',
            }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Open Leads',
        #     'res_model': 'sale.order',
        #     'view_mode': 'tree,form',
        #     'target': 'current',
        # }

    @api.onchange('leads_source', 'lead_owner', 'name', 'email_address', 'phone_number', 'phone_number_second', 'place',
                  'district', 'course_id', 'lead_qualification', 'last_studied_course', 'probability', 'leads_assign',
                  'admission_status', 'lead_quality', 'sales_person_id')
    def onchange_fields_dates(self):
        for i in self:
            i.last_update_date = fields.Datetime.now()

    def cancel_lead(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('leads.mail_seminar_leads_done').id)])
        if activity_id:
            activity_id.action_feedback(feedback=f'lead is cancelled.')
        self.state = 'cancel'

    @api.depends('leads_source')
    def get_manager(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        print('res_user.has_group')
        if res_user.has_group('leads.leads_admin'):
            self.make_visible_manager = False

        else:
            self.make_visible_manager = True

    make_visible_manager = fields.Boolean(string="User", compute='get_manager')

    def action_add_lead_quality_undefined_to_nil(self):
        active_ids = self.env.context.get('active_ids', [])
        rec = self.env['leads.logic'].sudo().search([('id', 'in', active_ids)])
        for i in rec:
            if not i.lead_quality:
                i.lead_quality = 'nil'

    # @api.depends('phone_number')
    # def _compute_name_without_spaces(self):
    #     for record in self:
    #         record.name_without_spaces = record.phone_number.replace(' ', '')
    @api.constrains('phone_number')
    def _check_name(self):
        for record in self:
            if ' ' in record.phone_number:
                record.phone_number = record.phone_number.replace(' ', '')

    def button_remove_spaces(self):
        rec = self.env['leads.logic'].search([])
        for record in rec:
            if ' ' in record.phone_number:
                record.phone_number = record.phone_number.replace(' ', '')

    def current_user_id(self):
        for i in self:
            i.current_user_id_int = self.env.user.id

    current_user_id_int = fields.Integer(string='Current User ID', compute='current_user_id')

    def change_leads_channel_name(self):
        for i in self:
            print(i.name, 'name')
        print('hi')
        active_ids = self.env.context.get('active_ids', [])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leads Channel',
            'res_model': 'channel.name.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'parent_obj': active_ids}

        }

    def action_change_source_seminar_to_seminar_data(self):
        rec = self.env['leads.logic'].sudo().search([])
        for i in rec:
            if i.leads_source:
                if i.lead_source_name == 'Seminar':
                    i.leads_source = 12

    def action_add_country_code(self):
        rec = self.env['leads.logic'].sudo().search([])
        for i in rec:
            number = i.phone_number
            number_count = len(number)
            if number_count == 10:
                print(number_count, 'number_count')
                i.phone_number = '+91' + i.phone_number
            if number_count == 12:
                print(number_count, 'number_count')
                i.phone_number = '+' + i.phone_number

    def action_lead_source_where_was_coming_data(self):
        rec = self.env['seminar.students'].sudo().search([])
        for i in rec:
            leads = self.env['leads.logic'].sudo().search([('phone_number', '=', i.contact_number)])
            if leads:
                if leads.lead_source_name == 'Seminar' or leads.lead_source_name == 'Seminar Data':
                    print(leads.name, 'leads')
                    print(i.seminar_id, 'seminar_id')
                    leads.sudo().update({
                        'seminar_id': i.seminar_id
                    })

    remarks_id = fields.Many2one('lead.status', string='Lead Status')
    remarks_lead_user_id = fields.Many2one('lead.status', string='Remarks', required=1)


class LeadsSources(models.Model):
    _name = 'leads.sources'
    _inherit = 'mail.thread'
    _description = 'Leads Sources'

    name = fields.Char('Name', required=True)
    digital_lead = fields.Boolean('Digital Lead', default=False)


class GenerateLeadLink(models.Model):
    _inherit = 'res.users'

    link = fields.Char(string='Link')
    link_active = fields.Boolean(string='Active')

    def action_generate_lead_link(self):
        self.link_active = True
        leads = "leads_form/" + str(self.env.user.id)
        self.link = leads
        print('hhhj')


class LeadsAssigningWizard(models.TransientModel):
    _name = 'leads.assigning.wizard'

    @api.onchange('assigned_to')
    def _onchange_leads_users(self):
        users = self.env.ref('leads.leads_basic_user').users
        lead_users = []
        for j in users:
            print(j.name, 'j')
            lead_users.append(j.employee_id.id)
        domain = [('id', 'in', lead_users)]
        return {'domain': {'assigned_to': domain}}

    assigned_to = fields.Many2one('hr.employee', string='Assigned To', domain=_onchange_leads_users)

    def action_done(self):
        # abc = self.env['leads.logic'].sudo().update({
        #     'lead_owner': self.assigned_to
        # })
        print(self._context['parent_obj'], 'current rec')

        aa = self.env['leads.logic'].search([])
        for i in aa:
            if i.id in self._context['parent_obj']:
                i.leads_assign = self.assigned_to
                i.state = 'confirm'
                i.assigned_date = fields.Datetime.now()
        # aa.lead_owner = self.assigned_to
        # abc.lead_owner = self.assigned_to

        # for i in abc:
        #     if i:
        #         print(i.id, 'selected only')
        #         abc.lead_owner = self.assigned_to

        print('hi')

    def cancel(self):
        print('hi')


class LeadsOwnTouchPoints(models.Model):
    _name = 'leads.own.touch.points'

    name = fields.Many2one('leads.touch.points', string='Touch Points')
    finished = fields.Boolean(string='Finished')
    date = fields.Datetime(string='Date')
    touch_id = fields.Many2one('leads.logic', string='Touch ID')

    @api.onchange('finished')
    def onchange_finished(self):
        for record in self:
            if record.finished == True:
                record.date = fields.Datetime.now()
            if record.finished == False:
                record.date = False


class AdmissionFeeReceiptCustom(models.Model):
    _name = 'admission.fee.receipt'

    name = fields.Char(string='Test Name')


class LeadStatus(models.Model):
    _name = 'lead.status'
    _inherit = 'mail.thread'
    _description = 'Lead Status'

    name = fields.Char('Name')
