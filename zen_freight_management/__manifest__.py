# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Freight Management',
    'version': '0.1',
    'category': 'Zensoftware/Freight',
    'author': "Ahmad Badawi",
    'summary': 'Zen Freight Management',
    'website': 'https://www.odoo.com/app/crm',
    'depends': [
        'sale_management',
        'zen_report_sale_order'
    ],
    'data': [
        'report/zen_freight_report_sale_order.xml',
        'views/zen_freight_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}