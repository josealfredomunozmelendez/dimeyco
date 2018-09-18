# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrContractType(models.Model):
    _inherit = "hr.contract.type"

    l10n_mx_edi_code = fields.Char(
        'Code', help='Code defined by SAT to this contract type.')
