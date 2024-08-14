# -*- coding: utf-8 -*-
{
    'name': "FSMS Tracker",

    'summary': """
        Income Tax Return Monitoring System""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Rann Aureada",
    'website': "https://www.amyucpas.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'FS Tracker',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'muk_web_theme'],

    # always loaded
    'data': [
        'views/groups_view.xml',
        'security/ir.model.access.csv',
        'views/main_project_view.xml',
        'views/task_view.xml',
        'views/tracker_process_view.xml',
        'views/tracker_preparation_view.xml',
        'views/label_note_view.xml',
        'views/state_history_view.xml',
        'views/associate_group_view.xml',
        'views/menu_view.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
