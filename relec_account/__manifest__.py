# -*- coding: utf-8 -*-
{
    'name': 'Rashmi Electricals Account Management',
    'version': '13.0.1',
    'category': 'Accounting/Accounting',

    'summary': 'Rashmi Electricals Account Management.',
    'description': """
Rashmi Electricals Account Management
========================
""",
    'author': 'Niraj Pajwani',
    'website': '',
    'depends': ['account', 'delivery', 'relec_base', 'relec_product'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_report.xml',
        'data/mail_data.xml',
        'views/account_move_view.xml',
        'views/commercial_report_invoice.xml',
        'views/tax_report_invoice.xml',
        'views/proforma_report_invoice.xml',
        'views/report_final_invoice.xml',
        'views/distributed_line_view.xml',
        'views/account_tax_view.xml',
        'views/domestic_pro_forma_template.xml',
        'views/domestic_final_invoice.xml',
        'views/domestic_tax_report_invoice.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}