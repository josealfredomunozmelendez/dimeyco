# coding: utf-8
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class ResCompany(models.Model):

    _inherit = 'res.company'

    def _compute_add(self):
        self.website_address_ids = self.sudo().partner_id.child_ids

    website_address_ids = fields.Many2many('res.partner',
                                           string='Web Contacts',
                                           compute='_compute_add',
                                           store=False,
                                           help="All contact public Contacts"
                                           "to be shown in contact form.")
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        related='country_id.currency_id',
    )

    code = fields.Char(help="Internal code name of the company")

    @api.multi
    @api.constrains('code')
    def unique_code(self):
        for record in self:
            if record.code and record.search(
                    [('code', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError(_('Code must be unique'))
