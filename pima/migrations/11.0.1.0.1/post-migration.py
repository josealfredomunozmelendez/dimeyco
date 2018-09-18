# -*- coding: utf-8 -*-
import logging
from odoo import SUPERUSER_ID, api
_logger = logging.getLogger(__name__)


def remove_website(cr):

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        module = env.ref('base.module_sale_subscription')
        module.button_uninstall()


def migrate(cr, version):
    if not version:
        return
    remove_website(cr)
