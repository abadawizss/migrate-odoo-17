# -*- coding: utf-8 -*-
{
    'name': 'Bank Guarantees',
    'version': '1.0',
    'category': 'Zensoftware/Sales',
    'description': """
        This module adds the functionality to manage bank guarantees and earnest money deposits.
    """,
    'depends': ['base','sale_management','sale_stock','documents','mail'],
    'data': [
        #additional sequence 20231218
        'security/security.xml',
        'wizards/zen_wizard_renew_replace.xml',
        'data/cron_job_reminder.xml',
        'data/template_email_bank_guarantees.xml',
        'views/documents.xml',
        'data/sequence_bank_guarantees.xml',
        #additional sequence 20231218
        
        'security/ir.model.access.csv',
        'views/zen_bank_guarantees.xml',
        'data/menu_zen_bank_guarantees.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
}