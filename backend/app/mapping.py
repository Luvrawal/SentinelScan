OWASP_CATEGORIES = {f"A{index:02d}" for index in range(1, 11)}

OWASP_TAG_MAP = {
    "access-control": "A01",
    "admin-panel": "A01",
    "default-login": "A01",
    "directory-listing": "A01",
    "exposure": "A01",
    "misconfig": "A02",
    "error": "A02",
    "cve": "A03",
    "tech": "A03",
    "supply-chain": "A03",
    "tls": "A04",
    "cookie": "A04",
    "ssl": "A04",
    "injection": "A05",
    "headers": "A06",
    "design": "A06",
    "auth": "A07",
    "login": "A07",
    "integrity": "A08",
    "sri": "A08",
    "logging": "A09",
    "exception": "A10",
}


def owasp_category(tags: list[str]) -> str:
    normalized = {str(tag).strip().casefold() for tag in tags}
    for tag, category in OWASP_TAG_MAP.items():
        if tag in normalized:
            return category
    # A finding must always have a reportable OWASP category. Unknown or
    # informational scanner output is conservatively treated as misconfiguration.
    return "A02"


def severity_bucket(score: float | None, fallback: str = "Low") -> str:
    from .scoring import cvss_severity

    return cvss_severity(score, fallback)
