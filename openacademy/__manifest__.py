# -*- coding: utf-8 -*-
{
    'name':        "OpenAcademy",

    'summary':
                   """
                   Openacademy""",

    'description': """
        Manage course, classes, teachers, students, ...
    """,

    'author':      "Odoo",
    'website':     "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category':    'OpenAcademy',
    'version':     '1.1',

    # any module necessary for this one to work correctly
    'depends':     ['base', 'mail', 'product', 'account'],

    # always loaded
    'data':        [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/course_views.xml",
        "views/session_views.xml",
        "views/partner_views.xml",
        "views/helper_views.xml",
        "views/menu_views.xml",
        "wizard/add_attendee_views.xml",
        # "data/openacademy_data.xml",
        "data/f_clean_instructors.xml",
        "data/f_set_instructors.xml",
        "views/session_actions.xml",
    ],
    # only loaded in demonstration mode
    'demo':        [],
}
