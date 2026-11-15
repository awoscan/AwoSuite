/* global frappe, __ */
// AwoBom Thin Adapter for ERPNext BOM (Bill of Materials)
// Reuses AWO Universal API v1 for scrap-adjusted costing, routing ops & target margin simulation.

frappe.ui.form.on("BOM", {
  refresh(frm) {
    frm.add_custom_button(
      __("AWO: Unit Cost & Margin Sim"),
      () => {
        frappe.prompt(
          [
            {
              fieldtype: "Float",
              fieldname: "overhead_percent",
              label: __("Factory Overhead (%)"),
              default: 12,
              reqd: 1,
            },
            {
              fieldtype: "Float",
              fieldname: "target_margin_percent",
              label: __("Target Gross Margin (%)"),
              default: 30,
              reqd: 1,
            },
          ],
          (values) => {
            frappe.call({
              method: "awo_suite.api.bom.calculate_erpnext_bom",
              args: {
                doc_or_name: frm.doc,
                overhead_percent: values.overhead_percent,
                target_margin_percent: values.target_margin_percent,
              },
              freeze: true,
              freeze_message: __("Simulating BOM Cost & Margin via AWO Universal API..."),
              callback(r) {
                const res = r && r.message;
                if (!res || !res.ok) return;
                const s = res.summary;
                frappe.msgprint({
                  title: __("AwoBom — Manufacturing Cost & Target Margin"),
                  indicator: "blue",
                  message: `
                    <div style="line-height:1.7">
                      <div><strong>BOM:</strong> ${frappe.utils.escape_html(s.bomId)} (Batch: ${s.batchQuantity})</div>
                      <div><strong>Materials + Operations:</strong> ${s.totalMaterialCost} + ${s.totalOperationCost} = <b>${s.primeCost} ${s.currency}</b></div>
                      <div><strong>Overhead (${s.overheadPercent}%):</strong> ${s.overheadCost} ${s.currency}</div>
                      <div><strong>Unit Manufacturing Cost:</strong> <b>${s.unitCost} ${s.currency}</b></div>
                      <div><strong>Recommended Selling Price (${s.targetMarginPercent}% Margin):</strong> <b style="color:#0284c7">${s.recommendedUnitPrice} ${s.currency}</b></div>
                      <div><strong>Top Cost Driver:</strong> <code>${frappe.utils.escape_html(s.topCostDriverItemCode || "-")}</code></div>
                    </div>
                  `,
                });
              },
            });
          },
          __("AwoBom Margin Simulator"),
          __("Calculate")
        );
      },
      __("AWO Suite")
    );
  },
});
