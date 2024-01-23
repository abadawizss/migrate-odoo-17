# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Discount Model Sale Order',
    'version': '1.0',
    'category': 'Zensoftware/Sale Order',
    'author': "Zen Software Solutions",
    'summary': 'Zen Discount Model Sale Order - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'base',
        'sale_management',
    ],
    'data': [
        'views/zen_disocunt_model.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
