# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Execution Plan Sale Order',
    'version': '1.0',
    'category': 'Zensoftware/Sale Order',
    'author': "Zen Software Solutions",
    'summary': 'Zen Execution Plan Sale Order - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'sale_management',
        'zen_approval',
    ],
    'data': [
        'data/cron_execution_plan.xml',
        'data/email_template_execution_date.xml',
        'views/zen_execution_plan.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}