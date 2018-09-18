# -*- coding: utf-8 -*-


def removed_view_customs_modules(cr):
    cr.execute("""DELETE FROM ir_ui_view WHERE id IN (
        SELECT res_id FROM ir_model_data
        WHERE module = 'l10n_mx_landing' AND model = 'ir.ui.view');""")
    cr.execute("""DELETE FROM ir_ui_view WHERE id IN (
        SELECT res_id FROM ir_model_data
        WHERE module = 'l10n_mx_customs' AND model = 'ir.ui.view');""")
    cr.execute("""DELETE FROM ir_model_data
               WHERE module = 'l10n_mx_landing' AND model = 'ir.ui.view';""")
    cr.execute("""DELETE FROM ir_model_data
               WHERE module = 'l10n_mx_customs' AND model = 'ir.ui.view';""")
    cr.execute("""UPDATE ir_model_data SET module = 'l10n_mx_edi_landing'
               WHERE module = 'l10n_mx_landing' AND model = 'ir.model.fields';""")  # noqa
    cr.execute("""UPDATE ir_model_data SET module = 'l10n_mx_edi_customs'
               WHERE module = 'l10n_mx_customs' AND model = 'ir.model.fields';""")  # noqa


def migrate(cr, version):
    if not version:
        return
    removed_view_customs_modules(cr)
