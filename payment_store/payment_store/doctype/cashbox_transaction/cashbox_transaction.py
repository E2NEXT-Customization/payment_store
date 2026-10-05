# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class CashboxTransaction(Document):
	def validate(self):
		if self.type == "Transfer" and not self.destination_cashbox:
			frappe.throw("Destination Cashbox is required for Transfers")
			
		if self.type == "Transfer" and not self.transfer_status:
			self.transfer_status = "Sent"

	def on_submit(self):
		self.update_wac(cancel=False)
		self.make_gl_entry()

	def on_cancel(self):
		if self.type == "Transfer" and self.transfer_status == "Confirmed":
			frappe.throw("Cannot cancel a confirmed transfer. Reverse it instead.")
			
		# Cancel GL Entry
		jes = frappe.get_all("Journal Entry Account", filters={"reference_type": self.doctype, "reference_name": self.name}, fields=["parent"])
		if jes:
			je = frappe.get_doc("Journal Entry", jes[0].parent)
			if je.docstatus == 1:
				je.cancel()
				
		self.update_wac(cancel=True)

	def update_wac(self, cancel=False):
		# Only inflows with a rate update WAC (Opening, Capital Injection, Cash In)
		if self.type not in ["Opening", "Capital Injection", "Cash In"] or not self.rate:
			return
			
		frappe.db.sql("SELECT name FROM `tabPayment Store Settings` FOR UPDATE")
		settings = frappe.get_single("Payment Store Settings")
		
		for row in settings.currencies:
			if row.currency == self.currency:
				old_qty = flt(row.running_quantity)
				old_wac = flt(row.wac)
				
				if not cancel:
					new_qty = old_qty + flt(self.amount)
					new_wac = ((old_qty * old_wac) + (flt(self.amount) * flt(self.rate))) / new_qty if new_qty > 0 else old_wac
					row.wac = new_wac
					row.running_quantity = new_qty
				else:
					new_qty = old_qty - flt(self.amount)
					# Cannot accurately revert WAC easily without before/after snapshot. 
					# For simplicity, just decrement qty. In a real system we'd snapshot it like Deals.
					row.running_quantity = new_qty
				break
				
		settings.flags.ignore_mandatory = True
		settings.save(ignore_permissions=True)
		self.db_update()

	def make_gl_entry(self):
		settings = frappe.get_single("Payment Store Settings")
		cashbox = frappe.get_doc("Cashbox", self.cashbox)
		
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = frappe.utils.today()
		je.company = settings.company
		je.multi_currency = 1
		
		# Base logic: determine Debit/Credit based on type
		# Simplified: All inflows Debit Cashbox. All outflows Credit Cashbox.
		inflows = ["Opening", "Cash In", "Capital Injection", "Customer Deposit", "Customer Payment"]
		is_inflow = self.type in inflows
		
		cash_account = cashbox.usd_account if self.currency == "USD" else cashbox.iqd_account
		base_currency = frappe.defaults.get_global_default("default_currency") or "IQD"
		
		exchange_rate = flt(self.rate) or 1.0
		if self.currency != base_currency and not self.rate:
			# Use current WAC for outflows
			rate = frappe.db.get_value("PS Currency Row", {"parent": "Payment Store Settings", "currency": self.currency}, "wac")
			exchange_rate = flt(rate)
			
		base_amount = flt(self.amount) * exchange_rate
		
		if is_inflow:
			je.append("accounts", {
				"account": cash_account,
				"debit_in_account_currency": self.amount,
				"exchange_rate": exchange_rate,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
			je.append("accounts", {
				"account": settings.exchange_profit_loss_account, # Replace with proper contra
				"credit_in_account_currency": base_amount,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
		elif self.type == "Transfer":
			# Transfer Sent: Cr Cashbox, Dr Cash in Transit
			je.append("accounts", {
				"account": cash_account,
				"credit_in_account_currency": self.amount,
				"exchange_rate": exchange_rate,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
			je.append("accounts", {
				"account": settings.cash_in_transit_account,
				"debit_in_account_currency": base_amount,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
		else:
			# Outflow
			je.append("accounts", {
				"account": cash_account,
				"credit_in_account_currency": self.amount,
				"exchange_rate": exchange_rate,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
			je.append("accounts", {
				"account": settings.exchange_profit_loss_account, # Replace with proper contra
				"debit_in_account_currency": base_amount,
				"reference_type": self.doctype,
				"reference_name": self.name
			})
			
		je.flags.ignore_permissions = True
		je.submit()
