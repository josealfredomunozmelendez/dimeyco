# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestEmployeeUser(TransactionCase):
    """Test link correct user to selected employee or assign only selected
    group to selected employee's user."""

    def setUp(self):
        """Pseudo-constructor."""
        super(TestEmployeeUser, self).setUp()
        self.employee_wizard = self.env['employee_user.wizard']
        self.employee = self.env['hr.employee']
        self.partner = self.env['res.partner']
        self.resource = self.env['resource.resource']
        self.group_system = self.env.ref('base.group_system')

    def test_10_employee_with_user(self):
        """Case: employee with user linked. Exists user belong to
        Administration/Settings groups; after action, user not belong
        to that group."""
        partner_01 = self.partner.create({'name': 'User_01'})

        user_01 = {
            'login': 'proof01@gmail.com',
            'active': 1,
            'partner_id': partner_01.id,
            'groups_id':  [(4, self.group_system.id)],
        }

        resource_01 = {
            'name': 'Emplo_01',
            'active': 1,
            'time_efficiency': 1,
            'resource_type': 'user',
            'user_id': self.env['res.users'].create(user_01).id,
        }
        resource_01 = self.resource.create(resource_01)
        emp_01 = {
            'resource_id': resource_01.id,
            'work_email': 'proof01@gmail.com',
        }

        employee_test = self.employee.create(emp_01)
        group_test = self.env.ref('hr.group_hr_manager')
        employee_wz = self.employee_wizard.sudo().with_context(
            {'active_ids': [employee_test.id, ]}).create(
                {'group_id': group_test.id})
        employee_wz.link_user()
        user = employee_test.user_id
        self.assertIn(group_test, user.groups_id, '*** Linked user does not \
                      belong to selected group ***')
