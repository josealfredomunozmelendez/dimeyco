# coding: utf-8
from openerp.tests.common import TransactionCase


class TestPrintReport(TransactionCase):

    def setUp(self):
        super(TestPrintReport, self).setUp()
        self.sale_obj = self.env['sale.order']

    def test_print_report(self):
        sale = self.sale_obj.search([], limit=1)
        if sale:
            self.assertTrue(sale.print_quotation(),
                            "The report was not generated")
            self.assertTrue(sale.action_quotation_send(),
                            "The action to send the report by mail was "
                            "no open")
