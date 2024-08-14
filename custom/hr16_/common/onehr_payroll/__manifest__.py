# -*- coding: utf-8 -*-
{
    'name': "Payroll Module",
    'summary': "OnE-HR's Payroll Module",
    'description': "OnE-HR's Payroll Module",
    'author': "XWare",
    'website': "https://www.xwareit.net/",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'hrad'],
    'data': [
        'views/hr_payroll_master_view.xml',
        'wizard/compute_payroll_wizard.xml',
        'wizard/compute_payroll_executives_wizard.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'LGPL-3',
}
