# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Remarks',
    'version': '1.0',
    'category': 'Zensoftware/Sale Order',
    'author': "Zen Software Solutions",
    'summary': 'Zen Remarks - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'sale_management',
    ],
    'data': [
        'views/zen_remarks.xml',
        'report/report_sale_order.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}