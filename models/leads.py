from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta


class LeadsForm(models.Model):
    _name = 'leads.logic'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Leads'
    _rec_name = 'name'

    leads_source = fields.Many2one('leads.sources', string='Leads Source', required=True)
    name = fields.Char(string='Lead Name', required=True)
    email_address = fields.Char(string='Email Address')
    phone_number = fields.Char(string='Mobile Number', required=True, copy=False)
    probability = fields.Float(string='Probability')
    admission_status = fields.Boolean(string='Admission')
    date_of_adding = fields.Date(string='Date of Adding', default=fields.Date.today())
    last_update_date = fields.Datetime(string='Last Updated Date', )
    course_id = fields.Char(string='Course', required=True)
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
    phone_number_second = fields.Char(string='Phone Number')
    sample = fields.Char(string='Sample', compute='get_phone_number_for_whatsapp', store=True)
    field_to_display = fields.Char(string='Field to Display')
    lead_channel = fields.Char(string='Lead Channel')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('crm', 'Added Crm'), ('cancel', 'Cancelled')], string='State',
        default='draft')
    last_studied_course = fields.Char(string='Last Studied Course')
    referred_by = fields.Selection([('staff', 'Staff'), ('student', 'Student'), ('other', 'Other')],
                                   string='Referred By')
    referred_by_id = fields.Many2one('hr.employee', string='Referred Person')
    referred_by_name = fields.Char(string='Referred Person')
    referred_by_number = fields.Char(string='Referred Person Number')
    batch_preference = fields.Char(string='Batch Preference')
    branch_id = fields.Many2one('logic.branches', string='Branch')
    # _sql_constraints = [
    #     ('unique_phone_number', 'UNIQUE(phone_number)', 'Duplicate record based on creation time!'),
    #     ('unique_phone_number_second', 'UNIQUE(phone_number_second)',
    #      'A record with the same mobile number already exists!' + 'unique_name'),
    # ]

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

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'leads.logic') or _('New')
        existing_record = self.search([('phone_number', '=', vals.get('phone_number'))])
        if existing_record:
            for record in existing_record:
                # Handle the duplicate record, e.g., raise an error
                raise ValidationError(
                    'A record with the same mobile number already exists! created by ' + record.create_uid.name)
        existing_record_second = self.search([('phone_number_second', '=', vals.get('phone_number_second'))])
        if existing_record_second:
            for rd in existing_record_second:
                if self.phone_number_second:
                    # Handle the duplicate record, e.g., raise an error
                    raise ValidationError(
                        'A record with the same mobile number already exists! created by ' + rd.create_uid.name)
        return super(LeadsForm, self).create(vals)

    def reset_to_draft(self):
        self.state = 'draft'

    # @api.onchange('branch_id')
    # def onchange_branch_id(self):
    #     # raise ValidationError(self.activity_ids)
    #     print(self.activity_ids, 'activity ids')
    #     print('d)

    @api.depends('sample')
    def _compute_display_value(self):
        for record in self:
            if record.sample:
                # Modify the display value as needed based on the original field's value
                modified_value = "Modified: "
                record.sample = modified_value

    @api.depends('phone_number')
    def get_phone_number_for_whatsapp(self):
        for rec in self:
            # modified_value = "Modified: "
            # rec.sample = 'modified_value'
            if rec.phone_number:
                self.sample = 'https://web.whatsapp.com/send?phone=' + rec.phone_number

    def whatsapp_click_button(self):
        for i in self:
            return {
                'type': 'ir.actions.act_url',
                'name': "Leads Whatsapp",
                'target': 'new',
                'url': i.sample,
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

    def confirm(self):
        for i in self.activity_ids:
            i.action_feedback(feedback='confirmed')
        self.state = 'confirm'

    # @api.onchange('admission_status')
    # def _onchange_admission_status(self):
    #     print('hi')
    #     ss = self.env['seminar.students'].search([])
    #     for rec in ss:
    #         if self.admission_status == True:
    #             if self.seminar_lead_id == rec.id:
    #                 rec.admission_status = 'yes'

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

    def leadcreation(self):
        if not self.sales_person_id:
            raise ValidationError('Please select sales person')
        elif not self.name:
            raise ValidationError('Please enter name')
        elif not self.email_address:
            raise ValidationError('Please enter email address')
        else:
            crm = self.env['crm.lead'].create({
                'student_name': self.name,
                # 'email_from': self.email_address,
                'phone': self.phone_number,
                'name': self.name,
                'user_id': self.sales_person_id.id,
            }
            )
            self.state = 'crm'

        print('hi')

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
