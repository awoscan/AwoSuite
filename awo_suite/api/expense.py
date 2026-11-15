"""ERPNext `Expense Claim` / `Purchase Invoice` <-> AwoExpense Universal API v1 Adapter.

Security invariants:
1. `evaluate_erpnext_expense` NEVER posts ledger entries (`postingAllowed == False`).
2. `approve_erpnext_expense` requires an explicit human `approver_email`, `payload_digest`, and `idempotency_key`.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from awo_suite.client import AwoUniversalClient, DEFAULT_API_BASE_URL

F = TypeVar("F", bound=Callable[..., Any])

try:
    import frappe  # type: ignore

    whitelist = frappe.whitelist
except ImportError:  # Standalone CI / integration test outside Frappe bench
    frappe = None  # type: ignore

    def whitelist(*_args: Any, **_kwargs: Any) -> Callable[[F], F]:
        def _decorator(fn: F) -> F:
            return fn

        return _decorator


def _build_client_from_settings(client: Optional[AwoUniversalClient] = None) -> AwoUniversalClient:
    if client is not None:
        return client
    if frappe is not None:
        settings = frappe.get_single("AWO Integration Settings")
        tenant_id = getattr(settings, "tenant_id", "") or getattr(frappe.local, "site", "erpnext-site")
        token = settings.get_password("adapter_token", raise_exception=False) or getattr(settings, "adapter_token", "")
        return AwoUniversalClient(
            api_base_url=getattr(settings, "api_base_url", DEFAULT_API_BASE_URL) or DEFAULT_API_BASE_URL,
            tenant_id=tenant_id,
            adapter_token=token or "",
            platform="erpnext",
        )
    return AwoUniversalClient()


def _coerce_doc_dict(doc_or_name: Union[str, Dict[str, Any], Any], doctype: str = "Expense Claim") -> Dict[str, Any]:
    if isinstance(doc_or_name, dict):
        return doc_or_name
    if isinstance(doc_or_name, str):
        stripped = doc_or_name.strip()
        if stripped.startswith("{"):
            return json.loads(stripped)
        if frappe is not None:
            return frappe.get_doc(doctype, stripped).as_dict()
        raise ValueError("Cannot resolve document name without Frappe runtime; pass a document dict.")
    if hasattr(doc_or_name, "as_dict"):
        return doc_or_name.as_dict()
    raise TypeError("Unsupported ERPNext document input.")


def map_erpnext_expense_to_envelope(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Maps an ERPNext `Expense Claim` or `Purchase Invoice` dict into the canonical AWO Expense Envelope."""
    raw_rows: List[Dict[str, Any]] = list(doc.get("expenses") or doc.get("items") or [])
    default_tax_rate = float(doc.get("default_tax_rate", 20.0))

    lines: List[Dict[str, Any]] = []
    for idx, row in enumerate(raw_rows):
        gross = float(row.get("sanctioned_amount") or row.get("amount") or row.get("base_net_amount") or 0.0)
        lines.append(
            {
                "description": str(
                    row.get("description") or row.get("expense_type") or row.get("item_name") or f"Row {idx + 1}"
                ),
                "category": str(row.get("expense_type") or row.get("expense_account") or "general"),
                "receiptRef": str(row.get("name") or f"ROW-{idx + 1}"),
                "grossAmount": gross,
                "taxRate": float(row.get("tax_rate", default_tax_rate)),
                "taxInclusive": bool(row.get("tax_inclusive", True)),
                "nonDeductiblePercent": float(row.get("non_deductible_percent", 0.0)),
            }
        )

    return {
        "claimId": str(doc.get("name") or "HR-EXP-DRAFT"),
        "currency": str(doc.get("currency") or doc.get("company_currency") or "TRY"),
        "employeeEmail": str(doc.get("employee_email") or doc.get("owner") or "employee@company.local"),
        "perDiemDays": float(doc.get("awo_per_diem_days") or 0.0),
        "perDiemDailyRate": float(doc.get("awo_per_diem_daily_rate") or 0.0),
        "mileageKm": float(doc.get("awo_mileage_km") or 0.0),
        "mileageRate": float(doc.get("awo_mileage_rate") or 0.0),
        "managerThreshold": float(doc.get("awo_manager_threshold") or 5000.0),
        "directorThreshold": float(doc.get("awo_director_threshold") or 25000.0),
        "lines": lines,
    }


@whitelist()
def evaluate_erpnext_expense(
    doc_or_name: Union[str, Dict[str, Any], Any],
    client: Optional[AwoUniversalClient] = None,
) -> Dict[str, Any]:
    doc = _coerce_doc_dict(doc_or_name, doctype="Expense Claim")
    envelope = map_erpnext_expense_to_envelope(doc)
    active_client = _build_client_from_settings(client)
    return active_client.evaluate_expense(envelope)


@whitelist()
def approve_erpnext_expense(
    evaluation_id: str,
    payload_digest: str,
    decision: str,
    approver_email: str,
    idempotency_key: str,
    approver_name: str = "",
    client: Optional[AwoUniversalClient] = None,
) -> Dict[str, Any]:
    active_client = _build_client_from_settings(client)
    return active_client.approve_expense(
        evaluation_id=evaluation_id,
        payload_digest=payload_digest,
        decision=decision,
        approver_email=approver_email,
        idempotency_key=idempotency_key,
        approver_name=approver_name,
    )
