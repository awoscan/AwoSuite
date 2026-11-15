"""End-to-end verification of AWO Universal API v1 (Node.js) + ERPNext Frappe Adapter (`awo_suite` Python).

Spawns `AwoSign/cloud-portal/server.js` on a free localhost port in an isolated temp data directory
(satisfying Windows Sandbox Rule 8 — server and client run in the same command/process tree) and verifies:
  1. `GET /api/v1/pricing/tiers` & `GET /api/catalog` (`3x3` tiered USD pricing + 4 bundles).
  2. `POST /api/v1/auth/bind-tenant` (`free_core` AND `pro_adapter` via server-issued `AWO-Guard` key).
  3. `AwoExpense` ERPNext adapter (`evaluate_erpnext_expense` -> `postingAllowed == False`, tamper rejection `409`,
     explicit Human-in-the-Loop `approve_erpnext_expense` -> `postingAllowed == True`, and idempotency replay).
  4. `AwoBom` ERPNext adapter (`calculate_erpnext_bom` reusing the exact same `AwoUniversalClient` & tenant token).
  5. `GET /api/v1/audit/logs` (`chainIntegrity.intact == True` across all hash-chained events).
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ADAPTER_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ADAPTER_ROOT.parent
PORTAL_DIR = REPO_ROOT / "AwoSign" / "cloud-portal"

sys.path.insert(0, str(ADAPTER_ROOT))

from awo_suite.api.bom import calculate_erpnext_bom  # noqa: E402
from awo_suite.api.expense import approve_erpnext_expense, evaluate_erpnext_expense  # noqa: E402
from awo_suite.client import AwoApiError, AwoUniversalClient  # noqa: E402


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


_DIRECT_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _wait_for_health(base_url: str, timeout_sec: float = 8.0) -> None:
    deadline = time.time() + timeout_sec
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with _DIRECT_OPENER.open(f"{base_url}/api/health", timeout=1.5) as resp:
                if resp.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(0.15)
    raise RuntimeError(f"Server failed to become healthy at {base_url}: {last_err}")


def _issue_pro_license_key(data_dir: str, env: dict[str, str]) -> str:
    node_code = (
        "const g = require('./awo-guard-engine');"
        "const k = g.issueServerLicenseKey({"
        "  tier: 'AWO-ENTERPRISE-ALL',"
        "  customerEmail: 'erp-admin@acme-mfg.example',"
        "  orderId: 'ord_e2e_pilot_001'"
        "});"
        "process.stdout.write(k.licenseKey);"
    )
    out = subprocess.check_output(
        ["node", "-e", node_code],
        cwd=str(PORTAL_DIR),
        env={**env, "AWO_GUARD_DATA_DIR": data_dir},
        text=True,
    )
    return out.strip()


def run_suite() -> None:
    tmp_dir = tempfile.mkdtemp(prefix="awo-universal-e2e-")
    port = _pick_free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = {
        **os.environ,
        "PORT": str(port),
        "AWO_GUARD_DATA_DIR": tmp_dir,
        "AWO_GUARD_MASTER_SECRET": "e2e-test-master-secret-2026-awosuite-v1",
    }

    pro_key = _issue_pro_license_key(tmp_dir, env)
    assert pro_key.startswith("AWO-ENT-"), f"Unexpected license key format: {pro_key}"

    proc = subprocess.Popen(
        ["node", "server.js"],
        cwd=str(PORTAL_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_for_health(base_url)

        client = AwoUniversalClient(
            api_base_url=base_url,
            tenant_id="acme-erpnext.frappe.cloud",
            platform="erpnext",
        )

        # 1. Verify 3x3 Tiered Pricing & 4 Bundles
        pricing = client.get_pricing_tiers()
        assert pricing["ok"] is True
        tiers = pricing["tiers"]
        assert tiers["tier1_hook"]["addonPriceUsd"] == 19
        assert tiers["tier1_hook"]["businessPriceUsd"] == 29
        assert tiers["tier1_hook"]["adapterPriceUsd"] == 59
        assert tiers["tier2_smb"]["adapterPriceUsd"] == 99
        assert tiers["tier3a_ops"]["adapterPriceUsd"] == 149
        assert tiers["tier3b_vertical"]["adapterPriceUsd"] == 199
        assert [b["priceUsdPerYear"] for b in pricing["bundles"]] == [99, 169, 249, 299]

        with _DIRECT_OPENER.open(f"{base_url}/api/catalog", timeout=5) as cat_resp:
            catalog = json.loads(cat_resp.read().decode("utf-8"))
        assert catalog["pricingModel"] == "tiered_3x3"
        assert len(catalog["tools"]) == 23
        outdoor = next(t for t in catalog["tools"] if t["slug"] == "awooutdoor")
        assert (outdoor["addonPriceUsd"], outdoor["businessPriceUsd"], outdoor["adapterPriceUsd"]) == (49, 99, 199)

        # 2. Verify Free Core Tenant Bind & 5-line limit gate
        free_bind = client.bind_tenant(plugin_slug="awoexpense", company_name="Acme Manufacturing A.S.")
        assert free_bind["ok"] is True
        assert free_bind["mode"] == "free_core"
        assert free_bind["limits"]["maxExpenseLines"] == 5

        oversized_doc = {
            "name": "HR-EXP-2026-OVER",
            "currency": "TRY",
            "expenses": [{"expense_type": "Travel", "amount": 100.0} for _ in range(6)],
        }
        try:
            evaluate_erpnext_expense(oversized_doc, client=client)
            raise AssertionError("Expected 402 PRO_ADAPTER_REQUIRED for >5 lines in free_core mode")
        except AwoApiError as err:
            assert err.status_code == 402
            assert err.payload.get("code") == "PRO_ADAPTER_REQUIRED"

        # 3. Upgrade same tenant to PRO Adapter via server-issued AWO-Guard key
        pro_bind = client.bind_tenant(
            plugin_slug="awoexpense",
            license_key=pro_key,
            company_name="Acme Manufacturing A.S.",
            site_url="https://acme-erpnext.frappe.cloud",
            actor_email="cfo@acme-mfg.example",
        )
        assert pro_bind["ok"] is True
        assert pro_bind["mode"] == "pro_adapter"
        assert pro_bind["limits"]["maxExpenseLines"] == 500

        # 4. Pilot 1: ERPNext Expense Claim -> Evaluate -> Tamper Check -> Human Approve -> Idempotency
        erpnext_claim = {
            "name": "HR-EXP-2026-0042",
            "currency": "TRY",
            "employee_email": "saha.muhendis@acme-mfg.example",
            "awo_per_diem_days": 2,
            "awo_per_diem_daily_rate": 750.0,
            "awo_mileage_km": 120,
            "awo_mileage_rate": 8.5,
            "expenses": [
                {
                    "name": "EXP-ROW-1",
                    "expense_type": "Konaklama",
                    "description": "Fabrika montaj otel konaklama",
                    "sanctioned_amount": 4400.0,
                    "tax_rate": 10.0,
                    "tax_inclusive": True,
                },
                {
                    "name": "EXP-ROW-2",
                    "expense_type": "Temsil & Agirlama",
                    "description": "Musteri yemegi (%30 KKEG)",
                    "sanctioned_amount": 2400.0,
                    "tax_rate": 20.0,
                    "tax_inclusive": True,
                    "non_deductible_percent": 30.0,
                },
            ],
        }
        eval_res = evaluate_erpnext_expense(erpnext_claim, client=client)
        assert eval_res["ok"] is True
        assert eval_res["mode"] == "pro_adapter"
        assert eval_res["humanInTheLoopRequired"] is True
        assert eval_res["postingAllowed"] is False
        assert eval_res["requiredApprovalRole"] == "department_manager"
        assert eval_res["summary"]["totalReimbursable"] == 9320.0

        # Tampered digest MUST fail with 409 PAYLOAD_DIGEST_MISMATCH
        try:
            approve_erpnext_expense(
                evaluation_id=eval_res["evaluationId"],
                payload_digest="0" * 64,
                decision="approved",
                approver_email="cfo@acme-mfg.example",
                idempotency_key="idem-claim-0042",
                client=client,
            )
            raise AssertionError("Expected 409 PAYLOAD_DIGEST_MISMATCH on altered digest")
        except AwoApiError as err:
            assert err.status_code == 409
            assert err.payload.get("code") == "PAYLOAD_DIGEST_MISMATCH"

        # Valid Human-in-the-Loop approval
        apr_res = approve_erpnext_expense(
            evaluation_id=eval_res["evaluationId"],
            payload_digest=eval_res["payloadDigest"],
            decision="approved",
            approver_email="cfo@acme-mfg.example",
            approver_name="Atilla CFO",
            idempotency_key="idem-claim-0042",
            client=client,
        )
        assert apr_res["ok"] is True
        assert apr_res["postingAllowed"] is True
        assert apr_res["ledgerPostingPayload"]["postingAllowed"] is True
        assert apr_res["ledgerPostingPayload"]["creditEntries"][0]["amount"] == 9320.0

        # Idempotent replay MUST return exact same result with `idempotentReplay: True`
        replay_res = approve_erpnext_expense(
            evaluation_id=eval_res["evaluationId"],
            payload_digest=eval_res["payloadDigest"],
            decision="approved",
            approver_email="cfo@acme-mfg.example",
            idempotency_key="idem-claim-0042",
            client=client,
        )
        assert replay_res["idempotentReplay"] is True
        assert replay_res["auditRecord"]["entryHash"] == apr_res["auditRecord"]["entryHash"]

        # 5. Pilot 2: ERPNext BOM -> Calculate Cost & Margin reusing the EXACT SAME `client` & token!
        erpnext_bom = {
            "name": "BOM-CNC-VALVE-001",
            "item": "FG-CNC-VALVE-DN50",
            "quantity": 10,
            "currency": "USD",
            "modified_by": "uretim.sef@acme-mfg.example",
            "items": [
                {
                    "item_code": "RM-SS316-BAR",
                    "item_name": "AISI 316 Paslanmaz Celik Mil",
                    "uom": "Kg",
                    "qty": 25,
                    "rate": 8.0,
                    "scrap": 10.0,  # 27.5 Kg * $8 = $220
                },
                {
                    "item_code": "RM-PTFE-SEAL",
                    "item_name": "PTFE Sizdirmazlik Contasi",
                    "uom": "Nos",
                    "qty": 20,
                    "rate": 2.5,
                    "scrap": 0.0,  # $50
                },
            ],
            "operations": [
                {
                    "operation": "CNC Torna Isleme",
                    "workstation": "MAZAK-CNC-01",
                    "time_in_mins": 90,
                    "hour_rate": 40.0,  # $60
                },
                {
                    "operation": "Basinc Sizdirmazlik Testi",
                    "workstation": "QC-HYDRO-01",
                    "time_in_mins": 30,
                    "hour_rate": 30.0,  # $15
                },
            ],
        }
        bom_res = calculate_erpnext_bom(
            erpnext_bom,
            overhead_percent=12.0,
            target_margin_percent=30.0,
            client=client,
        )
        assert bom_res["ok"] is True
        assert bom_res["mode"] == "pro_adapter"
        s_bom = bom_res["summary"]
        assert s_bom["totalMaterialCost"] == 270.0
        assert s_bom["totalOperationCost"] == 75.0
        assert s_bom["primeCost"] == 345.0
        assert s_bom["overheadCost"] == 41.4
        assert s_bom["totalBatchCost"] == 386.4
        assert s_bom["unitCost"] == 38.64
        assert s_bom["recommendedUnitPrice"] == 55.2  # 38.64 / (1 - 0.30) = 55.20
        assert s_bom["topCostDriverItemCode"] == "RM-SS316-BAR"

        # 6. Verify SHA-256 Hash-Chained Audit Trail Integrity across ALL events
        audit = client.get_audit_logs()
        assert audit["ok"] is True
        assert audit["chainIntegrity"]["intact"] is True
        event_types = [r["eventType"] for r in audit["records"]]
        assert event_types == [
            "tenant.bound",
            "tenant.bound",
            "expense.evaluated",
            "expense.approved",
            "bom.calculated",
        ]

        print("ALL_E2E_UNIVERSAL_API_AND_ERPNEXT_ADAPTER_CHECKS_PASSED")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    run_suite()
