"""Controller for AWO Integration Settings Single DocType."""

from __future__ import annotations

from awo_suite.client import AwoUniversalClient, DEFAULT_API_BASE_URL

try:
    from frappe.model.document import Document  # type: ignore
except ImportError:  # Standalone mode outside Frappe bench
    class Document:  # type: ignore
        pass


class AWOIntegrationSettings(Document):
    """Stores AWO Universal API credentials and binds the ERPNext tenant."""

    def bind_session(self, plugin_slug: str = "awoexpense") -> dict:
        license_key = ""
        if hasattr(self, "get_password"):
            license_key = self.get_password("license_key", raise_exception=False) or ""
        else:
            license_key = getattr(self, "license_key", "") or ""

        client = AwoUniversalClient(
            api_base_url=getattr(self, "api_base_url", DEFAULT_API_BASE_URL) or DEFAULT_API_BASE_URL,
            tenant_id=getattr(self, "tenant_id", "") or "erpnext-site",
            platform="erpnext",
        )
        result = client.bind_tenant(plugin_slug=plugin_slug, license_key=license_key)
        if result.get("adapterToken"):
            self.adapter_token = result["adapterToken"]
        return result
