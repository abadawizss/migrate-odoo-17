# -*- coding: utf-8 -*-
{
    'name': 'Rashmi Electricals Sales Management',
    'version': '13.0.1',
    'category': 'Sales/Sales',
    'summary': 'Rashmi Electricals Sales Management.',
    'description': """
Rashmi Electricals Stock Management
======================
""",
    'author': 'Niraj Pajwani',
    'website': '',
    'depends': ['sale', 'delivery', 'relec_base', 'relec_account', 'sale_order_lot_selection'],
    'data': [
        'data/mail_data.xml',
        # 'views/res_config_settings_view.xml',
        'views/sale_view.xml',
        'views/account_move_view.xml',
        'views/sale_report_templates.xml',
        'views/sale_domestic_pro_forma_template.xml',
        'views/sale_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}