# -*- coding: utf-8 -*-
{
    'name': "Sales render",

    'summary': """
        Adds a render field that will appear on all of the sale documents.""",

    'description': """
        Adds a render field that will appear on all of the sale documents.
    """,

    'author': "Llacox",
    'website': "http://www.llacox.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '11.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','website_quote','sale'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
}