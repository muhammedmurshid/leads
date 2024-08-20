from odoo import fields, models, api, _


class BulkLeadSources(models.Model):
    _name = 'change.leads.sources'
    _description = 'Leads Sources'

    lead_source_id = fields.Many2one('leads.sources', string='Lead Source')
    leads = fields.Many2many('leads.logic', string='Leads')

    def action_change_sources(self):
        for i in self.leads:
            i.leads_source = self.lead_source_id.id
