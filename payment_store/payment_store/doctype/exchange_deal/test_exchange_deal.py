# Copyright (c) 2026, Developer and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestExchangeDeal(FrappeTestCase):
	def test_create_deal(self):
		deal = frappe.new_doc("Exchange Deal")
		deal.deal_type = "Sell FC"
		deal.deal_mode = "Official"
		deal.rate = 1320
		deal.foreign_amount = 100
		deal.iqd_amount = 132000
		deal.payment_mode = "Cash"
		self.assertEqual(deal.deal_type, "Sell FC")
