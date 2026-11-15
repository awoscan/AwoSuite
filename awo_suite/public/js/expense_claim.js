/* global frappe, __ */
// AwoExpense Thin Adapter for ERPNext Expense Claim & Purchase Invoice
// Enforces explicit Human-in-the-Loop approval before ledger posting.

["Expense Claim", "Purchase Invoice"].forEach((doctypeName) => {
  frappe.ui.form.on(doctypeName, {
    refresh(frm) {
      frm.add_custom_button(
        __("AWO: Evaluate VAT & Approval"),
        () => {
          frappe.call({
            method: "awo_suite.api.expense.evaluate_erpnext_expense",
            args: { doc_or_name: frm.doc },
            freeze: true,
            freeze_message: __("Evaluating via AWO Universal API v1..."),
            callback(r) {
              const res = r && r.message;
              if (!res || !res.ok) return;
              const s = res.summary;
              const d = new frappe.ui.Dialog({
                title: __("AwoExpense — Human-in-the-Loop Financial Gate"),
                fields: [
                  {
                    fieldtype: "HTML",
                    fieldname: "summary_html",
                    options: `
                      <div style="padding:8px 0;line-height:1.6">
                        <div><strong>Claim:</strong> ${frappe.utils.escape_html(s.claimId)} (${frappe.utils.escape_html(s.currency)})</div>
                        <div><strong>Net / VAT / Deductible VAT:</strong> ${s.totalNet} / ${s.totalTax} / ${s.totalDeductibleTax}</div>
                        <div><strong>Total Reimbursable:</strong> <b>${s.totalReimbursable} ${frappe.utils.escape_html(s.currency)}</b></div>
                        <div><strong>Required Role:</strong> <code>${frappe.utils.escape_html(res.requiredApprovalRole)}</code></div>
                        <div><strong>Audit Digest:</strong> <code style="font-size:11px">${frappe.utils.escape_html(res.payloadDigest)}</code></div>
                      </div>
                    `,
                  },
                  {
                    fieldtype: "Select",
                    fieldname: "decision",
                    label: __("Explicit Human Decision"),
                    options: "approved\nrejected",
                    default: "approved",
                    reqd: 1,
                  },
                ],
                primary_action_label: __("Confirm & Record Audit Hash"),
                primary_action(values) {
                  frappe.call({
                    method: "awo_suite.api.expense.approve_erpnext_expense",
                    args: {
                      evaluation_id: res.evaluationId,
                      payload_digest: res.payloadDigest,
                      decision: values.decision,
                      approver_email: frappe.session.user_email || frappe.session.user,
                      approver_name: frappe.session.user_fullname || frappe.session.user,
                      idempotency_key: `erpnext-${s.claimId}-${res.evaluationId}`,
                    },
                    callback(apr) {
                      if (apr && apr.message && apr.message.ok) {
                        d.hide();
                        frappe.msgprint({
                          title: __("AWO Hash-Chained Audit Recorded"),
                          indicator: apr.message.postingAllowed ? "green" : "orange",
                          message: __(
                            "Decision: <b>{0}</b> · Audit Hash: <code>{1}</code>",
                            [apr.message.decision, apr.message.auditRecord.entryHash]
                          ),
                        });
                      }
                    },
                  });
                },
              });
              d.show();
            },
          });
        },
        __("AWO Suite")
      );
    },
  });
});
