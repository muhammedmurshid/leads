from odoo import models, fields, api


class PipelineModel(models.Model):
    _name = 'logic.leads.pipeline'


class LeadReport(models.TransientModel):
    _name = 'lead.report'

    date_from = fields.Date(string="From Date", required=True, placeholder="Report From Date")
    to_date = fields.Date(string="To Date" , required=True, placeholder="Report To Date")
    datas_ids = fields.Many2many('leads.logic', string="Data")

    @api.onchange('date_from', 'to_date')
    def _onchange_inbetween_date(self):
        print(self.date_from, self.to_date, 'date')
        leads = self.env['leads.logic'].sudo().search([('date_of_adding', '>=', self.date_from), ('date_of_adding', '<=', self.to_date)])
        print(leads, 'datas')
        self.datas_ids = leads.ids


    def get_report_lines(self):
        invoice_list = []
        counts = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_source = self.env['leads.sources'].sudo().search([])

        total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot')])
        total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids)])

        for j in lead_source:
            hot_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot')])
            cold_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold')])
            bad_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead')])
            nil_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil')])
            warm_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm')])
            total_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id)])
            if total_count == 0:
                perc_total = 0
            else:
                perc_total = round((total_count / total_leads) * 100)

            line = {'lead_source': j.name,
                    'hot_count': hot_count,
                    'cold_count': cold_count,
                    'bad_count': bad_count,
                    'nil_count': nil_count,
                    'warm_count': warm_count,
                    'total_count': total_count,
                    'total_hot': total_hot,

                    'perc_total': perc_total
                    }
            invoice_list.append(line)


        # for i in hos:
        #     if i.id in datas:
        #         print(i.name, 'uu')
        #         if i:
        #             line = {'hostel_name': i.name,
        #                     'hostel_rent': i.common_rent,
        #                     'hostel_type': i.type,
        #                     'hostel_contact': i.contact_number,
        #                     'hostel_location': i.location,
        #                     'hostel_gender': i.hostel_type,
        #                     'hostel_status': i.status
        #                     }
        #             invoice_list.append(line)
        return invoice_list

    def print_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def print_xlsx_report_course(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_course/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_course_reports(self):
        invoice_list = []
        counts = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_course = self.env['logic.base.courses'].sudo().search([])

        # total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot')])
        # total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids)])

        for j in lead_course:
            print
            # hot_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot')])
            # cold_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold')])
            # bad_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead')])
            # nil_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil')])
            # warm_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm')])
            total_count = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('leads_source', '=', j.id)])
            # if total_count == 0:
            #     perc_total = 0
            # else:
            #     perc_total = round((total_count / total_leads) * 100)

            line = {'lead_course': j.name,

                    }
            invoice_list.append(line)
        return invoice_list
