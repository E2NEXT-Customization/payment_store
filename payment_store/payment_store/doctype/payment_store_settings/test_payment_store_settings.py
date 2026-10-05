# Copyright (c) 2026, Developer and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestPaymentStoreSettings(FrappeTestCase):
	def test_roles_exist(self):
		roles = ["Payment Store Manager", "Payment Store Cashier", "Payment Store Auditor"]
		for role in roles:
			self.assertTrue(frappe.db.exists("Role", role))

	def test_workspace_exists(self):
		self.assertTrue(frappe.db.exists("Workspace", "Payment Store"))

	def test_settings_doctype(self):
		self.assertTrue(frappe.db.exists("DocType", "Payment Store Settings"))
		# check default value
		doc = frappe.get_doc("Payment Store Settings")
		self.assertEqual(doc.iqd_rounding_step, "250")
