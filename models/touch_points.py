from odoo import fields, models, _


class LeadsTouchPoints(models.Model):
    _name = 'leads.touch.points'
    _description = 'Touch Point'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')

