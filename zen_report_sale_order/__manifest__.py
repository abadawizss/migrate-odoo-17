# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Report Sale Order',
    'version': '0.1',
    'category': 'Zensoftware/Sale Order',
    'author': "Ahmad Badawi",
    'summary': 'Zen Report Sale Order',
    'website': 'https://www.odoo.com/app/crm',
    'depends': [
        'sale_management',
    ],
    'data': [
        'report/zen_report_sale_order.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}