# Copyright (c) 2026, Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ExchangeDeal(Document):
	def validate(self):
		self.validate_rate_band()
		self.calculate_totals()
		
	def validate_rate_band(self):
		if self.approval_status == "Approved":
			return
			
		settings = frappe.get_single("Payment Store Settings")
		band = flt(settings.allowed_custom_rate_band)
		if band > 0 and self.deal_mode == "Custom":
			# Get active rate
			active_rate = frappe.db.get_value("PS Daily Rate", {"is_active": 1, "currency": self.currency}, ["company_buy_rate", "company_sell_rate"], as_dict=True)
			if active_rate:
				base_rate = active_rate.company_sell_rate if self.deal_type == "Sell" else active_rate.company_buy_rate
				diff = abs(flt(self.rate) - flt(base_rate))
				allowed_diff = flt(base_rate) * (band / 100.0)
				if diff > allowed_diff:
					self.approval_status = "Pending"
					frappe.msgprint("Rate is out of allowed band. Deal requires Manager approval.", alert=True)

	def calculate_totals(self):
		if self.last_edited_field == "usd_amount":
			self.iqd_amount = flt(self.usd_amount) * flt(self.rate)
		else:
			if flt(self.rate) > 0:
				self.usd_amount = flt(self.iqd_amount) / flt(self.rate)
				
		self.usd_amount = flt(self.usd_amount, 2)
		self.iqd_amount = flt(self.iqd_amount, 0)
		
		# For simplicity here, paid_amount = iqd_amount if Cash
		if self.payment_mode == "Cash":
			self.paid_amount = self.iqd_amount

	def on_submit(self):
		if self.approval_status == "Pending":
			frappe.throw("Cannot submit a deal pending approval.")
			
		self.update_wac(cancel=False)
		self.make_gl_entry()

	def on_cancel(self):
		if self.journal_entry:
			je = frappe.get_doc("Journal Entry", self.journal_entry)
			if je.docstatus == 1:
				je.cancel()
		self.update_wac(cancel=True)

	def update_wac(self, cancel=False):
		# Lock Settings
		frappe.db.sql("SELECT name FROM `tabPayment Store Settings` FOR UPDATE")
		settings = frappe.get_single("Payment Store Settings")
		
		for row in settings.currencies:
			if row.currency == self.currency:
				self.wac_before = flt(row.wac)
				old_qty = flt(row.running_quantity)
				old_wac = flt(row.wac)
				
				# If Buy, we add USD to cashbox. WAC changes.
				# If Sell, we subtract USD. WAC stays same.
				if self.deal_type == "Buy":
					if not cancel:
						new_qty = old_qty + flt(self.usd_amount)
						if new_qty > 0:
							new_wac = ((old_qty * old_wac) + (flt(self.usd_amount) * flt(self.rate))) / new_qty
						else:
							new_wac = old_wac
						
						row.wac = new_wac
						row.running_quantity = new_qty
						self.wac_after = new_wac
					else:
						# Revert exactly to what it was
						row.wac = flt(self.wac_before)
						row.running_quantity = old_qty - flt(self.usd_amount)
				else:
					# Sell
					if not cancel:
						self.wac_after = old_wac
						row.running_quantity = old_qty - flt(self.usd_amount)
					else:
						row.running_quantity = old_qty + flt(self.usd_amount)
						
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
		
		# WAC at posting
		cost_rate = flt(self.wac_before)
		if self.deal_type == "Buy":
			cost_rate = flt(self.rate)
		self.cost_rate = cost_rate
			
		if self.deal_type == "Sell":
			profit = flt(self.iqd_amount) - (flt(self.usd_amount) * cost_rate)
			self.profit_iqd = profit
			
			je.append("accounts", {
				"account": cashbox.iqd_account,
				"debit_in_account_currency": self.iqd_amount,
				"account_currency": frappe.defaults.get_global_default("default_currency") or "IQD"
			})
			je.append("accounts", {
				"account": cashbox.usd_account,
				"credit_in_account_currency": self.usd_amount,
				"exchange_rate": cost_rate,
				"account_currency": self.currency
			})
			if profit != 0:
				je.append("accounts", {
					"account": settings.exchange_profit_loss_account,
					"credit_in_account_currency": profit if profit > 0 else 0,
					"debit_in_account_currency": abs(profit) if profit < 0 else 0,
					"account_currency": frappe.defaults.get_global_default("default_currency") or "IQD"
				})
		elif self.deal_type == "Buy":
			je.append("accounts", {
				"account": cashbox.usd_account,
				"debit_in_account_currency": self.usd_amount,
				"exchange_rate": self.rate,
				"account_currency": self.currency
			})
			je.append("accounts", {
				"account": cashbox.iqd_account,
				"credit_in_account_currency": self.iqd_amount,
				"account_currency": frappe.defaults.get_global_default("default_currency") or "IQD"
			})
			
		je.flags.ignore_permissions = True
		je.submit()
		self.journal_entry = je.name
		self.db_update()
