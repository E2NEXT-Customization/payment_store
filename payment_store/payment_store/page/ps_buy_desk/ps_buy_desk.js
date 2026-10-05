frappe.pages['ps-buy-desk'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'شراء دولار',
		single_column: true
	});
	new payment_store.DeskCore(page.main, {
		page: page,
		title: 'شراء دولار',
		desk_type: 'buy'
	});
}