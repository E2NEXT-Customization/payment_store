# Copyright (c) 2026, Developer and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestCashboxTransaction(FrappeTestCase):
	def test_create_transaction(self):
		tx = frappe.new_doc("Cashbox Transaction")
		tx.type = "Cash In"
		tx.amount = 500
		self.assertEqual(tx.type, "Cash In")
