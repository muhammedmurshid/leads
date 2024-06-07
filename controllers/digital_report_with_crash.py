from odoo import http
from odoo.http import request
import xlsxwriter
import io
from odoo.http import request
from odoo.http import Controller, request, route, content_disposition


class LeadSourceCrashDigitalExcelReportController(http.Controller):
    @http.route([
        '/lead_report_source_crash_digital/excel_report/<model("lead.report"):report_id>',
    ], type='http', auth="user", csrf=False)
    def get_crash_excel_report_digital(self, report_id=None, **args):
        print(report_id, 'report_id')
        datas = report_id.datas_ids
        print(datas, 'date')
        lead_source = request.env['leads.sources'].sudo().search([('digital_lead', '=', True)])

        total_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'), ('course_type', '=', 'crash'),
             ('leads_source', 'in', lead_source.ids)])
        total_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'), ('course_type', '=', 'crash'),
             ('leads_source', 'in', lead_source.ids)])
        total_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'), ('course_type', '=', 'crash'),
             ('leads_source', 'in', lead_source.ids)])
        total_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'), ('course_type', '=', 'crash'),
             ('leads_source', 'in', lead_source.ids)])
        total_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'), ('course_type', '=', 'crash'),
             ('leads_source', 'in', lead_source.ids)])
        total_leads = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('course_type', '=', 'crash'), ('lead_quality', '!=', False),
             ('leads_source', 'in', lead_source.ids)])
        total_adm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True), ('course_type', '=', 'crash'),
             ('leads_source', 'in', lead_source.ids)])
        total_leads_count = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('course_type', '=', 'crash'), ('lead_quality', '!=', False),
             ('leads_source', 'in', lead_source.ids)])
        adm_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True), ('lead_quality', '=', 'hot'),
             ('course_type', '=', 'crash'), ('leads_source', 'in', lead_source.ids)])
        adm_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True), ('lead_quality', '=', 'cold'),
             ('course_type', '=', 'crash')])
        adm_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True), ('lead_quality', '=', 'warm'),
             ('course_type', '=', 'crash')])
        adm_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True), ('lead_quality', '=', 'nil'),
             ('course_type', '=', 'crash')])
        adm_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True), ('lead_quality', '=', 'bad_lead'),
             ('course_type', '=', 'crash')])
        google_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'google')])
        google_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'google')])
        google_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'google')])
        google_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'google')])
        google_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'google')])
        hoardings_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'hoardings')])
        hoardings_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'hoardings')])
        hoardings_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'hoardings')])
        hoardings_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'hoardings')])
        hoardings_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'hoardings')])
        tv_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'tv_ads')])
        tv_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'tv_ads')])
        tv_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'tv_ads')])
        tv_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'tv_ads')])
        tv_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'tv_ads')])
        social_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'social_media')])
        social_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'social_media')])
        social_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'social_media')])
        social_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'social_media')])
        social_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'social_media')])
        whatsapp_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        whatsapp_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        whatsapp_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        whatsapp_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        whatsapp_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        whatsapp_adm_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        social_adm_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'social_media')])
        google_adm_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'google')])
        tv_adm_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'tv_ads')])
        friend_adm_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'through friends')])
        other_adm_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'other')])
        hoardings_adm_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('admission_status', '=', True),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'hoardings')])
        other_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        other_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        other_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        other_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        other_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        friend_hot = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'hot'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'through friends')])
        friend_warm = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'warm'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'through friends')])
        friend_cold = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'cold'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'through friends')])
        friend_nil = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'nil'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'through friends')])
        friend_bad = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids), ('lead_quality', '=', 'bad_lead'),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'through friends')])
        whatsapp_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'whatsapp')])
        social_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'social_media')])
        google_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'google')])
        tv_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'tv_ads')])
        friend_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'through friends')])
        other_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'other')])
        hoardings_total = request.env['leads.logic'].sudo().search_count(
            [('id', 'in', datas.ids),('course_type', '=', 'crash'),
             ('incoming_source', '=', 'hoardings')])
        if whatsapp_total == 0 or total_leads_count == 0:
            perc_whatsapp = 0
        else:
            perc_whatsapp = round((whatsapp_total / total_leads_count) * 100)
        if google_total == 0 or total_leads_count == 0:
            perc_google = 0
        else:
            perc_google = round((google_total / total_leads_count) * 100)
        if hoardings_total == 0 or total_leads_count == 0:
            perc_hoardings = 0
        else:
            perc_hoardings = round((hoardings_total / total_leads_count) * 100)
        if social_total == 0 or total_leads_count == 0:
            perc_social = 0
        else:
            perc_social = round((social_total / total_leads_count) * 100)
        if friend_total == 0 or total_leads_count == 0:
            perc_friend = 0
        else:
            perc_friend = round((friend_total / total_leads_count) * 100)
        if tv_total == 0 or total_leads_count == 0:
            perc_tv = 0
        else:
            perc_tv = round((tv_total / total_leads_count) * 100)
        if other_total == 0 or total_leads_count == 0:
            perc_other = 0
        else:
            perc_other = round((other_total / total_leads_count) * 100)
        if total_leads_count == 0 or total_leads_count == 0:
            perc_total = 0
        else:
            perc_total = round((total_leads_count / total_leads_count) * 100)
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Digital Lead Report' + '.xlsx'))
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
        sub_source = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': 'white',
            'bg_color': '#cf99c6',  # Background color
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
        report_lines = report_id.get_crash_digital_report_lines()
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

        row += 1
        # sheet.merge_range(f'B{row_size + 3}:J7', 'SUB SOURCES', title_format)
        sheet.set_row(row, 20)
        sheet.write(row, 1, 'Google', sub_source)
        sheet.write(row, 2, google_hot, )
        sheet.write(row, 3, google_warm, )
        sheet.write(row, 4, google_cold)
        sheet.write(row, 5, google_bad)
        sheet.write(row, 6, google_nil)
        sheet.write(row, 7, google_adm_total, admission)
        sheet.write(row, 8, google_total, total_format)
        sheet.write(row, 9, perc_google, percentage)

        row += 1
        sheet.write(row, 1, 'Hoardings', sub_source)
        sheet.write(row, 2, hoardings_hot, )
        sheet.write(row, 3, hoardings_warm, )
        sheet.write(row, 4, hoardings_cold)
        sheet.write(row, 5, hoardings_bad)
        sheet.write(row, 6, hoardings_nil)
        sheet.write(row, 7, hoardings_adm_total, admission)
        sheet.write(row, 8, hoardings_total, total_format)
        sheet.write(row, 9, perc_hoardings, percentage)

        row += 1
        sheet.write(row, 1, 'Social Media', sub_source)
        sheet.write(row, 2, social_hot, )
        sheet.write(row, 3, social_warm, )
        sheet.write(row, 4, social_cold)
        sheet.write(row, 5, social_bad)
        sheet.write(row, 6, social_nil)
        sheet.write(row, 7, social_adm_total, admission)
        sheet.write(row, 8, social_total, total_format)
        sheet.write(row, 9, perc_social, percentage)
        row += 1
        sheet.write(row, 1, 'Through Friends', sub_source)
        sheet.write(row, 2, friend_hot, )
        sheet.write(row, 3, friend_warm, )
        sheet.write(row, 4, friend_cold)
        sheet.write(row, 5, friend_bad)
        sheet.write(row, 6, friend_nil)
        sheet.write(row, 7, friend_adm_total, admission)
        sheet.write(row, 8, friend_total, total_format)
        sheet.write(row, 9, perc_friend, percentage)
        row += 1
        sheet.write(row, 1, 'Tvs Ads', sub_source)
        sheet.write(row, 2, tv_hot, )
        sheet.write(row, 3, tv_warm, )
        sheet.write(row, 4, tv_cold)
        sheet.write(row, 5, tv_bad)
        sheet.write(row, 6, tv_nil)
        sheet.write(row, 7, tv_adm_total, admission)
        sheet.write(row, 8, tv_total, total_format)
        sheet.write(row, 9, perc_tv, percentage)
        row += 1
        sheet.write(row, 1, 'WhatsApp', sub_source)
        sheet.write(row, 2, whatsapp_hot, )
        sheet.write(row, 3, whatsapp_warm, )
        sheet.write(row, 4, whatsapp_cold)
        sheet.write(row, 5, whatsapp_bad)
        sheet.write(row, 6, whatsapp_nil)
        sheet.write(row, 7, whatsapp_adm_total, admission)
        sheet.write(row, 8, whatsapp_total, total_format)
        sheet.write(row, 9, perc_whatsapp, percentage)
        row += 1
        sheet.write(row, 1, 'Other', sub_source)

        sheet.write(row, 2, other_hot, )
        sheet.write(row, 3, other_warm, )
        sheet.write(row, 4, other_cold)
        sheet.write(row, 5, other_bad)
        sheet.write(row, 6, other_nil)
        sheet.write(row, 7, other_adm_total, admission)
        sheet.write(row, 8, other_total, total_format)
        sheet.write(row, 9, perc_other, percentage)
        row += 1
        sheet.set_row(row, 20)
        # row += 1
        # sheet.write(row, 1, 'Admission', header_format)
        # sheet.write(row, 2, adm_hot, admission)
        # sheet.write(row, 3, adm_warm, admission)
        # sheet.write(row, 4, adm_cold, admission)
        # sheet.write(row, 5, adm_bad, admission)
        # sheet.write(row, 6, adm_nil, admission)
        # sheet.write(row, 7, total_adm, admission)
        # sheet.write(row, 8, total_leads, total_leads_format)

        row += 1

        sheet.write(row, 1, 'Total', header_format)
        sheet.write(row, 2, total_hot, total_format)
        sheet.write(row, 3, total_warm, total_format)
        sheet.write(row, 4, total_cold, total_format)
        sheet.write(row, 5, total_bad, total_format)
        sheet.write(row, 6, total_nil, total_format)
        sheet.write(row, 7, total_adm, admission)
        sheet.write(row, 8, total_leads_count, total_format)

        # row += 1
        # sheet.write(row, 1, 'Percentage %', header_format)
        # sheet.write(row, 2, perc_hot, percentage)
        # sheet.write(row, 3, perc_warm, percentage)
        # sheet.write(row, 4, perc_cold, percentage)
        # sheet.write(row, 5, perc_bad, percentage)
        # sheet.write(row, 6, perc_nil, percentage)
        # sheet.write(row, 7, perc_total, percentage)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
