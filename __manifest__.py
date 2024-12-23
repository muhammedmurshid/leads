{
    'name': "Leads",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['mail', 'crm', 'logic_base',],
    'data': [
        'security/lead_users.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'views/logic_leads.xml',
        'views/lead_web_form.xml',
        'data/scheduled_action.xml',
        'views/activity_view.xml',
        'views/lead_channel_name.xml',
        'views/search_wizard.xml',
        'views/re_allocation_req.xml',
        'views/touch_points.xml',
        'views/lead_target.xml',
        'views/admission.xml',
        'data/cron_job.xml',
        'views/re_allocation.xml',
        'views/lead_report.xml',
        'views/duplicate_pipeline_leads.xml',
        'views/leads_bulk_assign_view.xml'
        # 'views/link_generation.xml',

    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'leads/static/src/js/log_note_hide_custom.js'],
    # },
    # 'demo': [],
    'images': [
        '/home/murshid/odoo/custome_addons/logic_leads/static/description/icon.png',
    ],
    'summary': "logic_leads",
    'description': "this_is_my_app",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}
