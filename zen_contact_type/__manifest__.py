# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Contact Type',
    'version': '1.0',
    'category': 'Zensoftware/Contact',
    'author': "Zen Software Solutions",
    'summary': 'Zen Contact Type - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'contacts',
        'purchase',
    ],
    'data': [
        'views/zen_res_partner.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}