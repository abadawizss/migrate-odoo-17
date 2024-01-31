# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Restrication',
    'version': '1.0',
    'category': 'Zensoftware/Sale Order',
    'author': "Zen Software Solutions",
    'summary': 'Zen Remarks - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'sale_management',
        'crm',
        'sales_team',
    ],
    'data': [
        'views/kanban_view.xml',
        # 'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}