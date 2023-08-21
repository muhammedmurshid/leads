from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LeadsForm(models.Model):
    _name = 'leads.logic'
    _inherit = 'mail.thread'

    leads_source = fields.Many2one('leads.sources', string='Leads source', required=True)
    name = fields.Char(string='Name')
    email_address = fields.Char(string='Email address')
    phone_number = fields.Char(string='Mobile number', required=True, copy=False)
    probability = fields.Float(string='Probability')
    admission_status = fields.Boolean(string='Admission')
    date_of_adding = fields.Date(string='Date of adding', default=fields.Date.today())
    last_update_date = fields.Date(string='Last updated date', default=fields.Date.today())
    course_id = fields.Char(string='Course')
    lead_quality = fields.Selection([('good', 'Good'), ('bad', 'Bad')], string='Lead quality')
    place = fields.Char('Place')
    leads_assign = fields.Many2one('res.users', string='Assign to')
    lead_owner = fields.Many2one('hr.employee', string='Lead owner')
    seminar_lead_id = fields.Integer()
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('crm', 'Added Crm'), ('cancel', 'Cancelled')], string='State',
        default='draft')
    last_studied_course = fields.Char(string='Last studied course')
    _sql_constraints = [
        ('unique_phone_number', 'UNIQUE(phone_number)', 'Duplicate record based on creation time!'),
    ]
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
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki')], string='District')

    @api.model
    def create(self, vals):
        existing_record = self.search([('phone_number', '=', vals.get('phone_number'))])
        if existing_record:
            # Handle the duplicate record, e.g., raise an error
            raise ValidationError('A record with the same mobile number already exists!')
        return super(LeadsForm, self).create(vals)

    def confirm(self):
        self.state = 'confirm'

    @api.onchange('admission_status')
    def _onchange_admission_status(self):
        print('hi')
        ss = self.env['seminar.students'].search([])
        for rec in ss:
            if self.admission_status == True:
                if self.seminar_lead_id == rec.id:
                    rec.admission_status = 'yes'

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


class LeadsSources(models.Model):
    _name = 'leads.sources'
    _inherit = 'mail.thread'

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
