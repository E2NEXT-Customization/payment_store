(()=>{frappe.provide("payment_store");payment_store.DeskCore=class{constructor(t,e){this.wrapper=$(t),this.page=e.page,this.desk_type=e.desk_type,this.title=e.title,this.setup()}setup(){this.page.set_title(this.title),this.wrapper.html(`
			<div class="ps-desk-container" dir="rtl">
				<div class="ps-live-strip">
					<span>\u0627\u0644\u0631\u0635\u064A\u062F \u0627\u0644\u0645\u062A\u0648\u0642\u0639:</span>
					<span class="ps-balance-usd">0.00 USD</span> | 
					<span class="ps-balance-iqd">0 IQD</span>
				</div>
				<div class="ps-main-layout">
					${this.get_layout_html()}
				</div>
			</div>
		`),this.bind_events(),this.load_data()}get_layout_html(){return["official_sell","custom_sell","buy"].includes(this.desk_type)?this.get_exchange_html():this.desk_type==="cash"?this.get_cash_html():this.desk_type==="closing"?"<h3>\u0648\u0627\u062C\u0647\u0629 \u0627\u0644\u062C\u0631\u062F \u0648\u0627\u0644\u0625\u063A\u0644\u0627\u0642 (\u062A\u062D\u062A \u0627\u0644\u0625\u0646\u0634\u0627\u0621)</h3>":this.desk_type==="control"?"<h3>\u0628\u0631\u062C \u0627\u0644\u0645\u0631\u0627\u0642\u0628\u0629 (\u062A\u062D\u062A \u0627\u0644\u0625\u0646\u0634\u0627\u0621)</h3>":""}get_cash_html(){return`
			<div class="ps-exchange-card">
				<h4>\u062A\u0633\u062C\u064A\u0644 \u062D\u0631\u0643\u0629 \u0635\u0646\u062F\u0648\u0642</h4>
				<div class="row">
					<div class="col-xs-6">
						<label>\u0646\u0648\u0639 \u0627\u0644\u062D\u0631\u0643\u0629</label>
						<select class="form-control" id="ps-cash-type">
							<option value="Cash In">\u0625\u064A\u062F\u0627\u0639 \u0646\u0642\u062F\u064A \u0639\u0627\u062F\u064A</option>
							<option value="Cash Out">\u0633\u062D\u0628 \u0646\u0642\u062F\u064A \u0639\u0627\u062F\u064A</option>
							<option value="Expense">\u0645\u0635\u0631\u0648\u0641\u0627\u062A</option>
							<option value="Customer Deposit">\u0625\u064A\u062F\u0627\u0639 \u0623\u0645\u0627\u0646\u0629 \u0639\u0645\u064A\u0644</option>
							<option value="Customer Withdrawal">\u0633\u062D\u0628 \u0623\u0645\u0627\u0646\u0629 \u0639\u0645\u064A\u0644</option>
							<option value="Transfer">\u062A\u062D\u0648\u064A\u0644 \u0625\u0644\u0649 \u0642\u0627\u0635\u0629 \u0623\u062E\u0631\u0649</option>
						</select>
					</div>
					<div class="col-xs-6">
						<label>\u0627\u0644\u0639\u0645\u0644\u0629</label>
						<select class="form-control" id="ps-cash-currency">
							<option value="USD">USD</option>
							<option value="IQD">IQD</option>
						</select>
					</div>
				</div>
				<div class="row mt-3">
					<div class="col-xs-6">
						<label>\u0627\u0644\u0645\u0628\u0644\u063A</label>
						<input type="number" class="form-control text-center" id="ps-cash-amount" placeholder="0">
					</div>
					<div class="col-xs-6">
						<label>\u0627\u0644\u0637\u0631\u0641 \u0627\u0644\u0645\u0639\u0646\u064A (\u0639\u0645\u064A\u0644 / \u0642\u0627\u0635\u0629)</label>
						<div id="ps-party-wrapper"></div>
					</div>
				</div>
				<div class="row mt-3">
					<div class="col-xs-12">
						<label>\u0627\u0644\u0628\u064A\u0627\u0646 / \u0645\u0644\u0627\u062D\u0638\u0627\u062A</label>
						<input type="text" class="form-control" id="ps-cash-remarks" placeholder="...">
					</div>
				</div>
				<div class="ps-action-section mt-4">
					<button class="btn btn-warning btn-block btn-lg" id="ps-submit-cash">\u062A\u0646\u0641\u064A\u0630 \u0627\u0644\u062D\u0631\u0643\u0629</button>
				</div>
			</div>
		`}get_exchange_html(){return`
			<div class="ps-exchange-card">
				<div class="ps-client-section">
					<label>\u0627\u0644\u0639\u0645\u064A\u0644</label>
					<div id="ps-customer-wrapper"></div>
				</div>
				<div class="ps-rate-section">
					<label>\u0633\u0639\u0631 \u0627\u0644\u0635\u0631\u0641</label>
					<input type="number" class="form-control text-center" id="ps-rate" ${this.desk_type==="official_sell"?"readonly":""} value="1320">
					<div class="ps-quote-lock">\u23F3 \u0627\u0644\u0633\u0639\u0631 \u0635\u0627\u0644\u062D \u0644\u0645\u062F\u0629 <span id="ps-countdown">--:--</span></div>
				</div>
				<div class="ps-amount-section">
					<div class="row">
						<div class="col-xs-6">
							<label>\u0627\u0644\u0645\u0628\u0644\u063A (USD)</label>
							<input type="number" class="form-control text-center" id="ps-usd" placeholder="0.00">
						</div>
						<div class="col-xs-6">
							<label>\u0627\u0644\u0645\u0628\u0644\u063A (IQD)</label>
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
					<button class="btn btn-primary btn-block btn-lg" id="ps-submit-deal">\u062A\u0646\u0641\u064A\u0630 \u0627\u0644\u0635\u0641\u0642\u0629</button>
				</div>
			</div>
		`}bind_events(){let t=this;this.wrapper.on("click",".ps-chip",function(){let e=parseFloat($(this).attr("data-val")),s=parseFloat(t.wrapper.find("#ps-usd").val())||0;t.wrapper.find("#ps-usd").val(s+e).trigger("input")}),this.wrapper.find("#ps-usd").on("input",function(){let e=parseFloat($(this).val())||0,s=parseFloat(t.wrapper.find("#ps-rate").val())||0;t.wrapper.find("#ps-iqd").val(Math.round(e*s))}),this.wrapper.find("#ps-iqd").on("input",function(){let e=parseFloat($(this).val())||0,s=parseFloat(t.wrapper.find("#ps-rate").val())||0;s>0&&t.wrapper.find("#ps-usd").val((e/s).toFixed(2))}),this.wrapper.find("#ps-submit-deal").on("click",function(){t.submit_deal()}),["official_sell","custom_sell","buy"].includes(this.desk_type)&&(this.customer_field=frappe.ui.form.make_control({df:{fieldtype:"Link",options:"Customer",fieldname:"customer",label:"\u0627\u0644\u0639\u0645\u064A\u0644",only_select:0,placeholder:"\u0627\u0628\u062D\u062B \u0623\u0648 \u0623\u0636\u0641 \u0639\u0645\u064A\u0644 \u062C\u062F\u064A\u062F..."},parent:this.wrapper.find("#ps-customer-wrapper"),render_input:!0})),this.desk_type==="cash"&&(this.party_field=frappe.ui.form.make_control({df:{fieldtype:"Dynamic Link",options:"party_type",fieldname:"party",label:"\u0627\u0644\u062C\u0647\u0629",only_select:0,placeholder:"\u0627\u062E\u062A\u0631 \u0627\u0644\u0639\u0645\u064A\u0644 \u0623\u0648 \u0627\u0644\u0642\u0627\u0635\u0629 \u0627\u0644\u0647\u062F\u0641..."},parent:this.wrapper.find("#ps-party-wrapper"),render_input:!0}),this.party_field.df.options="Customer",this.wrapper.find("#ps-cash-type").on("change",function(){$(this).val()==="Transfer"?t.party_field.df.options="Cashbox":t.party_field.df.options="Customer"}),this.wrapper.find("#ps-submit-cash").on("click",function(){t.submit_cash_transaction()}))}load_data(){frappe.call({method:"frappe.client.get_list",args:{doctype:"PS Daily Rate",filters:{is_active:1,currency:"USD"},fields:["company_sell_rate","company_buy_rate"]},callback:t=>{if(t.message&&t.message.length>0){let e=this.desk_type==="buy"?t.message[0].company_buy_rate:t.message[0].company_sell_rate;this.wrapper.find("#ps-rate").val(e)}}})}submit_deal(){let t=this.wrapper.find("#ps-usd").val(),e=this.wrapper.find("#ps-iqd").val(),s=this.wrapper.find("#ps-rate").val(),l=this.customer_field.get_value();if(!t||!e||!l){frappe.msgprint("\u064A\u0631\u062C\u0649 \u0625\u062F\u062E\u0627\u0644 \u062C\u0645\u064A\u0639 \u0627\u0644\u062D\u0642\u0648\u0644 (\u0627\u0644\u0639\u0645\u064A\u0644 \u0648\u0627\u0644\u0645\u0628\u0644\u063A).");return}frappe.call({method:"frappe.client.insert",args:{doc:{doctype:"Exchange Deal",deal_type:this.desk_type==="buy"?"Buy":"Sell",deal_mode:this.desk_type==="custom_sell"?"Custom":"Official",currency:"USD",customer:l,cashbox:"Main Cashbox",rate:s,rate_source:this.desk_type==="custom_sell"?"Manual":"Board",usd_amount:t,iqd_amount:e,last_edited_field:"usd_amount",payment_mode:"Cash"}},callback:a=>{a.exc||frappe.call({method:"frappe.client.submit",args:{doc:a.message},callback:i=>{frappe.show_alert({message:"\u062A\u0645 \u062A\u0646\u0641\u064A\u0630 \u0627\u0644\u0635\u0641\u0642\u0629 \u0628\u0646\u062C\u0627\u062D!",indicator:"green"}),this.wrapper.find("#ps-usd").val("").trigger("input")}})}})}submit_cash_transaction(){let t=this.wrapper.find("#ps-cash-type").val(),e=this.wrapper.find("#ps-cash-currency").val(),s=this.wrapper.find("#ps-cash-amount").val(),l=this.wrapper.find("#ps-cash-remarks").val(),a=this.party_field?this.party_field.get_value():null;if(!s||s<=0){frappe.msgprint("\u064A\u0631\u062C\u0649 \u0625\u062F\u062E\u0627\u0644 \u0645\u0628\u0644\u063A \u0635\u062D\u064A\u062D.");return}if(["Customer Deposit","Customer Withdrawal"].includes(t)&&!a){frappe.msgprint("\u064A\u0631\u062C\u0649 \u0627\u062E\u062A\u064A\u0627\u0631 \u0627\u0644\u0639\u0645\u064A\u0644.");return}if(t==="Transfer"&&!a){frappe.msgprint("\u064A\u0631\u062C\u0649 \u062A\u062D\u062F\u064A\u062F \u0627\u0644\u0642\u0627\u0635\u0629 \u0627\u0644\u0647\u062F\u0641.");return}let i={doctype:"Cashbox Transaction",type:t,cashbox:"Main Cashbox",currency:e,amount:s,remarks:l};t==="Transfer"?(i.destination_cashbox=a,i.transfer_status="Sent"):a&&(i.party_type="Customer",i.party=a),frappe.call({method:"frappe.client.insert",args:{doc:i},callback:p=>{p.exc||frappe.call({method:"frappe.client.submit",args:{doc:p.message},callback:n=>{frappe.show_alert({message:"\u062A\u0645 \u062A\u0646\u0641\u064A\u0630 \u0627\u0644\u062D\u0631\u0643\u0629 \u0628\u0646\u062C\u0627\u062D!",indicator:"green"}),this.wrapper.find("#ps-cash-amount").val(""),this.party_field&&this.party_field.set_value("")}})}})}};})();
//# sourceMappingURL=ps_desk_core.bundle.ZJTK6Y45.js.map
