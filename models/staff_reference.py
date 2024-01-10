from odoo import models, fields, api, _


class StaffReferenceLeads(models.Model):
    _name = "staff.reference.leads"
    _description = "Staff Reference Leads"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'display_name'

    lead_name = fields.Char('Name', required=True)
    lead_source_id = fields.Many2one('leads.sources', 'Lead Source', domain="[('name', '=', 'Logic Staff')]",
                                     required=1)
    email_address = fields.Char(string='Email Address')
    phone_number = fields.Char(string='Mobile Number', required=True)
    country = fields.Selection(
        [('india', 'India'), ('germany', 'Germany'), ('canada', 'Canada'), ('usa', 'USA'), ('australia', 'Australia'),
         ('italy', 'Italy'), ('france', 'France'), ('united_kingdom', 'United Kingdom'),
         ('saudi_arabia', 'Saudi Arabia'), ('ukraine', 'Ukraine'), ('united_arab_emirates', 'United Arab Emirates'),
         ('china', 'China'), ('japan', 'Japan'), ('singapore', 'Singapore'), ('indonesia', 'Indonesia'),
         ('russia', 'Russia'), ('oman', 'Oman'), ('nepal', 'Nepal'), ('japan', 'Japan')],
        string='Country', default='india')
    district = fields.Selection([('wayanad', 'Wayanad'), ('ernakulam', 'Ernakulam'), ('kollam', 'Kollam'),
                                 ('thiruvananthapuram', 'Thiruvananthapuram'), ('kottayam', 'Kottayam'),
                                 ('kozhikode', 'Kozhikode'), ('palakkad', 'Palakkad'), ('kannur', 'Kannur'),
                                 ('alappuzha', 'Alappuzha'), ('malappuram', 'Malappuram'), ('kasaragod', 'Kasaragod'),
                                 ('thrissur', 'Thrissur'), ('idukki', 'Idukki'), ('pathanamthitta', 'Pathanamthitta'),
                                 ('abroad', 'Abroad'), ('other', 'Other'), ('nil', 'Nil')],
                                string='District', required=True)
    place = fields.Char('Place')
    course_id = fields.Many2one('logic.base.courses', string='Preferred Course', required=1)
    branch_id = fields.Many2one('logic.base.branches', string='Branch', required=1)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string='State', default='draft',
                             tracking=True)

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.lead_name + '-' + record.phone_number

    def action_add_lead(self):
        lead = self.env['leads.logic'].sudo().create({
            'name': self.lead_name,
            'leads_source': self.lead_source_id.id,
            'email_address': self.email_address,
            'phone_number': self.phone_number,
            'country': self.country,
            'district': self.district,
            'place': self.place,
            'base_course_id': self.course_id.id,
            'branch': self.branch_id.id,
            'lead_quality': 'nil',
            'lead_status': 'nil',
            'lead_referral_staff_id': self.create_uid.id,
            'lead_owner': self.create_uid.employee_id.id,
            'mode_of_study': 'nil',
        })
        self.write({'state': 'confirm'})
        print('action add lead')
