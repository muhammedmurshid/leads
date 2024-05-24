from odoo import http
from odoo.http import request
import xlsxwriter
import io
from odoo.http import Controller, request, route, content_disposition


class LeadExcelReportCourseController(http.Controller):
    @http.route([
        '/lead_report_course/excel_report/<model("lead.report"):report_id>',
    ], type='http', auth="user", csrf=False)
    def get_course_base_excel_report(self, report_id=None, **args):
        print(report_id, 'report_id')
        datas = report_id.datas_ids
        print(datas, 'date')
        lead_source = request.env['leads.sources'].sudo().search([])
        course = request.env['logic.base.courses'].sudo().search([('state', '=', 'done')])
        total_count = request.env['leads.logic'].sudo().search_count([('id', 'in', datas.ids)])

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Course Wise Report' + '.xlsx'))
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
        percentage = workbook.add_format({
            'font_color': 'black',
            'bg_color': '#f0a732',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        admission = workbook.add_format({
            'font_color': 'black',
            'bg_color': '#84f032',  # Background color
            'align': 'center',
            'valign': 'vcenter',
        })
        # get data for the report.
        report_lines = report_id.get_course_reports()
        print(report_lines, 'report_lines')
        non_empty_columns = set()
        for line in report_lines:
            if line['adm_count'] > 0 or line['count'] > 0 or line['prc_count'] > 0:
                non_empty_columns.add('Admission')
                non_empty_columns.add('Total')
                non_empty_columns.add('Percentage %')
            for source in lead_source:
                search_count = request.env['leads.logic'].sudo().search_count(
                    [('id', 'in', datas.ids), ('leads_source', '=', source.id),
                     ('base_course_id', '=', line['course_id'])]
                )
                if search_count > 0:
                    non_empty_columns.add(source.name)

        # prepare excel sheet styles and formats
        sheet = workbook.add_worksheet("courses")
        sheet.write(1, 0, 'No.', header_format)
        sheet.write(1, 1, 'Courses', header_format)
        for source in lead_source:
            sheet.write(1, 1 + source.id, source.name, header_format)
        print(len(lead_source), 'len(lead_source)')
        sheet.write(1, len(lead_source)+2, 'Admission', header_format)
        sheet.write(1, len(lead_source)+3,'Total', header_format)
        sheet.write(1, len(lead_source)+4, 'Percentage %', header_format)

        row = 2
        number = 1
        # write the report lines to the excel document
        for line in report_lines:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, )
            sheet.write(row, 1, line['lead_course'], )
            for source in lead_source:
                sheet.write(1, 1 + source.id, source.name, header_format)

                search_count = request.env['leads.logic'].sudo().search_count(
                    [('id', 'in', datas.ids), ('leads_source', '=', source.id),
                     ('base_course_id', '=', line['course_id'])])
                perc_course = round((search_count / total_count) * 100)
                sheet.write(row, 1 + source.id, search_count, )
            sheet.write(row, len(lead_source)+2, line['adm_count'], admission)
            sheet.write(row, len(lead_source)+3, line['count'], total_format)
            sheet.write(row, len(lead_source)+4, line['prc_count'], percentage)

            row += 1
            number += 1
        sheet.set_row(row, 20)
        sheet.write(row, 1, 'Admission', header_format)
        for adm in lead_source:
            adm_count = request.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', adm.id),('admission_status', '=', True),
                 ])
            sheet.write(row, 1 + adm.id, adm_count, admission)
        row += 1
        sheet.write(row, 1, 'Total', header_format)
        for v in lead_source:
            search_count = request.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', v.id),
                 ])
            sheet.write(row, 1 + v.id, search_count, total_format)
            sheet.write(row, len(lead_source) + 3, total_count, total_leads_format)
        row += 1
        sheet.write(row, 1, 'Percentage %', header_format)
        for e in lead_source:
            search_prc = request.env['leads.logic'].sudo().search_count(
                [('id', 'in', datas.ids), ('leads_source', '=', e.id),
                 ])
            perc_source = round((search_prc / total_count) * 100)
            sheet.write(row, 1 + e.id, perc_source, percentage)

            # perc_source = round((search_count / total_count) * 100)
            # sheet.write(row, len(lead_source)+4, perc_source, percentage)
        row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
