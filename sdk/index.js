/**
 * @awoscan/awo-suite-sdk v2.2.0
 * Universal Cross-CMS Embed SDK & <awo-suite-widget> Web Component for all 23 AWO Suite B2B Tools (TR / EN)
 * https://awosuite.awoscan.com | https://awoscan.com
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.AWOSuiteSDK = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var TOOLS = [
    { slug: "awosign", prefix: "AWO-SIGN", name: "AwoSign", descEn: "QR vCard, CR80 Badge, Email Signature & IBAN Studio", descTr: "QR Kartvizit, Yaka Kartı, E-Posta İmzası & IBAN Stüdyosu" },
    { slug: "awoexpense", prefix: "AWO-EXP", name: "AwoExpense", descEn: "Receipt OCR, Expense Claim & Per Diem Studio", descTr: "Fiş OCR, Masraf Formu & Harcırah Stüdyosu" },
    { slug: "awosocial", prefix: "AWO-SOC", name: "AwoSocial", descEn: "B2B Social Media Banner & OpenGraph Visual Studio", descTr: "Kurumsal Sosyal Medya Görsel & Banner Stüdyosu" },
    { slug: "awoquote", prefix: "AWO-QUOTE", name: "AwoQuote", descEn: "Commercial Proforma Invoice & Price Quote Studio", descTr: "Proforma Fatura & Ticari Teklif Stüdyosu" },
    { slug: "awoservice", prefix: "AWO-SERV", name: "AwoService", descEn: "Field Service Job Order & Technical Report Studio", descTr: "Teknik Servis İş Emri & Saha Raporu Stüdyosu" },
    { slug: "awosite", prefix: "AWO-SITE", name: "AwoSite", descEn: "Construction Site Daily Log & HSE Inspection Studio", descTr: "Şantiye Günlük Raporu & İSG Denetim Stüdyosu" },
    { slug: "awobalance", prefix: "AWO-BAL", name: "AwoBalance", descEn: "B2B Current Account Reconciliation (BA/BS) Studio", descTr: "Cari Hesap & BA/BS Mutabakat Stüdyosu" },
    { slug: "awocontract", prefix: "AWO-CONT", name: "AwoContract", descEn: "Commercial Contract, NDA & SLA Template Studio", descTr: "Ticari Sözleşme, Gizlilik (NDA) & SLA Stüdyosu" },
    { slug: "awowarranty", prefix: "AWO-WARR", name: "AwoWarranty", descEn: "Digital Warranty Certificate & Serial QR Studio", descTr: "Dijital Garanti Belgesi & Seri No QR Stüdyosu" },
    { slug: "awoprofile", prefix: "AWO-PROF", name: "AwoProfile", descEn: "Corporate Capabilities Deck & Company Profile Studio", descTr: "Kurumsal Tanıtım Dosyası & Şirket Profili Stüdyosu" },
    { slug: "awocrm", prefix: "AWO-CRM", name: "AwoCRM", descEn: "B2B Sales Pipeline, Lead Scoring & Deal Desk Studio", descTr: "B2B Satış Hattı & Müşteri Takip Stüdyosu" },
    { slug: "awostock", prefix: "AWO-STCK", name: "AwoStock", descEn: "Warehouse Count Sheet, Delivery Note & QR Stock Studio", descTr: "Depo Sayım Tutanağı, İrsaliye & Stok QR Stüdyosu" },
    { slug: "awobom", prefix: "AWO-BOM", name: "AwoBom", descEn: "Manufacturing Bill of Materials & Unit Costing Studio", descTr: "Üretim Reçetesi (BOM) & Birim Maliyet Stüdyosu" },
    { slug: "awoforms", prefix: "AWO-FORM", name: "AwoForms", descEn: "B2B Order Intake, Dealer Application & Checklist Studio", descTr: "Kurumsal Sipariş, Bayilik Başvuru & Kontrol Formu Stüdyosu" },
    { slug: "awolabel", prefix: "AWO-LBL", name: "AwoLabel", descEn: "Industrial Product Label, GS1 Barcode & Pallet Tag Studio", descTr: "Endüstriyel Ürün Etiketi, Barkod & Palet Künyesi Stüdyosu" },
    { slug: "awotender", prefix: "AWO-TNDR", name: "AwoTender", descEn: "B2B RFQ / Tender Specification & Vendor Comparison Studio", descTr: "İhale Şartnamesi (RFQ) & Tedarikçi Kıyaslama Stüdyosu" },
    { slug: "awodealer", prefix: "AWO-DLR", name: "AwoDealer", descEn: "B2B Wholesale Price List & Tiered Dealer Catalog Studio", descTr: "Toptan Fiyat Listesi & Kademeli Bayi Kataloğu Stüdyosu" },
    { slug: "awopass", prefix: "AWO-PASS", name: "AwoPass", descEn: "Visitor Badge, Event Pass & Vehicle Entry Permit Studio", descTr: "Ziyaretçi Kartı, Etkinlik Yaka Kartı & Araç Giriş İzni Stüdyosu" },
    { slug: "awoasset", prefix: "AWO-ASST", name: "AwoAsset", descEn: "IT/Equipment Custody Handover (Zimmet) & QR Tag Studio", descTr: "Personel Zimmet Tutanağı & Demirbaş QR Etiketi Stüdyosu" },
    { slug: "awofleet", prefix: "AWO-FLT", name: "AwoFleet", descEn: "Corporate Vehicle Handover, Fuel Log & Fleet Inspection Studio", descTr: "Araç Teslim Tutanağı, Yakıt/KM & Filo Kontrol Stüdyosu" },
    { slug: "awopulse", prefix: "AWO-PLS", name: "AwoPulse", descEn: "B2B Customer Satisfaction (CSAT/NPS) & QR Survey Studio", descTr: "Müşteri Memnuniyet Anketi (CSAT/NPS) & QR Geri Bildirim Stüdyosu" },
    { slug: "awooutdoor", prefix: "AWO-OUT", name: "AwoOutdoor Media", descEn: "Outdoor Advertising Inventory & Media Plan Proposal Studio", descTr: "Açık Hava Reklam Envanteri & Medya Planlama Stüdyosu" },
    { slug: "awoproof", prefix: "AWO-PRF", name: "AwoProof", descEn: "Proof of Posting for Outdoor Advertising with GPS/Time Watermark", descTr: "Açık Hava Reklamı Yayın & Montaj Kanıtı (Proof of Posting) Stüdyosu" }
  ];

  function getStudioUrl(slug, lang) {
    var clean = String(slug || "awosign").toLowerCase().trim();
    var isEn = String(lang || "tr").toLowerCase() === "en";
    return "https://" + clean + ".awoscan.com/app/" + (isEn ? "en.html" : "");
  }

  function mountWidget(container, options) {
    var opts = options || {};
    var el = typeof container === "string" ? document.querySelector(container) : container;
    if (!el) return null;
    var iframe = document.createElement("iframe");
    iframe.src = getStudioUrl(opts.tool || "awosign", opts.lang || "tr");
    iframe.style.width = opts.width || "100%";
    iframe.style.height = opts.height || "780px";
    iframe.style.border = "1px solid #e2e8f0";
    iframe.style.borderRadius = "12px";
    iframe.setAttribute("loading", "lazy");
    iframe.setAttribute("allow", "clipboard-write");
    el.innerHTML = "";
    el.appendChild(iframe);
    return iframe;
  }

  if (typeof window !== "undefined" && window.customElements && !window.customElements.get("awo-suite-widget")) {
    var AwoWidget = function () {
      return Reflect.construct(HTMLElement, [], AwoWidget);
    };
    AwoWidget.prototype = Object.create(HTMLElement.prototype);
    AwoWidget.prototype.connectedCallback = function () {
      mountWidget(this, {
        tool: this.getAttribute("tool") || "awosign",
        lang: this.getAttribute("lang") || "tr",
        height: this.getAttribute("height") || "780px"
      });
    };
    window.customElements.define("awo-suite-widget", AwoWidget);
  }

  return {
    version: "2.2.0",
    tools: TOOLS,
    getStudioUrl: getStudioUrl,
    mountWidget: mountWidget
  };
});

