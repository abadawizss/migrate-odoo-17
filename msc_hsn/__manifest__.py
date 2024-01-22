# -*- coding: utf-8 -*-
###############################################################################
#
#    Meghsundar Private Limited(<https://www.meghsundar.com>).
#
###############################################################################
{
    'name': 'HSN Code',
    'version': '14.0.1',
    'summary': 'HSN Code',
    'description': 'HSN Code',
    'category': 'Product',
    'license': 'AGPL-3',
    'author': 'Meghsundar Private Limited',
    'website': 'https://meghsundar.com',
    'depends': ['l10n_in', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/master_hsn_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
}