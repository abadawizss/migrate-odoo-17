# -*- coding: utf-8 -*-
{
    'name': "Zen Sale Project",
    'summary': """This module is developed to create projects from sale orders and tasks from order lines. Each sale order can be associated with a project,
     and each order line can be associated with a task under that project.""",
    'description': """
        This module is developed to create projects from sale orders and tasks from order lines. Each sale order can be associated with a project, 
        and each order line can be associated with a task under that project.
    """,
    'author': "Muhammad Imran",
    'website': 'https://www.zensoftwaresolutions.com',
    # 'category': 'project',
    'category': 'Zensoftware/Project',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','project', 'sale_management', 'portal', 'sale_stock'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/project_form.xml',
        # 'views/project_portal_templates.xml',
        'views/portal_template.xml',
        # 'views/templates.xml',
    ],
    'assets': {
        # 'web.assets_backend': [
        #     'zen_sale_project/static/src/js/my_script.js',
        # ],
        'web.assets_frontend': [
            'zen_sale_project/static/src/js/my_script.js',
            'zen_sale_project/static/src/xml/portal_chatter_inherit.xml',
        ],
        # 'web.qunit_suite_tests': [
        #     'zen_sale_project/static/src/js/my_script.js',
        #
        # ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}