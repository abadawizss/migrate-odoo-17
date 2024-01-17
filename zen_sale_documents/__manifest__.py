# -*- coding: utf-8 -*-
{
    'name': 'Zen Sale Documents',
    'version': '1.0',
    'category': 'Zensoftware/Sale',
    'author': "Zen Software Solutions",
    'summary': 'Zen Sale Documents - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    # any module necessary for this one to work correctly
    'depends': ['sale', 'crm', 'documents', 'sale_crm', 'mail', 'base','zen_crm_documents'],

    # always loaded
    'data': [
        'views/sale_document.xml'
    ],
    
}
