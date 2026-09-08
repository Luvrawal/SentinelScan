from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .models import NvdCache, ScanCve, Technology

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
CACHE_TTL = timedelta(hours=24)

# Only emit CPEs when the product identity is sufficiently unambiguous.
CPE_PRODUCTS = {
    "apache http server": ("a", "apache", "http_server"),
    "apache httpd": ("a", "apache", "http_server"),
    "nginx": ("a", "f5", "nginx"),
    "php": ("a", "php", "php"),
    "jquery": ("a", "jquery", "jquery"),
    "wordpress": ("a", "wordpress", "wordpress"),
    "react": ("a", "facebook", "react"),
    "next.js": ("a", "vercel", "next_js"),
}


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(":", "\\:")


def technology_cpe(technology: Technology) -> str | None:
    product = CPE_PRODUCTS.get(technology.name.casefold())
    if not product or not technology.version:
        return None
    part, vendor, name = product
    version = technology.version.strip().replace(" ", "_")
    return f"cpe:2.3:{part}:{_escape(vendor)}:{_escape(name)}:{_escape(version)}:*:*:*:*:*:*:*"


def _fresh(cache: NvdCache) -> bool:
    expires_at = cache.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at > datetime.now(timezone.utc)


def _request_cves(cpe: str, settings: Settings) -> list[dict[str, Any]]:
    headers = {"apiKey": settings.nvd_api_key} if settings.nvd_api_key else {}
    params = {"cpeName": cpe}
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(NVD_URL, params=params, headers=headers)
            if response.status_code == 429 or response.status_code >= 500:
                response.raise_for_status()
            response.raise_for_status()
            payload = response.json()
            vulnerabilities = payload.get("vulnerabilities", [])
            return vulnerabilities if isinstance(vulnerabilities, list) else []
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2**attempt)
    raise RuntimeError("NVD lookup failed") from last_error


def fetch_cves(db: Session, technology: Technology, settings: Settings) -> list[dict[str, Any]]:
    cpe = technology.cpe or technology_cpe(technology)
    if not cpe:
        return []
    technology.cpe = cpe
    cache = db.get(NvdCache, cpe)
    if cache and _fresh(cache):
        return cache.response_body if isinstance(cache.response_body, list) else []
    try:
        vulnerabilities = _request_cves(cpe, settings)
    except RuntimeError:
        return []
    now = datetime.now(timezone.utc)
    if cache:
        cache.response_body = vulnerabilities
        cache.fetched_at = now
        cache.expires_at = now + CACHE_TTL
        cache.last_error = None
    else:
        db.add(NvdCache(cache_key=cpe, response_body=vulnerabilities, fetched_at=now, expires_at=now + CACHE_TTL))
    return vulnerabilities


def persist_cves(db: Session, scan_id: str, technology: Technology, vulnerabilities: list[dict[str, Any]]) -> int:
    inserted = 0
    existing = {
        row.cve_id
        for row in db.scalars(select(ScanCve).where(ScanCve.scan_id == scan_id, ScanCve.technology_id == technology.id))
    }
    for vulnerability in vulnerabilities:
        cve = vulnerability.get("cve") if isinstance(vulnerability, dict) else None
        if not isinstance(cve, dict):
            continue
        cve_id = cve.get("id")
        if not isinstance(cve_id, str) or not cve_id or cve_id in existing:
            continue
        descriptions = cve.get("descriptions") or []
        description = next((item.get("value") for item in descriptions if item.get("lang") == "en"), None)
        db.add(ScanCve(scan_id=scan_id, technology_id=technology.id, cve_id=cve_id, description=description, published_at=_parse_date(cve.get("published")), raw_data=cve))
        existing.add(cve_id)
        inserted += 1
    return inserted


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
