# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def set_not_null(cr):

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.cr.execute(
            '''UPDATE
                   account_analytic_line
               SET
                   name=id
               WHERE
                   name IS NULL
            ''')


def migrate(cr, version):
    if not version:
        return
    set_not_null(cr)
