# -*- coding: utf-8 -*-
{
    'name': "Billing and Collection System",
    'summary': """
        Billing and Collection Details Information""",
    'description': """
        AMYu Systems - Billing and Collection System. 

        Processes the Billing and Collection of Finance and Audit Department, 
        wherein the prequisites are the client profiles fetched from CPMS, 
        and the clients' Billing Summary.

        As of version 1, the expected generated outputs are the 
        (1) Collection Reports and (2) SOA & Billing Statements. 
    """,
    'author': 'Rann Aureada & Angelo Algarne',
    'website': "https://www.amyucpas.com",
    'category': 'Custom',
    'version': '0.1',
    'depends': ['base', 'muk_web_theme', 'hrad', 'amyu1'],

    # always loaded
    'data': [
      'data/bank.csv',
      'data/services.type.csv',
      'security/ir.model.access.csv',
      'report/ar_report.xml',
      'views/soa_ar_journal_view.xml',
      'views/soa_manual_posting_view.xml',
      'views/base_billing_view.xml',
      'views/billing_summary_view.xml',
    #   'views/audit_billing_view.xml',
    #   'views/trc_billing_view.xml',
    #   'views/books_billing_view.xml',
    #   'views/business_permit_billing_view.xml',
    #   'views/gis_billing_view.xml',
    #   'views/loa_billing_view.xml',
    #   'views/special_engagement_view.xml',
      'views/services_type_view.xml',
      'views/bcs_billing_view.xml',
      'views/bcs_collection_view.xml',
      'views/bcs_update_view.xml',
      'views/state_billing_view.xml',
      'views/bcs_group_view.xml',
      'views/bcs_client_billing_info_views.xml',
      'views/bcs_bank_view.xml',
      'views/bcs_menu_view.xml',
     ],
    'application': True,
    'license': 'LGPL-3',
}
