import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def change_partner_banks(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        payslip_banks = env['res.bank'].search([]).filtered(
            lambda r: r.get_external_id()[r.id].startswith(
                'l10n_mx_edi_payslip'))
        accounts = env['res.partner.bank'].search([
            ('bank_id', 'in', payslip_banks.ids)])
        for acc in accounts:
            new_bank = env['res.bank'].search([
                ('name', '=', acc.bank_id.name), ('id', '!=', acc.bank_id.id)
            ])
            if not new_bank:
                _logger.warning('WARNING: No bank found %s', acc.bank_id.name)
                continue
            if len(new_bank) > 1:
                new_bank = new_bank.filtered(lambda r: r.get_external_id(
                )[r.id].startswith('l10n_mx_edi_bank'))
            _logger.info(
                'INFO: Changing %s - %s for %s - %s', acc.bank_id.id,
                acc.bank_id.name, new_bank.id, new_bank.name)
            acc.bank_id = new_bank
        payslip_banks.unlink()


def migrate(cr, version):
    if not version:
        return
    change_partner_banks(cr)
