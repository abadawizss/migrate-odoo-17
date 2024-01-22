# -*- coding: utf-8 -*-
{
    'name': 'Rashmi Electricals Sale & Stock Management',
    'version': '13.0.1',
    'category': 'Sales',
    'summary': 'Rashmi Electricals Sale & Stock Management.',
    'description': """
Rashmi Electricals Sale & Stock Management
=============================

This module makes the link between the Rashmi Electricals sale and Rashmi Electricals stock management
applications.
""",
    'author': 'Niraj Pajwani',
    'website': '',
    'depends': ['sale_stock', 'relec_sale', 'relec_stock'],
    'data': [
        'views/stock_picking_view.xml',
        # 'views/report_picking_list.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True
}