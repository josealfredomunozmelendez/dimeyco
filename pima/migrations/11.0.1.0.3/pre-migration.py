# -*- coding: utf-8 -*-


def removed_view_customs_modules(cr):
    cr.execute("""UPDATE ir_module_module SET state = 'uninstallable'
               WHERE name in ('l10n_mx_customs', 'l10n_mx_landing');""")


def migrate(cr, version):
    if not version:
        return
    removed_view_customs_modules(cr)
