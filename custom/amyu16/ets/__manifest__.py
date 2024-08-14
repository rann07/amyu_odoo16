{
    'name': 'Errand Tracking System',
    'author': 'Angelo Admin',
    'category': 'Application',
    'summary': 'Errand Tracking System',
    'version': '1.0',
    'description': """
        AMYu System - Errand Tracking System
    """,
    'depends': ['base', 'hrad'],
    'data': [
        'security/ir.model.access.csv',
        'views/ets_errand_view_tree.xml',
        'views/ets_errand_own_views.xml',
        'views/ets_errand_for_approval_views.xml',
        'views/ets_errand_db_views.xml',
        'views/ets_location_views.xml',
        'views/ets_liaison_views.xml',
        'views/ets_menu_views.xml',
        
        'data/location.csv',
    ],
    'auto_install': True,
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}