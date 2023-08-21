from odoo import http
from odoo.http import request
import io
import base64


class ServiceRequest(http.Controller):
    @http.route(['/leads_form/<int:user_id>'], type='http', auth="public", website=True,)
    def service_request_form(self, user_id, **kw):
        # byte_msg = user_id.encode('ascii')
        # base64_val = base64.b64decode(byte_msg)
        # user_id = int(base64_val.decode('ascii'))
        # print("The Converted value of the string  \"", py_string, "\"  is\n", base64_string)
        user = request.env['res.users'].sudo().browse(user_id)
        user_data = {
            'id': user.id,
            'name': user.name,
        }

        # if user:
        #     user_data = {
        #
        #         # Include other relevant fields
        #     }
        # products = request.env['res.users'].sudo().search([])
        # aa = http.request.env.context.get('uid')
        # user = http.request.env['res.users'].sudo().search([('id', '=', aa)])
        # print(user.name)
        # values = {
        #     'user': products,
        #     'aa': aa,
        #     'current_user': user
        # }
        return request.render("leads.leads_service_request_form", user_data)

    @http.route(['/leads_form/submit'], type='http', auth="public", website=True, csrf=False)
    def customer_leads_form_submit(self, **kw):

        request.env["crm.lead"].sudo().create({
            'name': kw.get('contact_name'),
            'student_name': kw.get('contact_name'),
            'phone': kw.get('phone'),
            # 'email_from': post.get('email'),
            'street': kw.get('description'),
            'father_name': kw.get('father_name'),
            'father_no': kw.get('father_phone'),
            'mother_name': kw.get('mother_name'),
            'mother_no': kw.get('mother_phone'),
            'last_institution': kw.get('last_institute'),
            'course_studied': kw.get('course_studied'),
            'referred': kw.get('referred_by'),
            'user_id': kw.get('sales_person'),
        })
        # products = request.env['product.product'].search([])
        # values = {
        #     'products': products
        # }
        return request.render("leads.tmp_leads_form_logic_success", {})
