# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Zen Action Plan Reminder for CRM and Sale Order',
    'version': '1.0',
    'category': 'Zensoftware/Reminder',
    'author': "Zen Software Solutions",
    'summary': 'Zen Action Plan Reminder CRM and Sale Order - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'sale_management',
        'base',
        'mail',
        'crm',
        'hr',
        'documents_hr'
    ],
    'data': [
        'data/email_template_sales_order.xml',
        'data/email_template_crm.xml',
        'data/cron_email.xml',
        'views/zen_configuration_reminder_crm_views.xml',
        'views/zen_configuration_reminder_sale_order_views.xml'
    ],
    
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
