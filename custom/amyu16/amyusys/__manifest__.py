# -*- coding: utf-8 -*-
{
    'name': "AMYU Systems",
    'summary': """
        Install all AMYU Systems (HRIS, CPMS, BCS, & ETS)""",
    'description': """
        AMYu Systems

        This module holds all AMYU systems as dependencies. Install this module to install the following:
            1. Human and Resources Information System
            2. Client Profile Management System
            3. Billing and Collection System
            4. Errand Tracking System
            
        If possible, this module will also include test data or import functions that will automatically fill tables.
    """,
    'author': 'Rann Aureada & Angelo Algarne',
    'website': "https://www.amyucpas.com",
    'category': 'Custom',
    'version': '0.1',
    'depends': ['base', 'muk_web_theme', 'hrad', 'amyu1', 'bcs', 'ets'],

    # always loaded
    'data': [
        'data/amyusys.included.modules.csv',
        'wizard/import_amyu_data_wizard_view.xml',
        'views/amyusys_main_view.xml',
        'views/amyusys_menu_view.xml',
     ],
    'application': True,
    'license': 'LGPL-3',
}
