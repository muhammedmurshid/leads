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
    admission_fee = fields.Float(string="Admission Fee", compute='_compute_batch_admission_fee', store=True)
    paid_amount = fields.Float(string="Paid Amount")
    due_amount = fields.Float(string="Due Amount", compute='_compute_due_amount', store=True)
    total_fee = fields.Float(string="Total Fee", related='batch_id.batch_fee')
    payment_mode = fields.Selection([('cash', 'Cash'), ('online', 'Online'), ('cheque', 'Cheque')], default='online',
                                    string="Payment Mode")
    pending_adm_fee = fields.Char(string="Pending Admission Fee", compute='_compute_pending_adm_fee', store=True)
    admission_id = fields.Char(string="Admission ID")
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    @api.depends('due_amount')
    def _compute_pending_adm_fee(self):
        for record in self:
            record.pending_adm_fee = ' ' + ':' + ' ' + str(record.due_amount) + ' ' + 'Pending'

    @api.depends('paid_amount', 'admission_fee')
    def _compute_due_amount(self):
        for record in self:
            record.due_amount = record.admission_fee - record.paid_amount

    @api.depends('batch_id')
    def _compute_batch_admission_fee(self):
        for record in self:
            record.admission_fee = record.batch_id.admission_fee

    def action_create_student(self):

        # student = self.env['logic.students'].sudo().create({
        #     'name': self.student_name,
        #     'batch_id': self.batch_id.id,
        #     'phone_number': self.mobile_number,
        #     'email': self.email,
        #     'gender': self.gender,
        #     'mode_of_study': self.mode_of_study,
        #     'admission_officer': self.admission_officer.id,
        #     'admission_fee': self.admission_fee,
        #     'pending_amount': self.pending_adm_fee,
        #     'total_fee': self.total_fee
        # })

        self.current_rec.admission_status = True
        today = datetime.date.today()

        year = today.year
        next_year = year + 1
        next_year_last_two_digits = next_year % 100

        # record.payment_reference = 'JK' + '-' + current_year
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fee Receipt',
            'res_model': 'admission.fee.receipt',

            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_email': self.email, 'default_student_name': self.student_name,
                        'default_mobile_number': self.mobile_number, 'default_batch_id': self.batch_id.id,
                        'default_paid_amount': self.paid_amount, 'default_admission_fee': self.admission_fee,
                        'default_invoice_date': fields.Date.today(),
                        'default_payment_reference': 'JK' + '-' + str(year) + '-' + str(
                            next_year_last_two_digits) + '/' + str(100), 'default_payment_mode': self.payment_mode,
                        'default_admission_id': self.admission_id}

        }


class PrintAdmissionFeeReceiptStudent(models.TransientModel):
    _name = 'admission.fee.receipt'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    student_name = fields.Char(string="Student Name", readonly=True)
    batch_id = fields.Many2one('logic.base.batch', string="Batch", domain=[('state', '=', 'done')], readonly=True)
    mobile_number = fields.Char(string="Mobile Number", readonly=True)
    email = fields.Char(string="Email", readonly=True)
    payment_mode = fields.Selection([('cash', 'Cash'), ('online', 'Online'), ('cheque', 'Cheque')], default='online',
                                    string="Payment Mode")
    admission_id = fields.Char(string="Admission ID", readonly=True)
    admission_officer = fields.Many2one('res.users', string="Admission Officer", default=lambda self: self.env.user.id,
                                        readonly=True)
    admission_fee = fields.Float(string="Admission Fee", compute='_compute_batch_admission_fee', store=True,
                                 readonly=True)
    invoice_date = fields.Date(string="Invoice Date")
    paid_amount = fields.Float(string="Paid Amount", readonly=True)
    payment_reference = fields.Char(string="Payment Reference")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)

    def action_print_receipt(self):
        return self.env.ref(
            'leads.admission_fee_template_report').report_action(self)

    def _compute_total_amount_in_words(self, doc):
        # INR = self.env['res.currency'].search([('name', '=', 'INR')])
        for move in doc:
            if move.paid_amount:
                total = move.paid_amount
                y = move.currency_id.amount_to_text(total)
                return str(y)

    @api.model
    def get_current_year(self):
        for record in self:
            current_date = fields.Date.today()
            current_year = current_date.year
            record.payment_reference = 'JK' + '-' + current_year
