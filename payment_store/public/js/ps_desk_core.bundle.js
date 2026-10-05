frappe.provide('payment_store');

payment_store.DeskCore = class DeskCore {
	constructor(wrapper, options) {
		this.wrapper = $(wrapper);
		this.page = options.page;
		this.desk_type = options.desk_type; // 'official_sell', 'custom_sell', 'buy', 'cash', 'closing', 'control'
		this.title = options.title;
		this.setup();
	}

	setup() {
		this.page.set_title(this.title);
		this.wrapper.html(`
			<div class="ps-desk-container" dir="rtl">
				<div class="ps-live-strip">
					<span>الرصيد المتوقع:</span>
					<span class="ps-balance-usd">0.00 USD</span> | 
					<span class="ps-balance-iqd">0 IQD</span>
				</div>
				<div class="ps-main-layout">
					${this.get_layout_html()}
				</div>
			</div>
		`);
		
		this.bind_events();
		this.load_data();
	}
	
	get_layout_html() {
		if (['official_sell', 'custom_sell', 'buy'].includes(this.desk_type)) {
			return this.get_exchange_html();
		}
		if (this.desk_type === 'cash') return this.get_cash_html();
		if (this.desk_type === 'closing') return `<h3>واجهة الجرد والإغلاق (تحت الإنشاء)</h3>`;
		if (this.desk_type === 'control') return `<h3>برج المراقبة (تحت الإنشاء)</h3>`;
		return ``;
	}

	get_cash_html() {
		return `
			<div class="ps-exchange-card">
				<h4>تسجيل حركة صندوق</h4>
				<div class="row">
					<div class="col-xs-6">
						<label>نوع الحركة</label>
						<select class="form-control" id="ps-cash-type">
							<option value="Cash In">إيداع نقدي عادي</option>
							<option value="Cash Out">سحب نقدي عادي</option>
							<option value="Expense">مصروفات</option>
							<option value="Customer Deposit">إيداع أمانة عميل</option>
							<option value="Customer Withdrawal">سحب أمانة عميل</option>
							<option value="Transfer">تحويل إلى قاصة أخرى</option>
						</select>
					</div>
					<div class="col-xs-6">
						<label>العملة</label>
						<select class="form-control" id="ps-cash-currency">
							<option value="USD">USD</option>
							<option value="IQD">IQD</option>
						</select>
					</div>
				</div>
				<div class="row mt-3">
					<div class="col-xs-6">
						<label>المبلغ</label>
						<input type="number" class="form-control text-center" id="ps-cash-amount" placeholder="0">
					</div>
					<div class="col-xs-6">
						<label>الطرف المعني (عميل / قاصة)</label>
						<div id="ps-party-wrapper"></div>
					</div>
				</div>
				<div class="row mt-3">
					<div class="col-xs-12">
						<label>البيان / ملاحظات</label>
						<input type="text" class="form-control" id="ps-cash-remarks" placeholder="...">
					</div>
				</div>
				<div class="ps-action-section mt-4">
					<button class="btn btn-warning btn-block btn-lg" id="ps-submit-cash">تنفيذ الحركة</button>
				</div>
			</div>
		`;
	}

	get_exchange_html() {
		let rate_readonly = this.desk_type === 'official_sell' ? 'readonly' : '';
		return `
			<div class="ps-exchange-card">
				<div class="ps-client-section">
					<label>العميل</label>
					<div id="ps-customer-wrapper"></div>
				</div>
				<div class="ps-rate-section">
					<label>سعر الصرف</label>
					<input type="number" class="form-control text-center" id="ps-rate" ${rate_readonly} value="1320">
					<div class="ps-quote-lock">⏳ السعر صالح لمدة <span id="ps-countdown">--:--</span></div>
				</div>
				<div class="ps-amount-section">
					<div class="row">
						<div class="col-xs-6">
							<label>المبلغ (USD)</label>
							<input type="number" class="form-control text-center" id="ps-usd" placeholder="0.00">
						</div>
						<div class="col-xs-6">
							<label>المبلغ (IQD)</label>
							<input type="number" class="form-control text-center" id="ps-iqd" placeholder="0">
						</div>
					</div>
					<div class="ps-chips mt-2">
						<button class="btn btn-default btn-sm ps-chip" data-val="100">+100$</button>
						<button class="btn btn-default btn-sm ps-chip" data-val="200">+200$</button>
						<button class="btn btn-default btn-sm ps-chip" data-val="500">+500$</button>
						<button class="btn btn-default btn-sm ps-chip" data-val="1000">+1000$</button>
					</div>
				</div>
				<div class="ps-action-section mt-4">
					<button class="btn btn-primary btn-block btn-lg" id="ps-submit-deal">تنفيذ الصفقة</button>
				</div>
			</div>
		`;
	}

	bind_events() {
		const me = this;
		
		this.wrapper.on('click', '.ps-chip', function() {
			let val = parseFloat($(this).attr('data-val'));
			let current = parseFloat(me.wrapper.find('#ps-usd').val()) || 0;
			me.wrapper.find('#ps-usd').val(current + val).trigger('input');
		});

		this.wrapper.find('#ps-usd').on('input', function() {
			let usd = parseFloat($(this).val()) || 0;
			let rate = parseFloat(me.wrapper.find('#ps-rate').val()) || 0;
			me.wrapper.find('#ps-iqd').val(Math.round(usd * rate));
		});

		this.wrapper.find('#ps-iqd').on('input', function() {
			let iqd = parseFloat($(this).val()) || 0;
			let rate = parseFloat(me.wrapper.find('#ps-rate').val()) || 0;
			if(rate > 0) me.wrapper.find('#ps-usd').val((iqd / rate).toFixed(2));
		});
		
		this.wrapper.find('#ps-submit-deal').on('click', function() {
			me.submit_deal();
		});

		// Render Frappe Link Field for Customer if it's an exchange desk
		if (['official_sell', 'custom_sell', 'buy'].includes(this.desk_type)) {
			this.customer_field = frappe.ui.form.make_control({
				df: {
					fieldtype: "Link",
					options: "Customer",
					fieldname: "customer",
					label: "العميل",
					only_select: 0,
					placeholder: "ابحث أو أضف عميل جديد..."
				},
				parent: this.wrapper.find('#ps-customer-wrapper'),
				render_input: true
			});
		}

		// Render Frappe Link Field for Party (Cash Desk)
		if (this.desk_type === 'cash') {
			this.party_field = frappe.ui.form.make_control({
				df: {
					fieldtype: "Dynamic Link",
					options: "party_type", // Will be overridden manually via query if needed
					fieldname: "party",
					label: "الجهة",
					only_select: 0,
					placeholder: "اختر العميل أو القاصة الهدف..."
				},
				parent: this.wrapper.find('#ps-party-wrapper'),
				render_input: true
			});
			// Hack dynamic link to just act as a Customer link by default
			this.party_field.df.options = "Customer";
			
			this.wrapper.find('#ps-cash-type').on('change', function() {
				let type = $(this).val();
				if (type === 'Transfer') {
					me.party_field.df.options = "Cashbox";
				} else {
					me.party_field.df.options = "Customer";
				}
			});
			
			this.wrapper.find('#ps-submit-cash').on('click', function() {
				me.submit_cash_transaction();
			});
		}
	}

	load_data() {
		// Load active rate
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "PS Daily Rate",
				filters: { is_active: 1, currency: "USD" },
				fields: ["company_sell_rate", "company_buy_rate"]
			},
			callback: (r) => {
				if(r.message && r.message.length > 0) {
					let rate = this.desk_type === 'buy' ? r.message[0].company_buy_rate : r.message[0].company_sell_rate;
					this.wrapper.find('#ps-rate').val(rate);
				}
			}
		});
	}
	
	submit_deal() {
		let usd = this.wrapper.find('#ps-usd').val();
		let iqd = this.wrapper.find('#ps-iqd').val();
		let rate = this.wrapper.find('#ps-rate').val();
		let customer = this.customer_field.get_value();
		
		if (!usd || !iqd || !customer) {
			frappe.msgprint("يرجى إدخال جميع الحقول (العميل والمبلغ).");
			return;
		}
		
		frappe.call({
			method: "frappe.client.insert",
			args: {
				doc: {
					doctype: "Exchange Deal",
					deal_type: this.desk_type === 'buy' ? 'Buy' : 'Sell',
					deal_mode: this.desk_type === 'custom_sell' ? 'Custom' : 'Official',
					currency: "USD",
					customer: customer,
					cashbox: "Main Cashbox", // Hardcoded for demo, normally fetched from user
					rate: rate,
					rate_source: this.desk_type === 'custom_sell' ? 'Manual' : 'Board',
					usd_amount: usd,
					iqd_amount: iqd,
					last_edited_field: 'usd_amount',
					payment_mode: 'Cash'
				}
			},
			callback: (r) => {
				if(!r.exc) {
					frappe.call({
						method: "frappe.client.submit",
						args: { doc: r.message },
						callback: (res) => {
							frappe.show_alert({message: "تم تنفيذ الصفقة بنجاح!", indicator: 'green'});
							this.wrapper.find('#ps-usd').val('').trigger('input');
						}
					});
				}
			}
		});
	}

	submit_cash_transaction() {
		let type = this.wrapper.find('#ps-cash-type').val();
		let currency = this.wrapper.find('#ps-cash-currency').val();
		let amount = this.wrapper.find('#ps-cash-amount').val();
		let remarks = this.wrapper.find('#ps-cash-remarks').val();
		let party = this.party_field ? this.party_field.get_value() : null;
		
		if (!amount || amount <= 0) {
			frappe.msgprint("يرجى إدخال مبلغ صحيح.");
			return;
		}
		if (['Customer Deposit', 'Customer Withdrawal'].includes(type) && !party) {
			frappe.msgprint("يرجى اختيار العميل.");
			return;
		}
		if (type === 'Transfer' && !party) {
			frappe.msgprint("يرجى تحديد القاصة الهدف.");
			return;
		}

		let doc = {
			doctype: "Cashbox Transaction",
			type: type,
			cashbox: "Main Cashbox", // Hardcoded for demo
			currency: currency,
			amount: amount,
			remarks: remarks
		};

		if (type === 'Transfer') {
			doc.destination_cashbox = party;
			doc.transfer_status = "Sent";
		} else if (party) {
			doc.party_type = "Customer";
			doc.party = party;
		}

		frappe.call({
			method: "frappe.client.insert",
			args: { doc: doc },
			callback: (r) => {
				if(!r.exc) {
					frappe.call({
						method: "frappe.client.submit",
						args: { doc: r.message },
						callback: (res) => {
							frappe.show_alert({message: "تم تنفيذ الحركة بنجاح!", indicator: 'green'});
							this.wrapper.find('#ps-cash-amount').val('');
							if(this.party_field) this.party_field.set_value('');
						}
					});
				}
			}
		});
	}
};
