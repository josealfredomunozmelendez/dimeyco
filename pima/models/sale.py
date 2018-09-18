# coding: utf-8
from odoo import models, fields, api, _
from . import rst2html


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    desc2html = fields.Text(string="Converted RST", compute="_rst2html")

    @api.depends('name')
    def _rst2html(self):
        for line in self:
            line.desc2html = rst2html.html.rst2html(line.name)

    @api.multi
    def _compute_analytic(self, domain=None):
        lines = {}
        res = super(SaleOrderLine, self)._compute_analytic(domain)
        if not domain:
            domain = [('so_line', 'in', self.ids), ('amount', '<=', 0.0)]
        data = self.env['account.analytic.line'].search(domain)
        for line in self.env.context.get("force_so_lines", []):
            lines.setdefault(line, 0.0)
        for line_analytic in data:
            if not line_analytic['product_uom_id']:
                continue
            line = line_analytic['so_line']
            lines.setdefault(line, 0.0)
            uom = line_analytic['product_uom_id']
            qty = line_analytic.invoiceables_hours
            if line.product_uom.category_id == uom.category_id:
                qty = uom._compute_quantity(line_analytic.invoiceables_hours,
                                            line.product_uom)
            lines[line] += qty
        for line, qty in lines.items():
            line.qty_delivered = qty
        return res

    def _timesheet_create_task_prepare_values(self):
        self.ensure_one()
        task = super(
            SaleOrderLine, self)._timesheet_create_task_prepare_values()
        task.update(
            name=self.name.split('\n')[0],
            kanban_state="blocked",
            user_id=self.env['project.project'].browse(
                task.get('project_id')).user_id.id,
            color=6)
        # TODO maybe this default color for the user stories can be configured
        # somewhere as a system parameter
        return task

    def _timesheet_create_task(self):
        """ All task created form sale order are marked as blocked task until
        the sale order has been paid.
        """
        res = super(SaleOrderLine, self)._timesheet_create_task()
        tasks = self.env['project.task']
        for task in res.values():
            tasks = tasks | task
        tasks.message_post(body=_(
            "This task will be blocked until the sale order has been paid"))
        return res


class SaleOrder(models.Model):

    _inherit = "sale.order"

    general_descripion = fields.Boolean(
        help="Check if you want to show(On reports and web views) a general "
        "description for this order and not its details(All Sale Order Lines)."
        " It's required set a Project product in the Page Project Description"
    )
    note2html = fields.Text(string="Converted RST", compute="_rst2html")
    project_product_id = fields.Many2one(
        'product.product', domain=[
            ('invoice_policy', '=', 'order'),
            ('product_tmpl_id.type', '=', 'service')],
        string="Project Product",
        help="This product will be used to show a general description of the "
        "order. All documents(Invoice, Reports) created from this order will "
        "show only this product and the total of the order")
    project_description = fields.Text(
        help="Description to be show in reports and invoice to describe "
        "the project")

    @api.depends('note')
    def _rst2html(self):
        for sale in self:
            sale.note2html = rst2html.html.rst2html(sale.note)

    @api.onchange('general_descripion')
    def onchange_general_descripion(self):
        """Adding default product if you want to show a general description for
        this order

        """
        self.update({
            'project_description': self.general_descripion and
            self.project_description,
            'project_product_id': self.general_descripion and
            self.env.ref('pima.project_product'),
        })

    @api.onchange('project_product_id')
    def onchange_project_product(self):
        """Adding a description for general project"""
        if self.project_product_id:
            self.update(
                {'project_description': (
                    self.project_product_id.description_sale or
                    self.project_product_id.name)}
            )

    @api.multi
    def order_lines_layouted(self):
        """Used to avoid sending the layout category if you only want to show a
        general description"""
        self.ensure_one()
        if not (self.general_descripion and self.project_product_id):
            return super(SaleOrder, self).order_lines_layouted()
        report_pages = [[]]
        report_pages[-1].append({
            'name': 'Uncategorized',
            'subtotal': 0,
            'pagebreak': 0,
            'lines': list(self.order_line)
        })
        return report_pages


class SalesChannel(models.Model):

    _inherit = "crm.team"

    address_id = fields.Many2one(
        'res.partner',
        string="Address to show in the Header of the sale Order")
