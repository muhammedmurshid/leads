from odoo import models, fields, api


class ChannelNameWizard(models.TransientModel):
    _name = 'channel.name.wizard'

    channel_name = fields.Char('Channel Name')

    def action_launch(self):
        print(self._context['parent_obj'], 'current rec')
        leads = self.env['leads.logic'].search([])
        for record in leads:
            if record.id in self._context['parent_obj']:
                record.lead_channel = self.channel_name
                # print(self.channel_name, 'channel name')
                # print(record.lead_channel, 'channel name record')


