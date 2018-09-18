# coding: utf-8
from odoo import models, fields, api


class Project(models.Model):

    _inherit = "project.project"

    label_acronymous = fields.Char(
        copy="False",
        help="Acronymous to show as prefix in the display name for the tasks"
             " without parent Tasks")
    label_subtasks = fields.Char(
        copy="False",
        help="Acronymous to show as prefix in the display name for the tasks"
             " with parent Tasks")
    label_acronymous_subtasks = fields.Char(
        copy="False",
        help="Acronyms to show as prefix in the display name for the tasks"
             " with parent Tasks")

    def _compute_task_count(self):
        """ Modify the task count to only take into account the parent tasks
        that are not orphan tasks.
        """
        for project in self:
            project.task_count = len(self.env['project.task'].search([
                ('id', 'in', project.task_ids.mapped('id')),
                ('parent_id', '=', False),
            ]))


class ProjectTask(models.Model):

    _inherit = "project.task"

    order_id = fields.Many2one(
        "sale.order", related="sale_line_id.order_id",
        store=True, index=True,
        help="Only the tasks that are defined as Epic necessarily need this \n"
        "field set so that it can be defined as such.",
        copy="False", track_visibility="onchange")

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        compute='_compute_account_analytic_id',
        inverse='_set_account_analytic_id')

    ticket_id = fields.Many2one(
        "helpdesk.ticket", copy="False")
    product_id = fields.Many2one(
        related="sale_line_id.product_id", readonly=True)
    accepted = fields.Boolean(help='Check if this criterion apply',
                              track_visibility='onchange')
    label_subtasks = fields.Char(
        related="project_id.label_subtasks", readonly=True)
    # User Story Specific Information
    description = fields.Html(track_visibility="onchange")
    planned_hours = fields.Float(
        string='Initially Planned Hours',
        help='Estimated time to do the task, usually set by the project '
             'manager when the task is in draft state.',
        track_visibility="onchange")
    owner_id = fields.Many2one(
        'res.users',
        help="User Story's Owner, generally the person which asked to develop "
             "this feature on customer side",
        track_visibility='onchange')
    approving_id = fields.Many2one(
        'res.users',
        help="User which says this User Story must/can be done")
    billable_hours = fields.Float()
    difficulty_id = fields.Many2one(
        'project.task.estimation',
        help="How difficult/clear is this ")
    budget = fields.Float(help="Estimated budget in dollars")
    currency_id = fields.Many2one(
        'res.currency',
        help="Currency which the budget was planned on (default usd)",
        default=lambda self: self.env.ref('base.USD'))
    # Grouping Information for Mapping.
    group_id = fields.Many2one('project.task')
    list_id = fields.Many2one('project.task')
    layer_id = fields.Many2one('project.task')
    is_layer = fields.Boolean(help='Is Layer?', track_visibility='onchange')
    gap = fields.Text(track_visibility="onchange")
    asumption = fields.Text(track_visibility="onchange")
    implementation = fields.Text(track_visibility="onchange")

    @api.multi
    @api.depends('order_id.analytic_account_id')
    def _compute_account_analytic_id(self):
        """Getting analytic account from a sale order if current task was
        created from a sale order line"""
        for rec in self:
            analytic = rec.timesheet_ids.mapped('account_id')
            rec.analytic_account_id = (
                rec.order_id.analytic_account_id.id
                if not analytic else analytic[0].id)

    @api.multi
    def _set_account_analytic_id(self):
        """If someone changes the analytic account in the task their analytic
        lines created from their timesheets should be changed too"""
        for rec in self.filtered('analytic_account_id'):
            account_id = rec.analytic_account_id
            rec.timesheet_ids.write({'account_id': account_id.id})

    @api.model
    def default_get(self, field_list):
        res = super(ProjectTask, self).default_get(field_list)
        res.update({'name': ''})
        return res

    @api.multi
    def write(self, vals):
        """ This overwrite is by bug found trying to do track of fields.Html
        """
        res = super(ProjectTask, self).write(vals)
        if vals.get('description'):
            body = ('<ul><li>Description: %s</li></ul>') % vals['description']
            self.message_post(body=body)
        return res

    @api.multi
    def do_approval(self):
        template = self.env.ref('pima.appr_start_mail')
        for task in self:
            task.message_post_with_template(template.id,
                                            message_type='notification')
            task.write({'approving_id': self.env.user.id})
        return True

    @api.multi
    def ask_review(self):
        self.ensure_one()
        if not self.accepted:
            self.write({'stage_id': self.env.ref(
                'pima.project_stage_ask_review').id})
        return True

    @api.multi
    def approve(self):
        self.ensure_one()
        if not self.accepted:
            self.write({'stage_id': self.env.ref(
                'pima.project_stage_approve').id,
                'accepted': True})
        return True

    @api.multi
    def open_subtasks(self):
        self.ensure_one()
        action = self.env.ref('project.project_task_action_from_partner')
        [action_dict] = action.read([])
        ctx = dict(self._context)
        ctx.update({
            'search_default_parent_id': self.id,
            'default_parent_id': self.id})
        action_dict['context'] = ctx
        action_dict['domain'] = [("parent_id", "=", self.id)]
        return action_dict


class UserStoryDifficulty(models.Model):
    _name = 'project.task.estimation'
    _order = "points asc"
    _description = '''Based on scrum cards values for estimation but used for
user stories estimations'''

    name = fields.Char(required=True, translate=True)
    points = fields.Float(
        required=True,
        help="Just to give another value to criterias and User Stories."
             " With it you can set an order and a value in terms of"
             " effort")
    estimated = fields.Float(
        required=True,
        help="How many hour do you think it can take?")
    help = fields.Text(
        help="Explain what kind of User Stories can be on this level,"
             " tell your experience give examples and so on.")

    @api.multi
    def name_get(self):
        def _name_get(data_name):
            name = data_name.get('name', '')
            return data_name['id'], name
        res = []
        for difficulty in self:
            name = '[%s] %s points, represent %s hours' % (
                difficulty.name,
                difficulty.points,
                difficulty.estimated)
            my_dict = {'id': difficulty.id, 'name': name, }
            res.append(_name_get(my_dict))
        return res
