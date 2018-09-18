# coding: utf-8
from odoo import models, fields


class HeldeskTeam(models.Model):

    _inherit = "helpdesk.team"

    project_id = fields.Many2one(
        "project.project",
        string="Support Project",
        help="The project where the task related to the tickets will be"
             " created")


class HeldeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    project_id = fields.Many2one(related="team_id.project_id")

    task_id = fields.Many2one(
        "project.task",
        help="Related task where the timesheet of this ticket will be loaded")
