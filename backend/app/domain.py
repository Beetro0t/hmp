from typing import Any

from app.config import settings


def domain_enabled() -> bool:
    return bool(settings.domain_api_key) and settings.domain_enabled


def fetch_domain_enrichment(address: str) -> dict[str, Any]:
    if not domain_enabled():
        return {}
    return {
        "note": "Domain enrichment stub - provide API key and implement requests."
    }
