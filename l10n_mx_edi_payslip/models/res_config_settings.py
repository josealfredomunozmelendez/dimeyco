# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_edi_minimum_wage = fields.Float(
        related='company_id.l10n_mx_edi_minimum_wage',
        string='Mexican minimum salary',
        help='Indicates the current daily amount of the general minimum wage '
        'in Mexico')
