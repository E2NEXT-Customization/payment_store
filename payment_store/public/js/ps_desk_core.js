frappe.provide('payment_store');

payment_store.DeskCore = class DeskCore {
	constructor(wrapper, options) {
		this.wrapper = $(wrapper);
		this.options = options || {};
		this.setup();
	}

	setup() {
		this.wrapper.html(`
			<div class="ps-desk-container" dir="rtl">
				<div class="ps-header">
					<h2>${this.options.title || 'Desk'}</h2>
				</div>
				<div class="ps-body">
					<!-- Components will be rendered here -->
				</div>
			</div>
		`);
	}
};
