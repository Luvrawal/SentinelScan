from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import dns.resolver
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Finding, KevCache

KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
KEV_KEY = "cisa-kev"
KEV_TTL = timedelta(hours=6)
DKIM_SELECTORS = ("default", "selector1", "selector2", "google", "k1")


def _txt(name: str) -> list[str]:
    return [str(record).strip('"') for record in dns.resolver.resolve(name, "TXT", lifetime=5)]


def dns_findings(hostname: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        records = _txt(hostname)
        if not any(record.casefold().startswith("v=spf1") for record in records):
            findings.append({"title": "Missing SPF record", "description": "No SPF policy was found for this domain.", "owasp": "A02"})
    except dns.exception.DNSException:
        findings.append({"title": "SPF record unavailable", "description": "The SPF record could not be evaluated.", "owasp": "A02"})

    try:
        dmarc = _txt(f"_dmarc.{hostname}")
        if not any(record.casefold().startswith("v=dmarc1") for record in dmarc):
            findings.append({"title": "Missing DMARC record", "description": "No DMARC policy was found for this domain.", "owasp": "A02"})
    except dns.exception.DNSException:
        findings.append({"title": "Missing DMARC record", "description": "No DMARC policy was found for this domain.", "owasp": "A02"})

    if not any(_has_dkim_selector(hostname, selector) for selector in DKIM_SELECTORS):
        findings.append({"title": "DKIM selector not found", "description": "No common DKIM selector was found; configure the active selector before treating this as definitive.", "owasp": "A02"})
    return findings


def _has_dkim_selector(hostname: str, selector: str) -> bool:
    try:
        return any(record.casefold().startswith("v=dkim1") or "p=" in record.casefold() for record in _txt(f"{selector}._domainkey.{hostname}"))
    except dns.exception.DNSException:
        return False


def cookie_findings(url: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        for cookie in response.headers.get_list("set-cookie"):
            lowered = cookie.casefold()
            missing = [flag for flag in ("secure", "httponly", "samesite") if flag not in lowered]
            if missing:
                findings.append({"title": "Cookie security flags missing", "description": f"A cookie is missing: {', '.join(missing)}.", "owasp": "A04"})
    except httpx.HTTPError:
        return findings
    return findings


def _fresh(cache: KevCache) -> bool:
    expires = cache.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return expires > datetime.now(timezone.utc)


def kev_cves(db: Session) -> set[str]:
    cache = db.get(KevCache, KEV_KEY)
    if cache and _fresh(cache):
        return set(cache.cve_ids)
    try:
        response = httpx.get(KEV_URL, timeout=20)
        response.raise_for_status()
        payload = response.json()
        entries = payload.get("vulnerabilities", [])
        cves = sorted({entry["cveID"] for entry in entries if isinstance(entry, dict) and entry.get("cveID")})
    except (httpx.HTTPError, ValueError, KeyError):
        return set(cache.cve_ids) if cache else set()
    now = datetime.now(timezone.utc)
    if cache:
        cache.response_body = entries
        cache.cve_ids = cves
        cache.fetched_at = now
        cache.expires_at = now + KEV_TTL
        cache.last_error = None
    else:
        db.add(KevCache(feed_key=KEV_KEY, response_body=entries, cve_ids=cves, fetched_at=now, expires_at=now + KEV_TTL))
    return set(cves)


def mark_kev_findings(db: Session, findings: list[Finding], kev_ids: set[str]) -> None:
    for finding in findings:
        if finding.cve_id and finding.cve_id in kev_ids:
            finding.kev_known_exploited = True
