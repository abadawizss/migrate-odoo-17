from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
import logging
_logger = logging.getLogger(__name__)



class TestZenBankGuarantees(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestZenBankGuarantees, self).setUp(*args, **kwargs)
        self.bank_guarantees_model = self.env['zen.bank.guarantees']
        self.partner_model = self.env['res.partner']
        self.sale_order_model = self.env['sale.order']
        return result

    def test_sale_order_count(self):
        partner = self.partner_model.create({'name': 'Test Partner'})
        sale_order = self.sale_order_model.create({'partner_id': partner.id})
        bank_guarantees = self.bank_guarantees_model.create({
            'customer_id': partner.id,
            'sales_order_id': sale_order.id,
            'issuing_bank': 'Test Bank',
            'type': 'bank_guarantee',
            'date_of_issuance': '2023-02-20',
            'release_due_date': '2023-03-20'
        })

        self.assertEqual(bank_guarantees.sale_order_count, 1)

    def test_action_view_sale_orders(self):
        partner = self.partner_model.create({'name': 'Test Partner'})
        _logger.info(":: Create partner id %s", partner)

        sale_order = self.sale_order_model.create({'partner_id': partner.id})
        _logger.info(":: Create sale_order id %s", sale_order)

        bank_guarantees = self.bank_guarantees_model.create({
            'customer_id': partner.id,
            'sales_order_id': sale_order.id,
            'issuing_bank': 'Test Bank',
            'type': 'bank_guarantee',
            'date_of_issuance': '2023-02-20',
            'release_due_date': '2023-03-20'
        })
        _logger.info(":: Create bank_guarantees id %s", bank_guarantees)


        action = bank_guarantees.action_view_sale_orders()
        _logger.info(":: Create action id %s", action)


        self.assertEqual(action['context']['search_default_zen_bank_guarantees_ids'][0], bank_guarantees.id)
        _logger.info(":: Create line id %s")
        self.assertEqual(action['context']['default_zen_bank_guarantees_ids'], [(4, [bank_guarantees.id])])
        self.assertEqual(action['domain'], [('zen_bank_guarantees_ids', 'in', [bank_guarantees.id])])

    def test_search_default_zen_bank_guarantees_ids(self):
        action = {'context': {'search_default_zen_bank_guarantees_ids': [10, 20, 30]}}
        _logger.info(":: Create action action %s", action)
        expected_value = 10
        _logger.info(":: Create expected_value action %s", action)

        self.assertEqual(action['context']['search_default_zen_bank_guarantees_ids'][0], expected_value)

