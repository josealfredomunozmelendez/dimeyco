# coding: utf-8
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderE(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(selection_add=[
        ('one_line', 'General Description'),
        ])

    @api.multi
    def create_invoices(self):
        """Now the invoice will be created using an unique product with the
        total order"""
        if not self.advance_payment_method == 'one_line':
            return super(SaleOrderE, self).create_invoices()
        sale_order = self.env['sale.order'].browse(
            self._context.get('active_ids'))[0]
        if not sale_order.project_product_id:
            raise UserError(
                _(("It is needed to choose a Project product to continue "
                   "the general description invoice. If the project "
                   "description isn't specified a default value would "
                   "be added")))
        self.write({
            'product_id': sale_order.project_product_id.id,
            'advance_payment_method': 'fixed',
            'amount': sale_order.amount_untaxed})
        inv = super(SaleOrderE, self).create_invoices()
        line = sale_order.order_line.filtered(
            lambda x: x.product_id == sale_order.project_product_id)
        line.invoice_lines.name = sale_order.project_description
        order = line.order_id
        line.state = 'cancel'
        line.unlink()
        order.invoice_status = 'invoiced'
        return inv
