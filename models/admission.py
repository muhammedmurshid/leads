from odoo import models, fields, api, _
import datetime


class AddToStudentList(models.TransientModel):
    _name = 'add.to.student.list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_name'

    student_name = fields.Char(string="Student Name")
    batch_id = fields.Many2one('logic.base.batch', string="Batch", domain=[('state', '=', 'done')])
    mobile_number = fields.Char(string="Mobile Number")
    email = fields.Char(string="Email")
    current_rec = fields.Many2one('leads.logic', string="Current Record")
    admission_officer = fields.Many2one('res.users', string="Admission Officer", default=lambda self: self.env.user.id)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender")
    mode_of_study = fields.Selection([('online', 'Online'), ('offline', 'Offline')], string="Mode of Study")
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=?', country)]")
    country = fields.Many2one('res.country')
    date_of_birth = fields.Date()

    def action_create_student(self):
        self.current_rec.admission_status = True
        today = datetime.date.today()

        year = today.year
        next_year = year + 1
        next_year_last_two_digits = next_year % 100

        student = self.env['logic.students'].sudo().create({
            'name': self.student_name,
            'batch_id': self.batch_id.id,
            'phone_number': self.mobile_number,
            'email': self.email,
            'gender': self.gender,
            'mode_of_study': self.mode_of_study,
            'admission_officer': self.admission_officer.id,

            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state': self.state.id,
            'country': self.country.id,
            'dob': self.date_of_birth,

            # 'pending_amount': self.pending_adm_fee,

            # 'adm_fee_due_amount': self.due_amount,
        })

        stud_id = self.env['logic.students'].search([])[-1].id
        self.current_rec.student_id = stud_id

        fee = self.env['admission.fee.collection'].sudo().create({
            'name': stud_id,
            'batch_id': self.batch_id.id,
            'mobile_number': self.mobile_number,
            'email': self.email,
            # 'mode_of_study': self.mode_of_study,


            'admission_officer_id': self.admission_officer.id,

            'invoice_date': fields.Date.today(),

        })
        fee_id = self.env['admission.fee.collection'].search([])[-1].id
        fee = self.env['admission.fee.collection'].browse(fee_id)
        print(fee.name.name, 'fee name')
        print(fee_id, 'fee id')
        self.current_rec.adm_id = fee_id
        # fee.state = 'paid'
        view_id = self.env.ref('fee_collection.model_admission_fee_collection_form_view').id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Fee Receipt',
            'view_mode': 'tree,form',
            'res_model': 'admission.fee.collection',
            'domain': [('id', '=', fee_id)],

            'context': "{'create': False}"
        }
