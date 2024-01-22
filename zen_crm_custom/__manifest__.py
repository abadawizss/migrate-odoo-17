# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen CRM',
    'version': '1.0',
    'category': 'Zensoftware/CRM',
    'author': "Zen Software Solutions",
    'summary': 'Zen CRM Custom - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'crm',
        'sales_team',
    ],
    'data': [
        'views/zen_crm_custom.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}