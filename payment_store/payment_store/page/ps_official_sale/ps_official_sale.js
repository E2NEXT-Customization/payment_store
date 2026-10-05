frappe.pages['ps-official-sale'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'بيع دولار – سعر رسمي',
		single_column: true
	});
	new payment_store.DeskCore(page.main, {
		page: page,
		title: 'بيع دولار – سعر رسمي',
		desk_type: 'official_sell'
	});
}