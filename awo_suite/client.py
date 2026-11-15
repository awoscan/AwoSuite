"""Zero-dependency Python thin client for AWO Universal API v1.0.

Shared by both AwoExpense and AwoBom inside ERPNext / Frappe Cloud.
Uses Python stdlib `urllib.request` + `json` so Frappe Cloud builds require zero extra pip wheels.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_API_BASE_URL = "https://awosign.awoscan.com"


class AwoApiError(RuntimeError):
    """Structured exception carrying HTTP status code and AWO Universal API error payload."""

    def __init__(self, status_code: int, message: str, payload: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(f"[AWO API {status_code}] {message}")
        self.status_code = status_code
        self.payload = payload or {}


class AwoUniversalClient:
    """Reusable multi-product adapter client for ERPNext / Frappe."""

    def __init__(
        self,
        api_base_url: str = DEFAULT_API_BASE_URL,
        tenant_id: str = "default-erpnext-site",
        adapter_token: str = "",
        platform: str = "erpnext",
        timeout_seconds: int = 15,
    ) -> None:
        self.api_base_url = (api_base_url or DEFAULT_API_BASE_URL).rstrip("/")
        self.tenant_id = tenant_id.strip() or "default-erpnext-site"
        self.adapter_token = adapter_token.strip()
        self.platform = platform.strip().lower() or "erpnext"
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.api_base_url}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "awo-suite-erpnext-adapter/2.2.0",
        }
        if self.adapter_token:
            headers["Authorization"] = f"Bearer {self.adapter_token}"

        raw_data = None
        if body is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
            raw_data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url=url, data=raw_data, headers=headers, method=method.upper())
        parsed_host = urllib.parse.urlparse(url).hostname or ""
        opener = (
            urllib.request.build_opener(urllib.request.ProxyHandler({}))
            if parsed_host in ("127.0.0.1", "localhost", "::1")
            else urllib.request.build_opener()
        )
        try:
            with opener.open(req, timeout=self.timeout_seconds) as resp:
                raw_resp = resp.read().decode("utf-8")
                return json.loads(raw_resp) if raw_resp else {}
        except urllib.error.HTTPError as exc:
            err_text = exc.read().decode("utf-8", errors="replace")
            try:
                err_json = json.loads(err_text)
            except ValueError:
                err_json = {"ok": False, "error": err_text}
            raise AwoApiError(
                exc.code,
                str(err_json.get("error") or f"HTTP {exc.code}"),
                err_json,
            ) from exc

    def get_pricing_tiers(self) -> Dict[str, Any]:
        return self._request("GET", "/api/v1/pricing/tiers")

    def bind_tenant(
        self,
        plugin_slug: str = "awoexpense",
        license_key: str = "",
        company_name: str = "",
        site_url: str = "",
        actor_email: str = "Administrator",
    ) -> Dict[str, Any]:
        result = self._request(
            "POST",
            "/api/v1/auth/bind-tenant",
            {
                "platform": self.platform,
                "tenantId": self.tenant_id,
                "pluginSlug": plugin_slug,
                "licenseKey": license_key,
                "companyName": company_name,
                "siteUrl": site_url,
                "actorEmail": actor_email,
            },
        )
        if result.get("adapterToken"):
            self.adapter_token = str(result["adapterToken"])
        return result

    def evaluate_expense(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "platform": self.platform,
            "tenantId": self.tenant_id,
            **envelope,
        }
        return self._request("POST", "/api/v1/adapters/expense/evaluate", payload)

    def approve_expense(
        self,
        evaluation_id: str,
        payload_digest: str,
        decision: str,
        approver_email: str,
        idempotency_key: str,
        approver_name: str = "",
    ) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/adapters/expense/approve",
            {
                "platform": self.platform,
                "tenantId": self.tenant_id,
                "evaluationId": evaluation_id,
                "payloadDigest": payload_digest,
                "decision": decision,
                "approverEmail": approver_email,
                "approverName": approver_name,
                "idempotencyKey": idempotency_key,
            },
        )

    def calculate_bom(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "platform": self.platform,
            "tenantId": self.tenant_id,
            **envelope,
        }
        return self._request("POST", "/api/v1/adapters/bom/calculate", payload)

    def get_audit_logs(self) -> Dict[str, Any]:
        return self._request(
            "GET",
            "/api/v1/audit/logs",
            query={"platform": self.platform, "tenantId": self.tenant_id},
        )
