"""ERPNext `BOM` <-> AwoBom Universal API v1 Adapter.

Reuses the exact same `AwoUniversalClient` & tenant token as `AwoExpense`, proving thin-adapter reusability.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from awo_suite.api.expense import _build_client_from_settings, whitelist
from awo_suite.client import AwoUniversalClient


def _coerce_bom_dict(doc_or_name: Union[str, Dict[str, Any], Any]) -> Dict[str, Any]:
    if isinstance(doc_or_name, dict):
        return doc_or_name
    if isinstance(doc_or_name, str):
        stripped = doc_or_name.strip()
        if stripped.startswith("{"):
            return json.loads(stripped)
        try:
            import frappe  # type: ignore

            return frappe.get_doc("BOM", stripped).as_dict()
        except ImportError as exc:
            raise ValueError("Cannot resolve BOM name without Frappe runtime; pass a BOM dict.") from exc
    if hasattr(doc_or_name, "as_dict"):
        return doc_or_name.as_dict()
    raise TypeError("Unsupported ERPNext BOM document input.")


def map_erpnext_bom_to_envelope(
    doc: Dict[str, Any],
    overhead_percent: float = 10.0,
    target_margin_percent: float = 25.0,
) -> Dict[str, Any]:
    """Maps an ERPNext `BOM` (`items` + `operations`) into the canonical AWO BOM Costing Envelope."""
    raw_items: List[Dict[str, Any]] = list(doc.get("items") or [])
    raw_ops: List[Dict[str, Any]] = list(doc.get("operations") or [])

    components: List[Dict[str, Any]] = [
        {
            "itemCode": str(item.get("item_code") or f"ITEM-{idx + 1}"),
            "itemName": str(item.get("item_name") or item.get("item_code") or f"Component {idx + 1}"),
            "uom": str(item.get("uom") or item.get("stock_uom") or "Nos"),
            "qty": float(item.get("qty") or item.get("stock_qty") or 0.0),
            "unitCost": float(item.get("rate") or item.get("base_rate") or 0.0),
            "scrapPercent": float(item.get("scrap") or 0.0),
        }
        for idx, item in enumerate(raw_items)
    ]

    operations: List[Dict[str, Any]] = [
        {
            "operationName": str(op.get("operation") or f"Op {idx + 1}"),
            "workstation": str(op.get("workstation") or ""),
            "timeMinutes": float(op.get("time_in_mins") or 0.0),
            "hourlyRate": float(op.get("hour_rate") or op.get("base_hour_rate") or 0.0),
        }
        for idx, op in enumerate(raw_ops)
    ]

    return {
        "bomId": str(doc.get("name") or doc.get("item") or "BOM-DRAFT"),
        "itemCode": str(doc.get("item") or doc.get("item_name") or "FG-ITEM"),
        "batchQuantity": float(doc.get("quantity") or 1.0),
        "currency": str(doc.get("currency") or "USD"),
        "overheadPercent": float(overhead_percent),
        "targetMarginPercent": float(target_margin_percent),
        "actorEmail": str(doc.get("modified_by") or doc.get("owner") or "planner@company.local"),
        "components": components,
        "operations": operations,
    }


@whitelist()
def calculate_erpnext_bom(
    doc_or_name: Union[str, Dict[str, Any], Any],
    overhead_percent: float = 10.0,
    target_margin_percent: float = 25.0,
    client: Optional[AwoUniversalClient] = None,
) -> Dict[str, Any]:
    doc = _coerce_bom_dict(doc_or_name)
    envelope = map_erpnext_bom_to_envelope(
        doc,
        overhead_percent=float(overhead_percent),
        target_margin_percent=float(target_margin_percent),
    )
    active_client = _build_client_from_settings(client)
    return active_client.calculate_bom(envelope)
