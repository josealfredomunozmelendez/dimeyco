# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class Wizard(models.TransientModel):
    """Wizard to link an user to employee or assign
    default group if user are linked already."""

    _name = 'employee_user.wizard'

    group_id = fields.Many2one(
        'res.groups', string="Group to assign",
        ondelete='set null', required=True)

    @api.multi
    def link_user(self):
        self.ensure_one()
        # Groups to assign: selected one and employee
        emp_group = self.env.ref('base.group_user')
        recv_group = set([self.group_id.id, emp_group.id])
        # Dict to use in write method
        vals = {'groups_id': [(6, 0, list(recv_group))]}
        ids_employee = self._context.get('active_ids')
        employees = self.env['hr.employee'].browse(ids_employee)
        for employee in employees:
            if not employee.user_id:
                # Try to find an user with same email
                user_id = self.env['res.users'].search(
                    [('login', '=', employee.work_email)])
                # Only an user would be got, res_users_login_key constraint
                # Avoid existence of two users with the same email (login)
                if not user_id:
                    raise UserError(_(
                        "User not created. Doesn't exists an user with same"
                        " email address."))
                # Assign user and group
                employee.user_id = user_id.id
                user_id.write(vals)
                continue
            # Only assign group
            employee.user_id.write(vals)
