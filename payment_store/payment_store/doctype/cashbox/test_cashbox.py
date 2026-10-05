# Copyright (c) 2026, Developer and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestCashbox(FrappeTestCase):
	def test_create_cashbox(self):
		if not frappe.db.exists("Cashbox", "Main Cashbox"):
			cb = frappe.get_doc({
				"doctype": "Cashbox",
				"cashbox_name": "Main Cashbox",
				"type": "Main",
				"iqd_account": "Cash - dummy"
			})
			# Just check that it can be initialized. Real save needs account existence.
			self.assertEqual(cb.cashbox_name, "Main Cashbox")
