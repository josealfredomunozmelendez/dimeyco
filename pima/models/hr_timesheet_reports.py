# coding: utf-8
from __future__ import division
import re

from odoo import models, fields, api, _
from openerp.tools.safe_eval import safe_eval

from . import rst2html


def clean_name(name):
    exp = r'\[.*?\]'
    text = name.strip()
    found = re.findall(exp, text)
    if found:
        for fou in found:
            text = text.replace(fou, '').strip()
    words = text.split(' ')
    if len(words) > 2:
        text = ' '.join([words[0], words[2]])
    return text


class HrTimesheetReportsBase(models.Model):

    _name = "hr.timesheet.reports.base"
    _inherit = ['mail.thread']

    @api.multi
    def _prepare_data(self, record):
        return {'author': clean_name(record.user_id.name),
                'description': record.name,
                'duration': record.unit_amount,
                'invoiceables_hours': record.invoiceables_hours,
                'to_invoice': record.to_invoice,
                'date': record.date,
                'analytic': record.account_id.name,
                'issue': record.issue_id.name,
                'line': False,  # TODO this can be deleted
                'invoice_id': record.invoice_id,
                'task_id': record.task_id,
                'record': record,
                'id': record.id}

    def _get_total_time(self, grouped, field):
        total_list = [g[field] for g in grouped]
        return sum(total_list)

    @api.multi
    def _get_report_inv(self):
        self.ensure_one()
        invoice_obj = self.env['account.invoice']
        domain_inv = \
            self.filter_invoice_id.domain if self.filter_invoice_id else []
        if not domain_inv:
            return ([], [], [], [], {})
        dom_inv = [len(d) > 1 and tuple(d) or d for d in safe_eval(domain_inv)]
        # Preparing grouped invoices due to it is 2 levels it need a
        # little extra Work.
        elements = invoice_obj.read_group(
            dom_inv,
            ['period_id', 'amount_total', 'amount_tax', 'amount_untaxed',
             'residual', 'partner_id'],
            ['period_id', 'amount_total', 'amount_tax', 'amount_untaxed',
             'residual'])
        grouped_by_currency = invoice_obj.read_group(
            dom_inv,
            ['currency_id', 'amount_total', 'amount_tax', 'amount_untaxed',
             'residual', 'partner_id'],
            ['currency_id', 'amount_total', 'amount_tax', 'amount_untaxed',
             'residual'])
        inv_line_obj = self.env['account.invoice.line']
        curr_obj = self.env['res.currency']
        grouped_by_product = {}
        ent_ids = [ent.id for ent in self.prod_ent_ids]
        train_ids = [ent.id for ent in self.prod_train_ids]
        cons_ids = [ent.id for ent in self.prod_cons_ids]
        all_ids = ent_ids + cons_ids + train_ids
        for gbc in grouped_by_currency:
            currency = gbc['currency_id']
            inv_line_ids = invoice_obj.search(
                dom_inv + [('currency_id', 'in', [currency[0]])])
            group_prod = inv_line_obj.read_group(
                [('invoice_id', 'in', inv_line_ids)],
                ['product_id', 'price_subtotal', ],
                ['product_id', 'price_subtotal', ])
            total_ent = sum([gr['price_subtotal'] for gr in group_prod
                             if gr['product_id'][0] in ent_ids])
            total_cons = sum([gr['price_subtotal'] for gr in group_prod
                              if gr['product_id'][0] in cons_ids])
            total_train = sum([gr['price_subtotal'] for gr in group_prod
                               if gr['product_id'][0] in train_ids])
            total_others = sum([gr['price_subtotal'] for gr in group_prod
                                if gr['product_id'][0] not in all_ids])
            total = total_ent + total_ent + total_train + total_others
            curr_from = self.currency_id
            curr_to = curr_obj.browse(currency[0])
            rate = curr_obj._get_conversion_rate(curr_from, curr_to)
            if not rate:
                UserWarning(_("Rate between currencies can not be 0"))
            grouped_by_product[gbc['currency_id'][1]] = {
                'enterprises': total_ent,
                'consultancy': total_cons,
                'others': total_others,
                'training': total_train,
                'pending': total_train,
                'total': total,
                'rate': rate,
                'total_in_control': round(total / rate, 2),
                'total_cons': round(total_cons / rate, 2),
                'total_train': round(total_train / rate, 2),
                'total_others': round(total_others / rate, 2),
                'total_lic': round(total_ent / rate, 2),
                'conversion_rate': curr_obj._get_conversion_rate(
                    curr_from, curr_to),
            }

        #  TODO: This must be a better way to achieve this list directly from
        #  search group on v8.0 for now the simplest way make a list with
        #  everything an group in the report itself
        invoices = invoice_obj.search(dom_inv)

        # Getting resumed numbers
        resumed_numbers = {
            'total_invoiced': sum([grouped_by_product[i]['total_in_control']
                                   for i in grouped_by_product])
        }
        return (elements, grouped_by_currency, invoices, grouped_by_product,
                resumed_numbers)

    @api.multi
    def _get_report_issue(self):
        issue_obj = self.env['project.issue']
        domain_issues = \
            self.filter_issue_id.domain if self.filter_issue_id else []
        if not domain_issues:
            return []
        dom_issues = [len(d) > 1 and tuple(d) or d
                      for d in safe_eval(domain_issues)]
        # Setting issues elements.
        issues_grouped = issue_obj.read_group(
            dom_issues, ['analytic_account_id'], ['analytic_account_id'])

        issues_all = []
        for issue in issues_grouped:
            analytic_id = issue.get('analytic_account_id')
            new_issue_dom = dom_issues + [('analytic_account_id', '=', analytic_id and analytic_id[0] or analytic_id)]  # noqa
            issue['children_by_stage'] = issue_obj.read_group(
                new_issue_dom, ['stage_id'], ['stage_id'],  # noqa
                orderby='stage_id asc') # noqa
            issues_all.append(issue)
        return issues_all

    @api.multi
    def _get_report_ts(self):
        self.ensure_one()
        timesheet_obj = self.env['account.analytic.line']
        domain = self.filter_id.domain
        dom = [len(d) > 1 and tuple(d) or d for d in safe_eval(domain)]
        timesheets = timesheet_obj.search(
            dom, order='account_id asc, user_id asc, date asc')  # noqa
        # Group elements
        res = []
        res_result = [self._prepare_data(tb) for tb in timesheets]  # noqa
        res = sorted(res_result, key=lambda k: k['issue'], reverse=True)
        grouped = timesheet_obj.read_group(
            dom, ['account_id', 'unit_amount', 'invoiceables_hours'],
            ['account_id'])
        grouped_month = timesheet_obj.read_group(
            dom, ['date', 'account_id', 'unit_amount', 'invoiceables_hours'],
            ['date'])
        grouped_by_user = timesheet_obj.read_group(
            dom, ['user_id', 'unit_amount', 'invoiceables_hours'],
            ['user_id'])
        # Separate per project (analytic)
        projects = set([l['analytic'] for l in res])
        return (grouped, grouped_month, projects, res, grouped_by_user)

    @api.multi
    def _get_total_inv_amount(self, grouped):
        self.ensure_one()
        pending = sum([gro['invoiceables_hours'] for gro in grouped])
        pending_inv = round(
            pending * self.product_id.list_price, 2)
        return pending_inv

    @api.multi
    def _get_result_ids(self):
        gi, gbc, ibrw, gbp, rn = self.sudo()._get_report_inv()  # noqa
        grouped, gbm, projects, res, gbu = self.sudo()._get_report_ts()  # noqa
        rn['pending'] = self.sudo()._get_total_inv_amount(grouped)  # noqa
        info = {
            'data': {},
            'resume': grouped,
            'resume_month': gbm,
            'resume_user': gbu,
            'resume_product': gbp,
            'invoices': ibrw,
            'issues': self.sudo()._get_report_issue(),
            'total_ts_bill_by_month': self._get_total_time(
                grouped, 'invoiceables_hours'),  # noqa
            'total_ts_by_month': self._get_total_time(grouped,
                                                      'unit_amount'),
            'periods': gi,
            'total_invoices': gbc,
            'resumed_numbers': rn,
        }
        for proj in projects:
            info['data'][proj] = [r for r in res if r['analytic'] == proj]
        return info

    @api.depends('comment_timesheet',
                 'comment_invoices',
                 'comment_issues')
    def _comment2html(self):
        self.cts2html = rst2html.html.rst2html(self.comment_timesheet)
        self.ci2html = rst2html.html.rst2html(self.comment_invoices)
        self.ciss2html = rst2html.html.rst2html(self.comment_issues)

    name = fields.Char('Report Title')
    comment_invoices = fields.Text('Comment about Invoices',
                                   help="It will appear just above "
                                   "list of invoices.")
    ci2html = fields.Text('Comments Invoices html',
                          compute='_comment2html',
                          help='It will appear just above '
                          'the resumed timesheets.')
    comment_timesheet = fields.Text('Comment about Timesheets',
                                    help='It will appear just above '
                                    'the resumed timesheets.')
    cts2html = fields.Text('Comments TS html',
                           compute='_comment2html',
                           help='It will appear just above '
                           'the resumed timesheets.')
    comment_issues = fields.Text('Comment about Timesheets',
                                 help='It will appear just above '
                                 'the resumed issues.')
    ciss2html = fields.Text('Comments Issues html',
                            compute='_comment2html',
                            help='It will appear just above '
                            'the resumed timesheets.')
    user_id = fields.Many2one(
        'res.users', 'Responsible',
        default=lambda self: self.env.uid,
        help='Owner of the report, generally the person that create it.')
    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        help='Contact which you will send this report.')
    filter_issue_id = fields.Many2one(
        'ir.filters', 'Issues',
        domain=[('model_id', 'ilike', 'project.issue')],
        help='Set the filter for issues TIP = go to issues and look for '
        ' the filter that adjust to your needs of issues to be shown.')
    filter_invoice_id = fields.Many2one(
        'ir.filters', 'Invoices',
        domain=[('model_id', 'ilike', 'account.invoice')],
        help='Filter of Invoices to be shown TIP = '
        'Go to Accounting/Customer '
        'Invoices in order to create the filter you want to show on this'
        'report.',)
    filter_id = fields.Many2one(
        'ir.filters', 'Filter',
        domain=[
            ('model_id', 'ilike', 'account.analytic.line')],
        help="Filter should be by date, group_by is ignored, the model "
        "which the filter should belong to is timesheet.")
    show_details = fields.Boolean('Show Detailed Timesheets')
    state = fields.Selection(
        [('draft', 'Draft'), ('sent', 'Sent')], 'Status', default='draft',
        help='Message sent already to customer (it will block edition)')
    company_id = fields.Many2one(
        'res.company', 'Company', help='Company which this report belongs to',
        default=lambda self: self.env['res.company']._company_default_get(
            'hr.timesheet.reports.base'))
    product_id = fields.Many2one(
        'product.product', 'Product to Compute Totals',
        help='This product will be used to compute totals')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        help='This product will be used to compute totals')
    prod_ent_ids = fields.Many2many(
        'product.product', 'prod_report_timesheet_rel1', 'report_id',
        'prod_ent_id', 'Products for Enterprises',
        help="All lines on invoices that have this product will be ignored as"
        " Effectivally Invoiced time already invoiced")
    prod_train_ids = fields.Many2many('product.product',
                                      'prod_report_timesheet_rel2',
                                      'report_id', 'prod_train_id',
                                      'Products for Training',
                                      help="All lines that have this "
                                      "products will "
                                      "Be ignored due to this is just "
                                      "for products")
    prod_cons_ids = fields.Many2many('product.product',
                                     'prod_report_timesheet_rel3',
                                     'report_id', 'prod_cons_id',
                                     'Products for Consultancy',
                                     help="All products here will be "
                                     "considered as consultancy"
                                     "then it will be compared by "
                                     "currency and by "
                                     "considering the product "
                                     "in this reports to use "
                                     "the unit_price and the currency")

    @api.multi
    def go_to_timesheet(self):
        self.ensure_one()
        context = dict(self._context)
        context.update({'ts_report_id': self.id})
        return {'type': 'ir.actions.act_window',
                'res_model': 'account.analytic.line',
                'name': 'Timesheet Activities Reported',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': self.filter_id.domain,
                'context': context}

    @api.multi
    def go_to_invoices(self):
        self.ensure_one()
        context = self.env._context
        context.update({
            'ts_report_id': self.id,
        })
        return {'type': 'ir.actions.act_window',
                'res_model': 'account.invoice',
                'name': 'Invoices Reported',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': self.filter_invoice_id.domain,
                'context': context,
                }

    @api.multi
    def go_to_issues(self):
        self.ensure_one()
        context = self.env._context
        context.update({'ts_report_id': self.id})
        return {'type': 'ir.actions.act_window',
                'res_model': 'project.issue',
                'name': 'Issues Reported',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': self.filter_issue_id.domain,
                'context': context,
                }

    @api.multi
    def send_by_email(self, cdsm=None):
        self.ensure_one()
        try:
            template_id = self.env.ref(
                'pima.email_reports_base')  # noqa
        except ValueError:
            template_id = False
        try:
            compose_form_id = self.env.ref(
                'mail.email_compose_message_wizard_form')  # noqa
        except ValueError:
            compose_form_id = False

        ctx = dict(self.env._context)
        ctx.update({
            'default_model': 'hr.timesheet.reports.base',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def mark_timesheet(self):
        return True

    @api.multi
    def clean_timesheet(self):
        """To be sure all timesheet lines are at least setted as billable
        100% in order to show correct first approach of numbers.
        """
        self.ensure_one()
        timesheet_obj = self.env['account.analytic.line']
        domain = self.filter_id.domain
        dom = [len(d) > 1 and tuple(d) or d for d in safe_eval(domain)]
        timesheets = timesheet_obj.search(
            dom + [('to_invoice', '=', False)])  # noqa
        # By default 100% wired to the one by default in db.
        # If you want another one overwrite this method or change the
        # rate on such record.
        timesheets.write({'to_invoice': 1})
        return True
