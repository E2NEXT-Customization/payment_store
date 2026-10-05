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
		`),this.bind_events(),this.load_data()}get_layout_html(){return["official_sell","custom_sell","buy"].includes(this.desk_type)?this.get_exchange_html():this.desk_type==="cash"?"<h3>\u0648\u0627\u062C\u0647\u0629 \u0627\u0644\u0642\u0627\u0635\u0629 (Cash In/Out/Transfer)</h3>":this.desk_type==="closing"?"<h3>\u0648\u0627\u062C\u0647\u0629 \u0627\u0644\u062C\u0631\u062F \u0648\u0627\u0644\u0625\u063A\u0644\u0627\u0642</h3>":this.desk_type==="control"?"<h3>\u0628\u0631\u062C \u0627\u0644\u0645\u0631\u0627\u0642\u0628\u0629 (\u0627\u0644\u0625\u062D\u0635\u0627\u0626\u064A\u0627\u062A)</h3>":""}get_exchange_html(){return`
			<div class="ps-exchange-card">
				<div class="ps-client-section">
					<label>\u0627\u0644\u0639\u0645\u064A\u0644</label>
					<div class="control-input-wrapper">
						<input type="text" class="form-control" id="ps-customer" placeholder="\u0627\u0628\u062D\u062B \u0628\u0627\u0644\u0627\u0633\u0645\u060C \u0627\u0644\u0647\u0627\u062A\u0641\u060C \u0623\u0648 \u0627\u0644\u0647\u0648\u064A\u0629...">
					</div>
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
		`}bind_events(){let t=this;this.wrapper.on("click",".ps-chip",function(){let e=parseFloat($(this).attr("data-val")),s=parseFloat(t.wrapper.find("#ps-usd").val())||0;t.wrapper.find("#ps-usd").val(s+e).trigger("input")}),this.wrapper.find("#ps-usd").on("input",function(){let e=parseFloat($(this).val())||0,s=parseFloat(t.wrapper.find("#ps-rate").val())||0;t.wrapper.find("#ps-iqd").val(Math.round(e*s))}),this.wrapper.find("#ps-iqd").on("input",function(){let e=parseFloat($(this).val())||0,s=parseFloat(t.wrapper.find("#ps-rate").val())||0;s>0&&t.wrapper.find("#ps-usd").val((e/s).toFixed(2))}),this.wrapper.find("#ps-submit-deal").on("click",function(){t.submit_deal()})}load_data(){frappe.call({method:"frappe.client.get_list",args:{doctype:"PS Daily Rate",filters:{is_active:1,currency:"USD"},fields:["company_sell_rate","company_buy_rate"]},callback:t=>{if(t.message&&t.message.length>0){let e=this.desk_type==="buy"?t.message[0].company_buy_rate:t.message[0].company_sell_rate;this.wrapper.find("#ps-rate").val(e)}}})}submit_deal(){let t=this.wrapper.find("#ps-usd").val(),e=this.wrapper.find("#ps-iqd").val(),s=this.wrapper.find("#ps-rate").val(),a=this.wrapper.find("#ps-customer").val();if(!t||!e||!a){frappe.msgprint("\u064A\u0631\u062C\u0649 \u0625\u062F\u062E\u0627\u0644 \u062C\u0645\u064A\u0639 \u0627\u0644\u062D\u0642\u0648\u0644 (\u0627\u0644\u0639\u0645\u064A\u0644 \u0648\u0627\u0644\u0645\u0628\u0644\u063A).");return}frappe.call({method:"frappe.client.insert",args:{doc:{doctype:"Exchange Deal",deal_type:this.desk_type==="buy"?"Buy":"Sell",deal_mode:this.desk_type==="custom_sell"?"Custom":"Official",currency:"USD",customer:a,cashbox:"Main Cashbox",rate:s,rate_source:this.desk_type==="custom_sell"?"Manual":"Board",usd_amount:t,iqd_amount:e,last_edited_field:"usd_amount",payment_mode:"Cash"}},callback:l=>{l.exc||frappe.call({method:"frappe.client.submit",args:{doc:l.message},callback:p=>{frappe.show_alert({message:"\u062A\u0645 \u062A\u0646\u0641\u064A\u0630 \u0627\u0644\u0635\u0641\u0642\u0629 \u0628\u0646\u062C\u0627\u062D!",indicator:"green"}),this.wrapper.find("#ps-usd").val("").trigger("input")}})}})}};})();
//# sourceMappingURL=ps_desk_core.bundle.MWZPTJTP.js.map
