from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta


class LeadsForm(models.Model):
    _name = 'leads.logic'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Leads'
    _rec_name = 'name'

    leads_source = fields.Many2one('leads.sources', string='Leads Source', required=True)
    name = fields.Char(string='Lead Name', required=True)
    email_address = fields.Char(string='Email Address')
    phone_number = fields.Char(string='Mobile Number', required=True)
    probability = fields.Float(string='Probability')
    admission_status = fields.Boolean(string='Admission', readonly=True)
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
        [('interested', 'Interested'), ('not_interested', 'Not Interested'), ('not_responding', 'Not Responding'),
         ('already_enrolled', 'Already Enrolled'), ('joined_in_another_institute', 'Joined in another institute'),
         ('under_follow_up', 'Under Follow Up')],
        string='Lead Status', required=True
    )

    place = fields.Char('Place')
    leads_assign = fields.Many2one('hr.employee', string='Assign to', default=lambda self: self.env.user.employee_id)
    lead_owner = fields.Many2one('hr.employee', string='Lead Owner')
    seminar_lead_id = fields.Integer()
    phone_number_second = fields.Char(string='Phone Number')
    sample = fields.Char(string='Sample', compute='get_phone_number_for_whatsapp')
    field_to_display = fields.Char(string='Field to Display')
    course_type = fields.Selection(
        [('indian', 'Indian'), ('international', 'International'), ('crash', 'Crash'), ('nil', 'Nil')],
        string='Course Type')
    lead_channel = fields.Char(string='Lead Channel')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')],
        string='State',
        default='draft', tracking=True)
    last_studied_course = fields.Char(string='Last Studied Course')
    college_name = fields.Char(string='College/School')
    referred_by = fields.Selection([('staff', 'Staff'), ('student', 'Student'), ('other', 'Other')],
                                   string='Referred By')
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

    remarks = fields.Char(string='Remarks')
    parent_number = fields.Char('Parent Number')
    mode_of_study = fields.Selection([('online', 'Online'), ('offline', 'Offline'), ('nil', 'Nil')],
                                     string='Mode of Study',
                                     required=True)
    platform = fields.Selection(
        [('facebook', 'Facebook'), ('instagram', 'Instagram'), ('website', 'Website'), ('other', 'Other')],
        string='Platform')

    admission_date = fields.Date(string='Admission Date', compute='_compute_admission_status', store=True)

    @api.onchange('base_course_id')
    def get_course_levels(self):
        ids = []
        # ids.append(self.base_course_id.course_levels.ids)
        levels = self.env['course.levels'].search(
            ['|', ('course_id', '=', self.base_course_id.id), ('name', '=', 'Nil')])
        for rec in levels:
            ids.append(rec.id)
        domain = [('id', 'in', ids)]
        return {'domain': {'course_level': domain}}

    course_level = fields.Many2one('course.levels', string='Course Level', domain=get_course_levels)
    level_name = fields.Char(string='Level Name', compute='get_course_groups', store=True)

    @api.onchange('branch', 'preferred_batch_id')
    def get_branch_inside_batches(self):
        print('oooops')
        ids = []
        for j in self:
            group = self.env['logic.base.batch'].search([('branch_id', '=', j.branch.id)])
            for rec in group:
                print(rec.id, 'gr')
                ids.append(rec.id)
        if self.branch:
            print('kkkkk')
            domain = [('id', 'in', ids)]

        else:
            print('naaaa')
            domain = []
        return {'domain': {'preferred_batch_id': domain}}

    preferred_batch_id = fields.Many2one('logic.base.batch', string='Preferred Batch',
                                         domain=get_branch_inside_batches)

    branch_true_or_false = fields.Boolean(string='Branch Check')

    @api.onchange('branch')
    def get_branch(self):
        if self.branch:
            self.branch_true_or_false = True
        else:
            self.branch_true_or_false = False

    @api.onchange('course_level')
    def get_course_groups(self):
        for j in self:
            j.level_name = j.course_level.name
            ids = []
            if not j.level_name == 'Nil':
                # ids.append(self.base_course_id.course_levels.ids)
                group = self.env['course.groups'].search([('level_ids', '=', j.course_level.id)])
                for rec in group:
                    print(rec.id, 'gr')
                    ids.append(rec.id)
                domain = [('id', 'in', ids)]
                return {'domain': {'course_group': domain}}
            else:
                group = self.env['course.groups'].sudo().search([])
                for rec in group:
                    print(rec.id, 'gr')
                    ids.append(rec.id)
                domain = [('id', 'in', ids)]
                return {'domain': {'course_group': domain}}

    course_group = fields.Many2one('course.groups', string='Course Group/Part', domain=get_course_groups)

    @api.onchange('course_group')
    def get_course_papers(self):
        ids = []
        # ids.append(self.base_course_id.course_levels.ids)
        group = self.env['course.papers'].search([('group_ids', '=', self.course_group.id)])
        for rec in group:
            print(rec.id, 'gr')
            ids.append(rec.id)
        domain = [('id', 'in', ids)]
        return {'domain': {'course_papers': domain}}

    course_papers = fields.Many2many('course.papers', string='Course Papers', domain=get_course_papers)

    # touch_points

    count_of_total_touch_points = fields.Integer(compute='get_count_of_total_touch_points', store=True)
    source_seminar_or_not = fields.Boolean(string='Source Seminar or Not')

    def get_admission_profile(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Admission',
            'view_mode': 'tree,form',
            'res_model': 'admission.fee.collection',
            'domain': [('name', '=', self.student_id.id)],
            'context': "{'create': False}"
        }

    def compute_count(self):
        for record in self:
            record.admission_count = self.env['admission.fee.collection'].search_count(
                [('name', '=', self.student_id.id)])

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

    @api.onchange('base_course_id')
    def onchange_base_course_id(self):
        for record in self:
            record.course_papers = False
            course = self.env['logic.base.courses'].search([('id', '=', record.base_course_id.id)])
            print(course.papers.ids, 'hmm')
            papers = self.env['course.papers'].search([('id', 'in', course.papers.ids)])
            # for j in papers:
            #     record.course_papers = [(4, j.id)]

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
        existing_record = self.env['leads.logic'].sudo().search([('phone_number', '=', vals.get('phone_number'))])
        if existing_record:
            for record in existing_record:
                # Handle the duplicate record, e.g., raise an error
                raise ValidationError(
                    'A record with the same mobile number already exists! created by ' + record.create_uid.name + ' ' + 'number is ' + record.phone_number)

        else:
            print('lll')
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
        for i in self.activity_ids:
            i.action_feedback(feedback='done')

        self.state = 'done'

    @api.constrains('phone_number_second')
    def check_number_duplicate(self):
        for record in self:
            if record.phone_number_second:
                duplicate_records = self.search(
                    [('phone_number_second', '=', record.phone_number_second), ('id', '!=', record.id)])
                if duplicate_records:
                    raise ValidationError(
                        'This number already exists in the records created by ' + record.create_uid.name + ' ' + 'number is ' + str(
                            record.phone_number_second))

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
            print(touch.name, 'toches')
            points = []
            res_list = {
                'name': touch.id,

            }
            points.append((0, 0, res_list))
            self.touch_ids = points
        self.activity_schedule('leads.mail_seminar_leads_done',
                               user_id=self.leads_assign.user_id.id)
        # print('agsfdsdshdasgda')
        # for i in self.activity_ids:
        #     i.action_feedback(feedback='confirmed')

        self.state = 'confirm'

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
        return {
            'type': 'ir.actions.act_window',
            'name': 'Admission Form',
            'res_model': 'add.to.student.list',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_mode_of_study': self.mode_of_study, 'default_email': self.email_address,
                        'default_mobile_number': self.phone_number, 'default_batch_id': self.preferred_batch_id.id,
                        'default_current_rec': self.id, }

        }

    def cron_seven_days_checking_lead(self):
        print('working')
        records = self.env['leads.logic'].search([('state', '=', 'confirm')])
        users_ids = []
        current_datetime = datetime.now()
        current_date = current_datetime.date()

        print(current_date, 'date')

        for rec in records:
            if rec.date_of_adding:
                print(rec.date_of_adding, 'date_of_adding')
                seven_days_later = rec.date_of_adding + timedelta(days=7)
                print(seven_days_later, 'seven_days_later')
                if rec.date_of_adding + timedelta(days=7) == current_date:
                    print('ya')
                    if rec.admission_status == False:
                        # print(rec.id, 'id')
                        rec.write({'state': 'draft'})
                        users = rec.env.ref('leads.leads_admin').users
                        for i in users:
                            # users_ids.append(i.id)
                            print(i.name, 'users')
                            rec.activity_schedule('leads.mail_activity_for_returned_leads', user_id=i.id,
                                                  lead_id=rec.id, assign_to=rec.leads_assign.id,
                                                  note=f'Lead status reset to Draft as the students admission decision is pending.')
                    else:
                        print('no')
                    print('hhi')
                else:
                    print('no')

            print(rec.id, 'id')
            print(rec.state, 'state')

            # rec.state = 'draft'

    # def leadcreation(self):
    #     if not self.sales_person_id:
    #         raise ValidationError('Please select sales person')
    #     elif not self.name:
    #         raise ValidationError('Please enter name')
    #     elif not self.email_address:
    #         raise ValidationError('Please enter email address')
    #     else:
    #         crm = self.env['crm.lead'].create({
    #             'student_name': self.name,
    #             # 'email_from': self.email_address,
    #             'phone': self.phone_number,
    #             'name': self.name,
    #             'user_id': self.sales_person_id.id,
    #         }
    #         )
    #         self.state = 'crm'
    #
    #     print('hi')

    sales_person_id = fields.Many2one('res.users', string='Sales person')

    @api.onchange('leads_source', 'lead_owner', 'name', 'email_address', 'phone_number', 'phone_number_second', 'place',
                  'district', 'course_id', 'lead_qualification', 'last_studied_course', 'probability', 'leads_assign',
                  'admission_status', 'lead_quality', 'sales_person_id')
    def onchange_fields_dates(self):
        for i in self:
            i.last_update_date = fields.Datetime.now()

    def cancel_lead(self):
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


class LeadsSources(models.Model):
    _name = 'leads.sources'
    _inherit = 'mail.thread'
    _description = 'Leads Sources'

    name = fields.Char('Name', required=True)


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

    assigned_to = fields.Many2one('hr.employee', string='Assigned To')

    def action_done(self):
        # abc = self.env['leads.logic'].sudo().update({
        #     'lead_owner': self.assigned_to
        # })
        print(self._context['parent_obj'], 'current rec')

        aa = self.env['leads.logic'].search([])
        for i in aa:
            if i.id in self._context['parent_obj']:
                i.leads_assign = self.assigned_to
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
