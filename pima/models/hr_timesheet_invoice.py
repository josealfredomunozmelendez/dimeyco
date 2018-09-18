# coding: utf-8
from odoo import fields, models, api


class HrTimesheetInvoiceFactor(models.Model):

    _name = "hr_timesheet_invoice.factor"
    _description = "Invoice Rate"
    _order = 'factor'

    name = fields.Char('Internal Name', required=True, translate=True)
    customer_name = fields.Char('Name', help="Label for the customer")
    factor = fields.Float(
        'Discount (%)',
        default=0.0,
        help="Discount in percentage")


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    to_invoice = fields.Many2one(
        'hr_timesheet_invoice.factor',
        'Invoiceable',
        default=lambda s: s.env['hr_timesheet_invoice.factor'].search(
            [], order='factor asc', limit=1),
        help="It allows to set the discount while making invoice, keep"
        " empty if the activities should not be invoiced.")

    invoiceables_hours = fields.Float(
        'Invoiceable Hours',
        compute="_compute_invoiceables_hours",
        help='Total hours to charge')

    invoice_id = fields.Many2one(
        'account.invoice',
        'Invoice',
        ondelete="set null",
        copy=False)

    @api.depends('to_invoice', 'unit_amount')
    def _compute_invoiceables_hours(self):
        for line in self:
            hours = line.unit_amount
            if line.to_invoice:
                hours -= (hours * line.to_invoice.factor / 100.0)
            line.invoiceables_hours = hours
