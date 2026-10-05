# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from payment_store.reconciliation.explainer import run_explainer
import json
import hashlib

class CashboxClosing(Document):
	def validate(self):
		self.calculate_expected()
		self.calculate_variance()
		
	def calculate_expected(self):
		if not self.cashbox: return
		cashbox = frappe.get_doc("Cashbox", self.cashbox)
		
		# Get GL balances for IQD and USD accounts
		iqd_bal = frappe.db.sql("""SELECT sum(debit_in_account_currency) - sum(credit_in_account_currency) FROM `tabGL Entry` WHERE account=%s AND is_cancelled=0""", cashbox.iqd_account)[0][0] or 0.0
		usd_bal = frappe.db.sql("""SELECT sum(debit_in_account_currency) - sum(credit_in_account_currency) FROM `tabGL Entry` WHERE account=%s AND is_cancelled=0""", cashbox.usd_account)[0][0] or 0.0
		
		self.expected = json.dumps({
			"IQD": iqd_bal,
			"USD": usd_bal
		})

	def calculate_variance(self):
		if not self.expected or not self.counts: return
		exp = json.loads(self.expected)
		
		# Sum physical counts
		counted = {"IQD": 0, "USD": 0}
		for row in self.counts:
			amt = float(row.denomination) * float(row.qty)
			if row.currency in counted:
				counted[row.currency] += amt
				
		self.counted_totals = json.dumps(counted)
		
		variance = {
			"IQD": counted["IQD"] - exp["IQD"],
			"USD": counted["USD"] - exp["USD"]
		}
		self.variance = json.dumps(variance)
		
		# Run Explainer offline detection
		explainer_res = run_explainer(self)
		self.explainer_result = json.dumps(explainer_res, ensure_ascii=False)

	def on_submit(self):
		# Lock cashbox for backdated entries
		frappe.db.set_value("Cashbox", self.cashbox, "locked_until", self.cutoff_datetime)
		
		# Post variance to Cash Over/Short account if applicable
		# Hash Z-Report
		data_str = f"{self.cashbox}{self.cutoff_datetime}{self.variance}"
		self.db_set("z_report_hash", hashlib.sha256(data_str.encode('utf-8')).hexdigest())
