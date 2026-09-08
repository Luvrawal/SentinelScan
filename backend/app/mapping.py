OWASP_TAG_MAP = {
    "exposure": "A01",
    "default-login": "A01",
    "misconfig": "A02",
    "cve": "A03",
    "tech": "A03",
    "tls": "A04",
    "cookie": "A04",
    "headers": "A06",
}


def owasp_category(tags: list[str]) -> str:
    for tag, category in OWASP_TAG_MAP.items():
        if tag in tags:
            return category
    return "A02"


def severity_bucket(score: float | None, fallback: str = "Low") -> str:
    if score is None:
        return fallback.title()
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"
