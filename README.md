# AWO Suite by AwoScan

**23 bilingual (TR / EN) B2B business tools — QR business cards, email signatures, IBAN QR, quotes, warranty certificates, balance reconciliation and more.**
Runs in the browser, as an offline desktop PWA, as a WordPress plugin, and as browser / Odoo / Gmail add-ons.

🌐 **Website:** https://awosuite.awoscan.com · 🇬🇧 https://awosuite.awoscan.com/en.html
🏢 **Publisher:** [AwoScan](https://awoscan.com) · ✉️ hello@awoscan.com

[English](#-english) · [Türkçe](#-türkçe)

---

## ✅ Official Store Listings / Resmi Mağaza Sayfaları

| Platform | Listing | Status |
| :--- | :--- | :---: |
| **Chrome Web Store** | [AwoSign: QR Business Card, Email Signature & IBAN Studio](https://chromewebstore.google.com/detail/awosign-qr-business-card/nefanmmgopkjebmmbboomkpaacnmjnib) | ✅ Live |
| **Firefox Add-ons (AMO)** | [AwoSign](https://addons.mozilla.org/en-US/firefox/addon/awosign/) | ✅ Live |
| **WordPress.org** | [AwoSign](https://wordpress.org/plugins/awosign/) · [AwoQuote](https://wordpress.org/plugins/awoquote/) | ✅ Live |
| **Odoo Apps Store** | [16.0](https://apps.odoo.com/apps/modules/16.0/awosign_corporate_identity) · [17.0](https://apps.odoo.com/apps/modules/17.0/awosign_corporate_identity) · [18.0](https://apps.odoo.com/apps/modules/18.0/awosign_corporate_identity) | ✅ Live |
| **Microsoft Edge Add-ons** | AwoSign | ⏳ In review |
| **Google Play** | AwoSign (`com.awoscan.awosign`) | ⏳ In review |

---

## 🇬🇧 English

### The 23 tools

| # | Tool | What it does | Live studio |
| :-: | :--- | :--- | :--- |
| 1 | **AwoSign** | QR vCard, CR80 staff badge, email signature & IBAN QR | [awosign.awoscan.com](https://awosign.awoscan.com) |
| 2 | **AwoExpense** | Receipt OCR, expense claims & accounting summary | [awoexpense.awoscan.com](https://awoexpense.awoscan.com) |
| 3 | **AwoSocial** | Holiday & special-day social posts in 10 languages | [awosocial.awoscan.com](https://awosocial.awoscan.com) |
| 4 | **AwoQuote** | Price quotes & proforma invoices with IBAN QR | [awoquote.awoscan.com](https://awoquote.awoscan.com) |
| 5 | **AwoService** | Signed field-service forms & handover reports | [awoservice.awoscan.com](https://awoservice.awoscan.com) |
| 6 | **AwoSite** | Construction-site photo log & A4 site reports | [awosite.awoscan.com](https://awosite.awoscan.com) |
| 7 | **AwoBalance** | Current-account balance & BA/BS reconciliation letters | [awobalance.awoscan.com](https://awobalance.awoscan.com) |
| 8 | **AwoContract** | Service/sales contracts, NDA & SLA templates | [awocontract.awoscan.com](https://awocontract.awoscan.com) |
| 9 | **AwoWarranty** | QR-verified warranty certificates & serial lookup | [awowarranty.awoscan.com](https://awowarranty.awoscan.com) |
| 10 | **AwoProfile** | A4 company profile & capabilities deck | [awoprofile.awoscan.com](https://awoprofile.awoscan.com) |
| 11 | **AwoCRM** | B2B customer cards & sales pipeline | [awocrm.awoscan.com](https://awocrm.awoscan.com) |
| 12 | **AwoStock** | Stock management, low-stock alerts & shelf QR labels | [awostock.awoscan.com](https://awostock.awoscan.com) |
| 13 | **AwoBom** | Bill of materials & unit costing | [awobom.awoscan.com](https://awobom.awoscan.com) |
| 14 | **AwoForms** | RFQ, order intake & lead forms | [awoforms.awoscan.com](https://awoforms.awoscan.com) |
| 15 | **AwoLabel** | Product labels, barcodes & pallet tags | [awolabel.awoscan.com](https://awolabel.awoscan.com) |
| 16 | **AwoTender** | Tender specifications & vendor comparison | [awotender.awoscan.com](https://awotender.awoscan.com) |
| 17 | **AwoDealer** | Wholesale price lists & dealer catalogs | [awodealer.awoscan.com](https://awodealer.awoscan.com) |
| 18 | **AwoPass** | Visitor badges, event passes & vehicle permits | [awopass.awoscan.com](https://awopass.awoscan.com) |
| 19 | **AwoAsset** | Equipment custody handover & QR asset tags | [awoasset.awoscan.com](https://awoasset.awoscan.com) |
| 20 | **AwoFleet** | Vehicle handover & fleet inspection | [awofleet.awoscan.com](https://awofleet.awoscan.com) |
| 21 | **AwoPulse** | Customer satisfaction (CSAT/NPS) QR surveys | [awopulse.awoscan.com](https://awopulse.awoscan.com) |
| 22 | **AwoOutdoor Media** | Outdoor advertising inventory & media planning | [awooutdoor.awoscan.com](https://awooutdoor.awoscan.com) |
| 23 | **AwoProof** | Proof of posting for outdoor advertising | [awoproof.awoscan.com](https://awoproof.awoscan.com) |

### Pricing
- **Free** version of every tool.
- **PRO** single tool: **$19 / year**.
- **AWO-SUITE Master Bundle** (all 23 tools): **$99 / year** — [Buy via Polar](https://buy.polar.sh/polar_cl_OBPp6aT5pZPKqUeMHq4iEXzFwgOzCt7LJIZWh33d2m8)

### Embed SDK (`sdk/`)
Embed any studio on any website (WordPress, Shopify, Wix, Webflow, Next.js…):

```html
<script src="https://awosign.awoscan.com/sdk/awo-embed.js" defer></script>
<awo-suite-widget tool="awosign" lang="en" height="780px"></awo-suite-widget>
```

```js
const AWOSuiteSDK = require("./sdk");
AWOSuiteSDK.getStudioUrl("awoquote", "en"); // https://awoquote.awoscan.com/app/en.html
AWOSuiteSDK.mountWidget("#box", { tool: "awowarranty", lang: "tr" });
```

### Machine-readable discovery (for AI agents)
- OpenAPI 3.1: https://awosuite.awoscan.com/openapi.json
- Catalog API: https://awosuite.awoscan.com/api/catalog
- MCP manifest: https://awosuite.awoscan.com/.well-known/mcp.json
- LLM docs: https://awoscan.com/llms.txt

### Privacy
The web/PWA studios work in the browser; company data you enter is stored locally on your device. PRO license checks send only the license key, the activating domain and an anonymous device fingerprint to the AwoScan license server.

---

## 🇹🇷 Türkçe

**AWO Suite**, KOBİ'ler ve kurumsal ekipler için **23 adet çift dilli (TR / EN) B2B iş aracından** oluşan bir pakettir. Tarayıcıda, çevrimdışı masaüstü uygulaması (PWA) olarak, WordPress eklentisi olarak ve Chrome / Firefox / Odoo / Gmail eklentisi olarak çalışır.

### Öne çıkanlar
- **AwoSign:** QR kartvizit (vCard), CR80 yaka kartı, e-posta imzası ve IBAN QR
- **AwoQuote:** Fiyat teklifi ve proforma fatura
- **AwoBalance:** Cari hesap ve BA/BS mutabakat mektubu (TTK m.94)
- **AwoWarranty:** QR doğrulamalı garanti belgesi
- **AwoOutdoor Media + AwoProof:** Açık hava reklam planlama ve yayın/montaj kanıtı

Tüm 23 aracın listesi yukarıdaki tabloda yer alır. Her aracın kendi canlı stüdyosu `https://<araç>.awoscan.com` adresindedir.

### Fiyatlandırma
- Her aracın **ücretsiz** sürümü vardır.
- Tekil **PRO**: **19 \$ / yıl**
- **AWO-SUITE Master Paket** (23 aracın tamamı): **99 \$ / yıl** — [Polar ile satın al](https://buy.polar.sh/polar_cl_OBPp6aT5pZPKqUeMHq4iEXzFwgOzCt7LJIZWh33d2m8)

### Gizlilik
Web/PWA stüdyoları tarayıcıda çalışır; girdiğiniz şirket bilgileri cihazınızda yerel olarak saklanır. PRO lisans doğrulamasında AwoScan lisans sunucusuna yalnızca lisans anahtarı, etkinleştirilen alan adı ve anonim bir cihaz parmak izi gönderilir.

---

## License / Lisans
The SDK in this repository is licensed under **GPL-2.0-or-later** (see [LICENSE](LICENSE)), the same license as the AWO Suite WordPress plugins.

## Security / Güvenlik
See [SECURITY.md](SECURITY.md).

© AwoScan — https://awoscan.com
