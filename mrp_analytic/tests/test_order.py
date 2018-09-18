# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.mrp_analytic.tests.common import TestMrpCommon
from odoo.addons.mrp.tests.test_order import TestMrpOrder


class TestMrpOrderAnalytic(TestMrpOrder, TestMrpCommon):

    def test_product_produce_3_with_analytic(self):
        """ Checking that the jousnal items created from this MO contain the
        analytic accounts correctly set"""
        acc = self.env['account.account'].search([('code', '=', '115.01.01')])
        self.env.ref('product.product_category_all').write(
            {'property_valuation': 'real_time',
             'property_stock_account_input_categ_id': acc.id,
             'property_stock_account_output_categ_id': acc.id})
        self.test_product_produce_3()
        move_obj = self.env['account.move']
        self.assertTrue(
            (self.last_mo.account_analytic_in_id |
             self.last_mo.account_analytic_out_id),
            'The MO does not have account analytic')
        for fmove in self.last_mo.move_finished_ids:
            # Checking analytic account
            am = move_obj.search([('stock_move_id', '=', fmove.id)])
            # Looking for the Journal entry related
            self.assertTrue(am, 'The move does not have an entry related')
            line = am.line_ids.filtered(
                lambda a: a.analytic_account_id ==
                self.last_mo.account_analytic_out_id)
            # It should have only one line with the same analytic
            self.assertEqual(
                len(line), 1,
                'There is more than one line with the same analytic')
            # The line must have debit
            self.assertTrue(line.credit > 0)

        for fmove in self.last_mo.move_raw_ids:
            # Checking analytic account
            am = move_obj.search([('stock_move_id', '=', fmove.id)])
            # Looking for the Journal entry related
            self.assertTrue(am, 'The move does not have an entry related')
            line = am.line_ids.filtered(
                lambda a: a.analytic_account_id ==
                self.last_mo.account_analytic_in_id)
            # It should have only one line with the same analytic
            self.assertEqual(
                len(line), 1,
                'There is more than one line with the same analytic')
            # The line must have credit
            self.assertTrue(line.debit > 0)
