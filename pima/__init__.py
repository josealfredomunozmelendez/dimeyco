# coding: utf-8
from odoo import api, SUPERUSER_ID
from . import models
from . import report
from . import wizard


def _auto_load_translation(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        lang_obj = env['res.lang']
        modobj = env['ir.module.module']
        lang = 'es_MX'
        lang_ids = lang_obj.search([('code', '=', lang)])
        if not lang_ids:
            lang_id = lang_obj.load_lang(lang)
            lang_ids += lang_obj.browse(lang_id)
        context = {'overwrite': True}
        mids = modobj.search([('state', '=', 'installed')])
        lang_ids += lang_obj.search([('code', '=', 'en_US')])
        mids.with_context(context)._update_translations(lang)
        lang_ids.write(
            {
                'date_format': '%d/%m/%Y',
                'time_format': '%H:%M:%S',
                'thousands_sep': ',',
                'decimal_point': '.',
                'grouping': '[3,3,3,3,3,3,3,3,-2]'})
