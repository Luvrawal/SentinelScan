from __future__ import annotations

from collections.abc import Iterable

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def cvss_severity(score: float | None, fallback: str = "Low") -> str:
    """Classify a CVSS v3 score using the locked thresholds."""
    if score is None:
        normalized = fallback.strip().title()
        return normalized if normalized in SEVERITY_ORDER else "Low"
    if score >= 9.0:
        return "Critical"
    if score >= 7.0:
        return "High"
    if score >= 4.0:
        return "Medium"
    return "Low"


def severity_sort_key(finding) -> tuple[int, float, str]:
    severity = SEVERITY_ORDER.get(finding.severity, SEVERITY_ORDER["Low"])
    score = finding.cvss_score if finding.cvss_score is not None else -1.0
    return severity, -score, finding.title.casefold()


def sort_findings(findings: Iterable) -> list:
    return sorted(findings, key=severity_sort_key)
