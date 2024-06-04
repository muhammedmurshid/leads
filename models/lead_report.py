from odoo import models, fields, api


class PipelineModel(models.Model):
    _name = 'logic.leads.pipeline'


class LeadReport(models.TransientModel):
    _name = 'lead.report'

    date_from = fields.Date(string="From Date", required=True, placeholder="Report From Date")
    to_date = fields.Date(string="To Date", required=True, placeholder="Report To Date")
    datas_ids = fields.Many2many('leads.logic', string="Data")
    report_admission = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Admission Report', default='yes')
    report_type = fields.Selection([('fully_report', 'Full Report'), ('only_crash', 'Crash Report'), ('without_crash', 'Without Crash')], default='fully_report')

    @api.onchange('date_from', 'to_date', 'report_admission', 'report_type')
    def _onchange_inbetween_date(self):
        self.datas_ids = False
        print(self.date_from, self.to_date, 'date')
        if self.report_admission == 'yes':
            if self.report_type == 'fully_report':
                leads = self.env['leads.logic'].sudo().search(
                    [('admission_date', '>=', self.date_from), ('admission_date', '<=', self.to_date),
                     ('admission_status', '=', True)])
                self.datas_ids = leads.ids
            if self.report_type == 'without_crash':
                leads = self.env['leads.logic'].sudo().search(
                    [('admission_date', '>=', self.date_from), ('admission_date', '<=', self.to_date),
                     ('admission_status', '=', True), ('course_type', '!=', 'crash')])
                self.datas_ids = leads.ids
            if self.report_type == 'only_crash':
                leads = self.env['leads.logic'].sudo().search(
                    [('admission_date', '>=', self.date_from), ('admission_date', '<=', self.to_date),
                     ('admission_status', '=', True), ('course_type', '=', 'crash')])
                self.datas_ids = leads.ids
        else:
            if self.report_type == 'fully_report':
                leads = self.env['leads.logic'].sudo().search(
                    [('date_of_adding', '>=', self.date_from), ('date_of_adding', '<=', self.to_date)])
                print(leads, 'datas')
                self.datas_ids = leads.ids
            if self.report_type == 'without_crash':
                leads = self.env['leads.logic'].sudo().search(
                    [('date_of_adding', '>=', self.date_from), ('date_of_adding', '<=', self.to_date),
                     ('course_type', '!=', 'crash')])
                self.datas_ids = leads.ids
            if self.report_type == 'only_crash':
                leads = self.env['leads.logic'].sudo().search(
                    [('date_of_adding', '>=', self.date_from), ('date_of_adding', '<=', self.to_date),
                     ('course_type', '=', 'crash')])
                self.datas_ids = leads.ids

    def get_report_lines(self):
        invoice_list = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_source = self.env['leads.sources'].sudo().search([])

        total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot')])
        total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '!=', False)])
        admission = self.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True)])

        for j in lead_source:
            hot_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot')])
            cold_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold')])
            bad_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead')])
            nil_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil')])
            warm_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm')])
            total_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '!=', False)])
            hot_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'), ('admission_status', '=', True)])
            cold_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'), ('admission_status', '=', True)])
            bad_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'), ('admission_status', '=', True)])
            nil_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'), ('admission_status', '=', True)]
            )
            warm_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'), ('admission_status', '=', True)]
            )
            adm_source = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('admission_status', '=', True)]
            )

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
                    'hot_adm': hot_adm,
                    'cold_adm': cold_adm,
                    'bad_adm': bad_adm,
                    'nil_adm': nil_adm,
                    'warm_adm': warm_adm,
                    'adm_source': adm_source,
                    'perc_total': perc_total
                    }
            invoice_list.append(line)
        return invoice_list

    def print_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_digital_report_lines(self):
        invoice_list = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_source = self.env['leads.sources'].sudo().search([('digital_lead', '=', True)])

        total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot')])
        total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '!=', False)])
        admission = self.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True)])

        for j in lead_source:
            hot_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot')])
            cold_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold')])
            bad_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead')])
            nil_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil')])
            warm_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm')])
            total_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '!=', False)])
            hot_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'), ('admission_status', '=', True)])
            cold_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'), ('admission_status', '=', True)])
            bad_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'), ('admission_status', '=', True)])
            nil_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'), ('admission_status', '=', True)]
            )
            warm_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'), ('admission_status', '=', True)]
            )
            adm_source = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('admission_status', '=', True)]
            )

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
                    'hot_adm': hot_adm,
                    'cold_adm': cold_adm,
                    'bad_adm': bad_adm,
                    'nil_adm': nil_adm,
                    'warm_adm': warm_adm,
                    'adm_source': adm_source,
                    'perc_total': perc_total
                    }
            invoice_list.append(line)
        return invoice_list

    def print_xlsx_digital_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/digital_lead_report/excel_report/%s' % (self.id),
            'target': 'new',
        }



    def get_course_reports(self):
        invoice_list = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_course = self.env['logic.base.courses'].sudo().search([('state', '=', 'done')])
        lead_source = self.env['leads.sources'].sudo().search([])

        for j in lead_course:
            source_id = lead_source.ids
            print(source_id, 'uuu')
            line = {'lead_course': j.name,
                    'course_id': j.id,
                    'count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id)]),
                    'source_count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id),
                         ('leads_source', 'in', lead_source.ids)]),
                    'prc_count': round((self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id),
                         ('leads_source', 'in', lead_source.ids)]) / self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids)])) * 100),
                    'adm_count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id),
                         ('leads_source', 'in', lead_source.ids),('admission_status', '=', True)])
                    }
            invoice_list.append(line)

        return invoice_list

    def print_xlsx_report_course(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_course/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_without_crash_report_lines(self):
        invoice_list = []
        counts = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_source = self.env['leads.sources'].sudo().search([])

        total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot'), ('course_type', '!=', 'crash')])
        total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('course_type', '!=', 'crash'),('lead_quality', '!=', False)])
        admission = self.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '!=', 'crash')])

        for j in lead_source:
            hot_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),('course_type', '!=', 'crash')])
            cold_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),('course_type', '!=', 'crash')])
            bad_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),('course_type', '!=', 'crash')])
            nil_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),('course_type', '!=', 'crash')])
            warm_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),('course_type', '!=', 'crash')])
            total_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id),('course_type', '!=', 'crash'),('lead_quality', '!=', False)])
            hot_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')])
            cold_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')])
            bad_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')])
            nil_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')]
            )
            warm_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')]
            )
            adm_source = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('admission_status', '=', True),('course_type', '!=', 'crash')]
            )

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
                    'hot_adm': hot_adm,
                    'cold_adm': cold_adm,
                    'bad_adm': bad_adm,
                    'nil_adm': nil_adm,
                    'warm_adm': warm_adm,
                    'adm_source': adm_source,
                    'perc_total': perc_total
                    }
            invoice_list.append(line)

        return invoice_list

    def print_without_crash_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_without_crash/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_without_digital_crash_report_lines(self):
        invoice_list = []
        counts = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_source = self.env['leads.sources'].sudo().search([('digital_lead', '=', True)])

        total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot'), ('course_type', '!=', 'crash')])
        total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('course_type', '!=', 'crash'),('lead_quality', '!=', False),('leads_source', 'in', lead_source.ids)])
        admission = self.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '!=', 'crash')])

        for j in lead_source:
            hot_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),('course_type', '!=', 'crash')])
            cold_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),('course_type', '!=', 'crash')])
            bad_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),('course_type', '!=', 'crash')])
            nil_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),('course_type', '!=', 'crash')])
            warm_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),('course_type', '!=', 'crash')])
            total_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id),('course_type', '!=', 'crash'),('lead_quality', '!=', False)])
            hot_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')])
            cold_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')])
            bad_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')])
            nil_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')]
            )
            warm_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),
                 ('admission_status', '=', True),('course_type', '!=', 'crash')]
            )
            adm_source = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('admission_status', '=', True),('course_type', '!=', 'crash')]
            )

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
                    'hot_adm': hot_adm,
                    'cold_adm': cold_adm,
                    'bad_adm': bad_adm,
                    'nil_adm': nil_adm,
                    'warm_adm': warm_adm,
                    'adm_source': adm_source,
                    'perc_total': perc_total
                    }
            invoice_list.append(line)

        return invoice_list

    def print_without_crash_digital_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_digital_without_crash/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_with_out_crash_course_reports(self):
        invoice_list = []
        lead_sources = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_course = self.env['logic.base.courses'].sudo().search([('state', '=', 'done')])
        lead_source = self.env['leads.sources'].sudo().search([])

        for j in lead_course:
            source_id = lead_source.ids
            print(source_id, 'uuu')
            line = {'lead_course': j.name,
                    'course_id': j.id,
                    'count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id), ('course_type', '!=', 'crash')]),
                    'source_count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id),
                         ('leads_source', 'in', lead_source.ids), ('course_type', '!=', 'crash')]),
                    'prc_count': round((self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id), ('course_type', '!=', 'crash'),
                         ('leads_source', 'in', lead_source.ids)]) / self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids)])) * 100),
                    'adm_count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id),
                         ('leads_source', 'in', lead_source.ids),('admission_status', '=', True),('course_type', '!=', 'crash')])
                    }
            invoice_list.append(line)

        return invoice_list

    def print_xlsx_without_crash_report_course(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_without_crash_course/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_crash_course_reports(self):
        invoice_list = []
        lead_sources = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_course = self.env['logic.base.courses'].sudo().search([('state', '=', 'done')])
        lead_source = self.env['leads.sources'].sudo().search([])

        for j in lead_course:
            source_id = lead_source.ids
            print(source_id, 'uuu')
            line = {'lead_course': j.name,
                    'course_id': j.id,
                    'count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id), ('course_type', '=', 'crash')]),
                    'source_count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id),
                         ('leads_source', 'in', lead_source.ids), ('course_type', '=', 'crash')]),
                    'prc_count': round((self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id), ('course_type', '=', 'crash'),
                         ('leads_source', 'in', lead_source.ids)]) / self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids)])) * 100),
                    'adm_count': self.env['leads.logic'].sudo().search_count(
                        [('id', 'in', datas.ids), ('base_course_id', '=', j.id),
                         ('leads_source', 'in', lead_source.ids),('admission_status', '=', True),('course_type', '=', 'crash')])
                    }
            invoice_list.append(line)

        return invoice_list

    def print_xlsx_crash_report_course(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_crash_course/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_crash_report_lines(self):
        invoice_list = []
        counts = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_source = self.env['leads.sources'].sudo().search([])

        total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot'), ('course_type', '=', 'crash')])
        total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('course_type', '=', 'crash'),('lead_quality', '!=', False)])
        admission = self.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash')])

        for j in lead_source:
            hot_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash')])
            cold_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash')])
            bad_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash')])
            nil_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash')])
            warm_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash')])
            total_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id),('course_type', '=', 'crash')])
            hot_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')])
            cold_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')])
            bad_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')])
            nil_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')]
            )
            warm_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')]
            )
            adm_source = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('admission_status', '=', True),('course_type', '=', 'crash')]
            )

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
                    'hot_adm': hot_adm,
                    'cold_adm': cold_adm,
                    'bad_adm': bad_adm,
                    'nil_adm': nil_adm,
                    'warm_adm': warm_adm,
                    'adm_source': adm_source,
                    'perc_total': perc_total
                    }
            invoice_list.append(line)

        return invoice_list

    def print_crash_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_source_crash/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def get_crash_digital_report_lines(self):
        invoice_list = []
        counts = []

        # hostel_ids = self.hostel_id.ids
        datas = self.datas_ids
        lead_source = self.env['leads.sources'].sudo().search([('digital_lead', '=', True)])

        total_hot = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot'), ('course_type', '=', 'crash')])
        total_leads = self.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('course_type', '=', 'crash')])
        admission = self.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash')])

        for j in lead_source:
            hot_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash')])
            cold_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash')])
            bad_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash')])
            nil_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash')])
            warm_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash')])
            total_count = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id),('course_type', '=', 'crash')])
            hot_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'hot'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')])
            cold_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'cold'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')])
            bad_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'bad_lead'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')])
            nil_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'nil'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')]
            )
            warm_adm = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('lead_quality', '=', 'warm'),
                 ('admission_status', '=', True),('course_type', '=', 'crash')]
            )
            adm_source = self.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', j.id), ('admission_status', '=', True),('course_type', '=', 'crash')]
            )

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
                    'hot_adm': hot_adm,
                    'cold_adm': cold_adm,
                    'bad_adm': bad_adm,
                    'nil_adm': nil_adm,
                    'warm_adm': warm_adm,
                    'adm_source': adm_source,
                    'perc_total': perc_total
                    }
            invoice_list.append(line)

        return invoice_list

    def print_crash_digital_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/lead_report_source_crash_digital/excel_report/%s' % (self.id),
            'target': 'new',
        }
