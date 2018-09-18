# -*- coding: utf-8 -*-
{
    'name': "Requisicion de Inventario",

    'summary': """
        Allow to request items trough a inventory requisition """,

    'description': """
       TBD
    """,

    'author': "LLACOX",
    'website': "http://www.llacox.com",

    # Categories can be used to filter modules in modules listing
    'category': 'stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'stock',
        'purchase',
        'hr',
        'stock_account',

    ],

    # always loaded
    'data': [
        # Security
        # "security/ir.model.access.csv",
        'report/purchase_order_templates.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/stock.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
