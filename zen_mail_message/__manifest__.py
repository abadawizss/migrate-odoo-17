# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Mail Message Chatter',
    'version': '1.0',
    'category': 'Zensoftware/Mail',
    'author': "Zen Software Solutions",
    'summary': 'Zen Mail Message Chatter - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'mail',
        'crm',
        'sale'
    ],
    'data': [
        'views/zen_configuration_chatter.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}