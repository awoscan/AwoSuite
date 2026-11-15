# AWO Suite for ERPNext & Frappe (`awo_suite` v2.2.0)

Official **MIT-licensed thin adapter** connecting **ERPNext (v14 / v15 / Frappe Cloud)** to the **AWO Universal API v1**.

## Included Wave 1 Pilot Integrations

1. **AwoExpense (`Expense Claim` & `Purchase Invoice`):**
   - Evaluates multi-rate VAT/KDV splits, non-deductible expense disallowance (KKEG), per-diem (`harcırah`), and mileage allowances.
   - Enforces mandatory **Human-in-the-Loop** financial approval (`postingAllowed = false` until an explicit approver confirms an unaltered `payloadDigest`).
   - Appends every evaluation and approval to a **SHA-256 hash-chained immutable audit log** (`/api/v1/audit/logs`) with idempotency protection.
2. **AwoBom (`BOM` & `Item` Costing Studio):**
   - Reuses the exact same `AwoUniversalClient` and tenant session token (`awoa1.*`) to compute scrap-adjusted multi-component material costs, workstation routing operation minutes, factory overhead (`%`), and target gross margin unit selling price.

## Installation (Frappe Bench / Frappe Cloud)

```bash
bench get-app https://github.com/awoscan/AwoSuite --branch main
bench --site your-site.erpnext.com install-app awo_suite
bench --site your-site.erpnext.com migrate
```

## Configuration (`AWO Integration Settings`)

1. Open **AWO Integration Settings** in Frappe Desk.
2. Set **API Base URL** (`https://awosign.awoscan.com` by default) and **Tenant ID** (e.g. your site domain).
3. **Free Core Mode:** Works immediately with zero license key (up to 5 expense lines / claim and 8 BOM components).
4. **PRO Adapter Mode:** Enter your `AWO-Guard` license key (`AwoExpense ERP Adapter` `$99/yr`, `AwoBom ERP Adapter` `$149/yr`, `AWO Manufacturing Pack` `$249/yr`, or `AWO All-Access Enterprise` `$299/yr`) and click **Bind Tenant Session**.
