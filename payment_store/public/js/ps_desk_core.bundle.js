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
		if (this.desk_type === 'cash') return `<h3>واجهة القاصة (Cash In/Out/Transfer)</h3>`;
		if (this.desk_type === 'closing') return `<h3>واجهة الجرد والإغلاق</h3>`;
		if (this.desk_type === 'control') return `<h3>برج المراقبة (الإحصائيات)</h3>`;
		return ``;
	}

	get_exchange_html() {
		let rate_readonly = this.desk_type === 'official_sell' ? 'readonly' : '';
		return `
			<div class="ps-exchange-card">
				<div class="ps-client-section">
					<label>العميل</label>
					<div class="control-input-wrapper">
						<input type="text" class="form-control" id="ps-customer" placeholder="ابحث بالاسم، الهاتف، أو الهوية...">
					</div>
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
		let customer = this.wrapper.find('#ps-customer').val();
		
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
};
