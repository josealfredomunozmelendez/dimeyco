# coding: utf-8
from odoo import models, api


class ProcurementRule(models.Model):

    _inherit = 'procurement.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name,
                 origin, values):
        res = super(ProcurementRule,
                    self.with_context(create_always=origin))._run_buy(
                        product_id, product_qty, product_uom,
                        location_id, name, origin, values)
        return res

    def _make_po_get_domain(self, values, partner):
        domain = super(ProcurementRule, self)._make_po_get_domain(
            values, partner)
        if self.env.context.get('create_always'):
            return (('partner_id', '=', partner.id),
                    ('state', '=', 'draft'),
                    ('origin', 'ilike', self.env.context['create_always']))
        return domain
