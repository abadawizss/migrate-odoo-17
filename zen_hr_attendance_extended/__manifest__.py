# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Zen HR Attendance Extended',
    'version': '1.0',
    'category': 'Zensoftware/Attendances',
    'author': "Zen Software Solutions",
    'summary': 'Zen HR Attendance Extended - v1.0',
    'website': 'https://www.zensoftwaresolutions.com',
    'depends': [
        'hr',
        'hr_attendance'
    ],
    'data': [
        'views/hr_attendance_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_work_location_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}