# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Disqualified Reason CRM',
    'version': '1.0',
    'category': 'Zensoftware/CRM',
    'author': "Zen Software Solutions",
    'summary': 'Zen Disqualified Reason CRM - v1.1',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'crm',
        'sales_team',
    ],
    'data': [
        'views/zen_disqualified_reason.xml',
        'wizard/zen_crm_lead_disqualify_views.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
