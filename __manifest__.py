{
    'name': "Leads",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['mail', 'crm'],
    'data': [
        'security/lead_users.xml',
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'views/logic_leads.xml',

    ],
    'demo': [],
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
