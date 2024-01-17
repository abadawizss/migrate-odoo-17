# -*- coding: utf-8 -*-
{
    'name': 'Rashmi Electricals Stock Management',
    'version': '13.0.1',
    'category': 'Operations/Inventory',
    'summary': 'Rashmi Electricals Stock Management.',
    'description': """
Rashmi Electricals Stock Management
======================
""",
    'author': 'Niraj Pajwani',
    'website': '',
    'depends': ['stock', 'delivery', 'relec_base', 'relec_product'],
    'data': [
        'views/stock_picking_view.xml',
        'views/picking_report.xml',
        'views/report_picking_list.xml',
        'views/report_deliveryslip.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}