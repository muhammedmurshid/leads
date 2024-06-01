from odoo import http
from odoo.http import request
import xlsxwriter
import io
from odoo.http import request
from odoo.http import Controller, request, route, content_disposition


class LeadWithoutCrashDigitalExcelReportController(http.Controller):
    @http.route([
        '/lead_report_digital_without_crash/excel_report/<model("lead.report"):report_id>',
    ], type='http', auth="user", csrf=False)
    def get_without_crash_digital_report(self, report_id=None, **args):
        print(report_id, 'report_id')
        datas = report_id.datas_ids
        print(datas, 'date')

        total_hot = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'hot'), ('course_type', '!=', 'crash')])
        total_cold = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'cold'), ('course_type', '!=', 'crash')])
        total_warm = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '!=', 'crash')])
        total_nil = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '!=', 'crash')])
        total_bad = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '!=', 'crash')])
        total_leads = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('course_type', '!=', 'crash'), ('lead_quality', '!=', False)])
        total_adm = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('admission_status', '=', True),('course_type', '!=', 'crash')])
        adm_hot = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('admission_status', '=', True),('lead_quality', '=', 'hot'),('course_type', '!=', 'crash')])
        adm_cold = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('admission_status', '=', True),('lead_quality', '=', 'cold'),('course_type', '!=', 'crash')])
        adm_warm = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('admission_status', '=', True),('lead_quality', '=', 'warm'),('course_type', '!=', 'crash')])
        adm_nil = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('admission_status', '=', True),('lead_quality', '=', 'nil'),('course_type', '!=', 'crash')])
        adm_bad = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids),('admission_status', '=', True),('lead_quality', '=', 'bad_lead'),('course_type', '!=', 'crash')])

        if total_hot == 0:
            perc_hot = 0
        else:
            perc_hot = round((total_hot / total_leads) * 100)
        if total_cold == 0:
            perc_cold = 0
        else:
            perc_cold = round((total_cold / total_leads) * 100)
        if total_warm == 0:
            perc_warm = 0
        else:
            perc_warm = round((total_warm / total_leads) * 100)
        if total_nil == 0:
            perc_nil = 0
        else:
            perc_nil = round((total_nil / total_leads) * 100)
        if total_bad == 0:
            perc_bad = 0
        else:
            perc_bad = round((total_bad / total_leads) * 100)
        if total_leads == 0:
            perc_total = 0
        else:
            perc_total = round((total_leads / total_leads) * 100)

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Source Wise Report' + '.xlsx'))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': 'white',
            'bg_color': '#2C3E50',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        total_format = workbook.add_format({
            'font_color': 'black',
            'bg_color': '#d6ce5c',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        total_leads_format = workbook.add_format({
            'font_color': 'black',
            'bg_color': 'green',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        admission = workbook.add_format({
            'font_color': 'black',
            'bg_color': '#84f032',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        percentage = workbook.add_format({
            'font_color': 'black',
            'bg_color': '#f0a732',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        # get data for the report.
        report_lines = report_id.get_without_digital_crash_report_lines()
        # prepare excel sheet styles and formats
        sheet = workbook.add_worksheet("invoices")
        sheet.write(1, 0, 'No.', header_format)
        sheet.write(1, 1, 'Lead Source', header_format)
        sheet.write(1, 2, 'Hot', header_format)
        sheet.write(1, 3, 'Warm', header_format)
        sheet.write(1, 4, 'Cold', header_format)
        sheet.write(1, 5, 'Bad Lead', header_format)
        sheet.write(1, 6, 'Nil', header_format)
        sheet.write(1, 7, 'Admission', header_format)
        sheet.write(1, 8, 'Total', header_format)
        sheet.write(1, 9, 'Percentage %', header_format)

        row = 2
        number = 1
        # write the report lines to the excel document
        for line in report_lines:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, )
            sheet.write(row, 1, line['lead_source'], )
            sheet.write(row, 2, line['hot_count'], )
            sheet.write(row, 3, line['warm_count'], )
            sheet.write(row, 4, line['cold_count'], )
            sheet.write(row, 5, line['bad_count'], )
            sheet.write(row, 6, line['nil_count'], )
            sheet.write(row, 7, line['adm_source'], admission)
            sheet.write(row, 8, line['total_count'], total_format)
            sheet.write(row, 9, line['perc_total'], percentage)

            row += 1
            number += 1
        sheet.set_row(row, 20)
        row += 1
        sheet.write(row, 1, 'Admission', header_format)
        sheet.write(row, 2, adm_hot, admission)
        sheet.write(row, 3, adm_warm, admission)
        sheet.write(row, 4, adm_cold, admission)
        sheet.write(row, 5, adm_bad, admission)
        sheet.write(row, 6, adm_nil, admission)
        # sheet.write(row, 7, total_adm, admission)
        # sheet.write(row, 8, total_leads, total_leads_format)

        row += 1
        print(report_lines, 'datas')
        sheet.write(row, 1, 'Total', header_format)
        sheet.write(row, 2, total_hot, total_format)
        sheet.write(row, 3, total_warm, total_format)
        sheet.write(row, 4, total_cold, total_format)
        sheet.write(row, 5, total_bad, total_format)
        sheet.write(row, 6, total_nil, total_format)
        sheet.write(row, 7, total_adm, admission)
        sheet.write(row, 8, total_leads, total_leads_format)

        row += 1
        sheet.write(row, 1, 'Percentage %', header_format)
        sheet.write(row, 2, perc_hot, percentage)
        sheet.write(row, 3, perc_warm, percentage)
        sheet.write(row, 4, perc_cold, percentage)
        sheet.write(row, 5, perc_bad, percentage)
        sheet.write(row, 6, perc_nil, percentage)
        sheet.write(row, 7, perc_total, percentage)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
