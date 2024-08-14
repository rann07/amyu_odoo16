# -*- coding: utf-8 -*-
{
    'name': "Client Profile Management System",

    'summary': """
        Client Information""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Rann Aureada",
    'website': "https://www.amyucpas.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'muk_web_theme', 'hrad'],

    # always loaded
    'data': [
        'views/cpms_group.xml',
        'security/ir.model.access.csv',
        'views/associate_profile_view.xml',
        'views/client_profile_view.xml',
        'views/cpms_state_view.xml',
        'views/cpms_client_list_view.xml',
        'views/cpms_report_view.xml',
        'views/department_menu_view.xml',
        'views/supervisor_view.xml',
        'views/manager_view.xml',
        'views/capitalization_menu_view.xml',
        'views/corporate_officer_menu_view.xml',
        'views/escalation_contact.xml',
        'views/cmps_menu_view.xml',
        'report/cpms_preview_reports.xml',

    ],
    'application': True,
    'license': 'LGPL-3',
}
