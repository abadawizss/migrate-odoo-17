# -*- coding: utf-8 -*-
{
    'name': "zen_crm_documents",

    'summary': """The zen_crm_documents module is a custom module for Odoo that allows users to attach documents to CRM records. """,

    'description': """
        The zen_crm_documents module is a custom module for Odoo that allows users to attach documents to CRM records. 
    """,

    'author': "Zen Software Solutions",
    'website': "https://www.zensoftwaresolutions.com",

    'category': 'crm',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'documents', 'sale_crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/crm_lead.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
