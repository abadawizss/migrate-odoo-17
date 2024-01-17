# -*- coding: utf-8 -*-
{
    'name': 'Rashmi Electricals Base',
    'version': '13.0.1',
    'category': 'Hidden',
    'summary': 'Rashmi Electricals Base.',
    'description': """
Rashmi Electricals Base
==========
""",
    'author': 'Niraj Pajwani',
    'website': '',
    'depends': ['web', 'l10n_in'],
    'data': [
        # 'views/report_templates.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/res_users_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}