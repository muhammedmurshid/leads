from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class AddToStudentList(models.TransientModel):
    _name = 'add.to.student.list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_name'

    student_name = fields.Char(string="Student Name")
    mobile_number = fields.Char(string="Mobile Number")
    email = fields.Char(string="Email")
    type = fields.Selection(
        [('new_admission', 'New Admission'), ('already_taken_admission', 'Already Taken Admission')], string="Type",
        required=1, default='new_admission')
    student_id = fields.Many2one('logic.students', string="Student")
    academic_year = fields.Selection([('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'), ('2026', '2026'), ('nil', 'Nil')], string='Academic Year', required=True)
    current_rec = fields.Many2one('leads.logic', string="Current Record")
    admission_officer = fields.Many2one('res.users', string="Admission Officer", default=lambda self: self.env.user.id)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender")
    mode_of_study = fields.Selection([('online', 'Online'), ('offline', 'Offline'), ('nil', 'Nil')],
                                     string="Mode of Study", required=1)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=?', country)]")
    country = fields.Many2one('res.country')
    course_id = fields.Many2one('logic.base.courses', string="Course")
    branch_id = fields.Many2one('logic.base.branches', string="Branch")
    course_level_id = fields.Many2one('course.levels', string="Course Level")
    course_group_id = fields.Many2one('course.groups', string="Course Group")
    course_papers_ids = fields.Many2many('course.papers', string="Course Papers")
    date_of_birth = fields.Date()
    course_type = fields.Selection(
        [('indian', 'Indian'), ('international', 'International'), ('crash', 'Crash'), ('nil', 'Nil')],
        string="Course Type")
    admission_date = fields.Date(string="Admission Date", default=fields.Date.context_today, required=1, readonly=1)

    @api.onchange('academic_year', 'branch_id')
    def academic_year_based_batches(self):
        self.batch_id = False
        if self.academic_year:
            batch = self.env['logic.base.batch'].sudo().search([('academic_year', '=', self.academic_year),('state', '=', 'done')])
            batches = []
            batches.clear()
            for i in batch:
                print(i.name, 'batch')
                if i.branch_id.id == self.branch_id.id:
                    batches.append(i.id)
            domain = [('id', 'in', batches)]
            print(domain, 'domain')
            print(batches, 'batches')

            return {'domain': {'batch_id': domain}}

    batch_id = fields.Many2one('logic.base.batch', string="Batch", domain=academic_year_based_batches)

    def action_create_student(self):
        seminar_lead = self.env['seminar.students'].sudo().search([('seminar_id', '=', self.current_rec.seminar_id)])
        for i in seminar_lead:
            if i.contact_number == self.mobile_number:
                # print(i.contact_number, 'a')
                i.sudo().update({
                    'admission_status': 'yes',
                })

        today = datetime.date.today()

        year = today.year
        next_year = year + 1
        next_year_last_two_digits = next_year % 100

        if self.type == 'new_admission':
            print('no student')
            self.current_rec.admission_status = True
            self.current_rec.state = 'done'
            self.current_rec.over_due = False
            self.current_rec.admission_date = self.admission_date
            student = self.env['logic.students'].sudo().create({
                'name': self.student_name,
                'batch_id': self.batch_id.id,
                'phone_number': self.mobile_number,
                'email': self.email,
                'gender': self.gender,
                'admission_date': self.admission_date,
                'mode_of_study': self.mode_of_study,
                'admission_officer': self.admission_officer.id,

                'street': self.street,
                'street2': self.street2,
                'zip': self.zip,
                'city': self.city,
                'state': self.state.id,
                'country': self.country.id,
                'dob': self.date_of_birth,
                'lead_id': self.current_rec.id,
                'std_adm_detail_ids': [(0, 0, {
                    'batch_id': self.batch_id.id,
                    'course_id': self.course_id.id,
                    'branch_id': self.branch_id.id,
                    'course_level_id': self.course_level_id.id,
                    'course_group_id': self.course_group_id.id,
                    'course_papers_ids': [(6, 0, self.course_papers_ids.ids)],

                })]
            })

            stud_id = self.env['logic.students'].search([])[-1].id
            self.current_rec.student_id = stud_id
            if self.course_type == 'crash':
                fee = self.env['admission.fee.collection'].sudo().create({
                    'name': stud_id,
                    'batch_id': self.batch_id.id,
                    'mobile_number': self.mobile_number,
                    'email': self.email,
                    # 'mode_of_study': self.mode_of_study,
                    'admission_officer_id': self.admission_officer.id,
                    'invoice_date': fields.Date.today(),
                    'admission_fee': 0,
                    'lead_id': self.current_rec.id,
                    'admission_date': self.admission_date,

                })
                fee_id = self.env['admission.fee.collection'].search([])[-1].id
                fee = self.env['admission.fee.collection'].browse(fee_id)
                fee.state = 'paid'
            else:

                fee = self.env['admission.fee.collection'].sudo().create({
                    'name': stud_id,
                    'batch_id': self.batch_id.id,
                    'mobile_number': self.mobile_number,
                    'email': self.email,
                    'admission_officer_id': self.admission_officer.id,
                    'invoice_date': fields.Date.today(),
                    'lead_id': self.current_rec.id,
                    'admission_date': self.admission_date,

                })
                fee_id = self.env['admission.fee.collection'].search([])[-1].id
                fee = self.env['admission.fee.collection'].browse(fee_id)
                print(fee.name.name, 'fee name')
                print(fee_id, 'fee id')
                self.current_rec.adm_id = fee_id

            return {
                'type': 'ir.actions.act_window',
                'name': 'Fee Receipt',
                'view_mode': 'tree,form',
                'res_model': 'admission.fee.collection',
                'domain': [('id', '=', fee_id)],

                'context': "{'create': False}"
            }
        else:
            print('yo yo')
            if self.student_id.adm_fee_due_amount == 0 and self.student_id.course_due_amount == 0:
                if self.student_id.admission_date:
                    self.current_rec.admission_date = self.admission_date
                    one_year = self.student_id.admission_date + relativedelta(years=1)
                    print(one_year, 'one year')
                    if one_year > today:
                        print('you are not eligible')
                        fee = self.env['admission.fee.collection'].sudo().create({
                            'name': self.student_id.id,
                            'batch_id': self.batch_id.id,
                            'mobile_number': self.mobile_number,
                            'email': self.email,
                            # 'mode_of_study': self.mode_of_study,
                            'admission_officer_id': self.admission_officer.id,
                            'invoice_date': fields.Date.today(),
                            'admission_date': self.admission_date,
                            'admission_fee': 0,
                            'lead_id': self.current_rec.id,

                        })

                        fee_id = self.env['admission.fee.collection'].search([])[-1].id
                        fee = self.env['admission.fee.collection'].browse(fee_id)
                        fee.state = 'paid'
                        fee.name.admission_date = today
                        fee.name.update({
                            'std_adm_detail_ids': [(0, 0, {
                                'batch_id': self.batch_id.id,
                                'course_id': self.course_id.id,
                                'branch_id': self.branch_id.id,
                                'course_level_id': self.course_level_id.id,
                                'course_group_id': self.course_group_id.id,
                                'course_papers_ids': [(6, 0, self.course_papers_ids.ids)],

                            })]
                        })
                        fee.name.admission_officer = self.admission_officer.id
                        fee.name.batch_id = self.batch_id.id
                        fee.name.mode_of_study = self.mode_of_study
                        # fee = self.env['admission.fee.collection'].sudo().create({
                        #     'name': self.student_id.id,
                        #     'batch_id': self.batch_id.id,
                        #     'mobile_number': self.mobile_number,
                        #     'email': self.email,
                        #     # 'mode_of_study': self.mode_of_study,
                        #     'admission_officer_id': self.admission_officer.id,
                        #     'invoice_date': fields.Date.today(),
                        #     'lead_id': self.current_rec.id
                        #
                        # })
                        #
                        # fee_id = self.env['admission.fee.collection'].search([])[-1].id
                        # fee = self.env['admission.fee.collection'].browse(fee_id)
                        # print(fee.name.name, 'fee name')
                        # print(fee_id, 'fee id')
                        # self.current_rec.adm_id = fee_id
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Fee Receipt',
                            'view_mode': 'tree,form',
                            'res_model': 'admission.fee.collection',
                            'domain': [('id', '=', fee_id)],
                            'context': "{'create': False}"
                        }

                    else:
                        if self.course_type == 'crash':
                            fee = self.env['admission.fee.collection'].sudo().create({
                                'name': self.student_id.id,
                                'batch_id': self.batch_id.id,
                                'mobile_number': self.mobile_number,
                                'email': self.email,
                                # 'mode_of_study': self.mode_of_study,
                                'admission_officer_id': self.admission_officer.id,
                                'invoice_date': fields.Date.today(),
                                'admission_fee': 0,
                                'lead_id': self.current_rec.id,
                                'admission_date': self.admission_date,

                            })
                            self.student_id.batch_id = self.batch_id

                            fee_id = self.env['admission.fee.collection'].search([])[-1].id
                            fee = self.env['admission.fee.collection'].browse(fee_id)
                            fee.state = 'paid'
                        else:
                            print('sec work')
                            fee = self.env['admission.fee.collection'].sudo().create({
                                'name': self.student_id.id,
                                'batch_id': self.batch_id.id,
                                'mobile_number': self.mobile_number,
                                'email': self.email,
                                # 'mode_of_study': self.mode_of_study,
                                'admission_officer_id': self.admission_officer.id,
                                'invoice_date': fields.Date.today(),
                                'lead_id': self.current_rec.id,
                                'admission_date': self.admission_date,

                            })
                            self.student_id.batch_id = self.batch_id
                            self.student_id.admission_fee = self.batch_id.admission_fee
                            self.student_id.course_fee = self.batch_id.course_fee
                            self.student_id.admission_date = self.admission_date
                            self.student_id.paid_amount = 0
                            self.student_id.paid_course_fee = 0
                            self.student_id.update({
                                'std_adm_detail_ids': [(0, 0, {
                                    'batch_id': self.batch_id.id,
                                    'course_id': self.course_id.id,
                                    'branch_id': self.branch_id.id,
                                    'course_level_id': self.course_level_id.id,
                                    'course_group_id': self.course_group_id.id,
                                    'course_papers_ids': [(6, 0, self.course_papers_ids.ids)],

                                })]
                            })
                            fee_id = self.env['admission.fee.collection'].search([])[-1].id
                            fee = self.env['admission.fee.collection'].browse(fee_id)
                            print(fee.name.name, 'fee name')
                            print(fee_id, 'fee id')
                            self.current_rec.adm_id = fee_id

                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Fee Receipt',
                            'view_mode': 'tree,form',
                            'res_model': 'admission.fee.collection',
                            'domain': [('id', '=', fee_id)],
                            'context': "{'create': False}"
                        }
                else:
                    print('not working')
            else:

                raise UserError(
                    _('Pending payment for previous fees')
                )
