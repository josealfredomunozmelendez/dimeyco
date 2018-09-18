# coding: utf-8
from __future__ import division

from odoo import fields, models, api


class AccountBudget(models.Model):
    _inherit = "crossovered.budget"

    use_cost = fields.Boolean(
        help="Used to compute costs on employees "
             "(Dates matter to be used)"
    )
    rate_usd = fields.Float(
        default=1.0,
        help="The conversion analysis is never the real one, then "
             "with this we can have an amount in th company currency "
             "and then properly exchange to usd using this factor as a "
             "reference always then with the execution we can see what "
             "was the real amount in usd."
    )
    cost_share = fields.Float(
        default=0.0,
        help="Percentage that this budget represent of the total "
             "Employee costs."
    )
    theoretical_timesheet = fields.Float(
        compute='_compute_amount',
        help="Summarize theoretical timesheet on employees which are cost."
    )
    hours_invoice = fields.Float(
        compute='_compute_amount',
        help="Summarize Invoiceable Hours on employees which are cost."
    )
    hours_informed = fields.Float(
        compute='_compute_amount',
        help="Summarize Informed Hours on employees which are cost."
    )
    planned_income = fields.Float(
        compute='_compute_amount',
        help="Amount of income earned in this budget."
    )
    planned_expense = fields.Float(
        compute='_compute_amount',
        help="Amount of expense spent in this budget."
    )
    practical_income = fields.Float(
        compute='_compute_amount',
        help="Amount of income executed in this budget."
    )
    practical_expense = fields.Float(
        compute='_compute_amount',
        help="Amount of expense spent in this budget."
    )
    theoretical_income = fields.Float(
        compute='_compute_amount',
        help="Amount of income expected in this budget."
    )
    theoretical_expense = fields.Float(
        compute='_compute_amount',
        help="Amount of expense expected in this budget."
    )
    cost_per_hour = fields.Float(
        compute='_compute_amount',
        help="Cost of Employee per hour."
    )
    employee_cost = fields.Float(
        compute='_compute_amount',
        help="Amount of Employee Costs in the company."
    )
    planned_amount = fields.Float(
        compute='_compute_amount',
        help='Planned Amount for this Budget'
    )
    practical_amount = fields.Float(
        compute='_compute_amount',
        help='Practical Amount for this Budget'
    )
    theoretical_amount = fields.Float(
        compute='_compute_amount',
        help='Theoretical Amount for this Budget'
    )
    color = fields.Integer(
        help="Color"
    )

    _sql_constraints = [
        ('rate_usd_exist',
         'CHECK (rate_usd>=0.0)',
         'A negative or zero rate does not make sense please try a proper '
         'value.')
    ]

    @api.depends()
    def _compute_amount(self):
        emp_obj = self.env['hr.employee']
        emp_ids = emp_obj.search([('is_cost', '=', True)])
        theoretical_timesheet = sum(emp_ids.mapped('theoretical_timesheet'))
        hours_invoice = sum(emp_ids.mapped('hours_invoice'))
        hours_informed = sum(emp_ids.mapped('hours_informed'))
        employee_cost = sum([
            emp.current_cost * emp.hours_informed for emp in emp_ids])
        for budget in self:
            planned_amount = 0.0
            practical_amount = 0.0
            theoretical_amount = 0.0
            planned_income = 0.0
            planned_expense = 0.0
            practical_income = 0.0
            practical_expense = 0.0
            theoretical_income = 0.0
            theoretical_expense = 0.0
            for cbl in budget.crossovered_budget_line:
                planned = cbl.planned_amount
                practical = cbl.practical_amount
                theoretical = cbl.theoritical_amount
                planned_amount += planned
                practical_amount += practical
                theoretical_amount += theoretical
                planned_income += planned if planned > 0 else 0
                planned_expense += planned if planned < 0 else 0
                practical_income += practical if practical > 0 else 0
                practical_expense += practical if practical < 0 else 0
                theoretical_income += theoretical if theoretical > 0 else 0
                theoretical_expense += theoretical if theoretical < 0 else 0
            cost_per_hour = (
                employee_cost / hours_informed if hours_informed else 0.0)
            budget.update(dict(
                planned_amount=planned_amount,
                practical_amount=practical_amount,
                theoretical_amount=theoretical_amount,
                planned_income=planned_income,
                planned_expense=-planned_expense,
                practical_income=practical_income,
                practical_expense=-practical_expense,
                theoretical_income=theoretical_income,
                theoretical_expense=-theoretical_expense,
                theoretical_timesheet=theoretical_timesheet,
                hours_invoice=hours_invoice,
                hours_informed=hours_informed,
                employee_cost=employee_cost,
                cost_per_hour=cost_per_hour,
            ))


class AccountBudgetLine(models.Model):
    _inherit = "crossovered.budget.lines"

    description = fields.Char()
    amount_usd = fields.Float(
        compute="_compute_amount_usd",
        help="Amount in usd, this will always be used to analyze with "
             "the employees behavior (TODO: make it configurable) "
    )

    @api.depends('planned_amount')
    @api.multi
    def _compute_amount_usd(self):
        for line in self:
            amount = round(
                line.planned_amount/line.crossovered_budget_id.rate_usd, 2)
            line.amount_usd = amount
