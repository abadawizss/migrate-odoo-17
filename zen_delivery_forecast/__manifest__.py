# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen Delivery Forecast Report',
    'version': '1.0',
    'category': 'Zensoftware/Report',
    'author': "Zen Software Solutions",
    'summary': 'Zen Delivery Forecast Report - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'sale_management',
        'zen_execution_plan',
    ],
    'data': [
        'report/delivery_forecast_report.xml',
        'report/report.xml',
        'wizard/wizard_delivery_forecast_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
