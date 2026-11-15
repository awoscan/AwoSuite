app_name = "awo_suite"
app_title = "AWO Suite Connector"
app_publisher = "AwoScan"
app_description = "AWO Universal API v1 Thin Adapter for ERPNext: AwoExpense (VAT, Human-in-the-Loop Approval & Hash-Chained Audit) + AwoBom (Scrap, Routing & Target Margin Costing)"
app_email = "hello@awoscan.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

doctype_js = {
    "Expense Claim": "public/js/expense_claim.js",
    "Purchase Invoice": "public/js/expense_claim.js",
    "BOM": "public/js/bom.js",
}
