# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from ..hooks import _load_xsd_complement


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_edi_curp = fields.Char(
        'CURP', size=18, help='Attribute to set in XML to express the CURP'
        'when the company is from a natural person.')
    l10n_mx_edi_minimum_wage = fields.Float(
        'Mexican minimum Wage',
        help='Indicates the current daily amount of the general minimum wage '
        'in Mexico')

    @api.model
    def _load_xsd_attachments(self):
        # noqa TODO Remove after of this merge https://github.com/odoo/enterprise/pull/1617
        res = super(ResCompany, self)._load_xsd_attachments()
        url = 'http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd'
        xsd = self.env.ref('l10n_mx_edi.xsd_cached_nomina12_xsd', False)
        if xsd:
            xsd.unlink()
        _load_xsd_complement(self._cr, None, url)
        return res
