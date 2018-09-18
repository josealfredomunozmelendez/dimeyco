# -*- coding: utf-8 -*-

from odoo.addons.mrp.tests import common


class TestMrpCommon(common.TestMrpCommon):

    @classmethod
    def generate_mo(cls, tracking_final='none', tracking_base_1='none',
                    tracking_base_2='none', qty_final=5, qty_base_1=4,
                    qty_base_2=1):
        """ This function generate a manufacturing order with one final
        product and two consumed product. Arguments allows to choose
        the tracking/qty for each different products. It returns the
        MO, used bom and the tree products.
        """
        res = super(TestMrpCommon, cls).generate_mo(
            tracking_final=tracking_final, tracking_base_1=tracking_base_1,
            tracking_base_2=tracking_base_2, qty_final=qty_final,
            qty_base_1=qty_base_1, qty_base_2=qty_base_2)
        res[2].standard_price = 20
        (res[3] | res[4]).write({'standard_price': 10})
        res[0].write(
            {'account_analytic_in_id':
             cls.env.ref('analytic.analytic_agrolait').id,
             'account_analytic_out_id':
             cls.env.ref('analytic.analytic_asustek').id,
             'analytic_tag_ids':
             [(6, 0, [cls.env.ref('analytic.tag_contract').id])]})
        cls.last_mo = res[0]
        return res
