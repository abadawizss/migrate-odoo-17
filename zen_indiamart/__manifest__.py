# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Indiamart',
    'version': '1.0',
    'category': 'Zensoftware/Integration',
    'author': "Zen Software Solutions",
    'summary': 'Zen Indiamart Integration - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'base',
        'crm',
        'sale_management',
        'contacts',
        'purchase'
    ],
    'data': [
        'data/cron_job_indiamart.xml',
        'views/zen_indiamart_configuration_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
