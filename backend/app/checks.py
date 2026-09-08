import socket

import dns.resolver
import httpx


def dns_posture(hostname: str) -> list[dict]:
    findings = []
    try:
        txt = [str(record) for record in dns.resolver.resolve(hostname, "TXT", lifetime=5)]
        if not any(value.startswith('"v=spf1') or value.startswith("v=spf1") for value in txt):
            findings.append({"title": "Missing SPF record", "description": "No SPF policy was found for this domain.", "owasp": "A02"})
    except (dns.exception.DNSException, socket.gaierror):
        findings.append({"title": "DNS posture unavailable", "description": "The domain TXT records could not be evaluated.", "owasp": "A02"})
    return findings


def cookie_posture(url: str) -> list[dict]:
    findings = []
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        for value in response.headers.get_list("set-cookie"):
            lowered = value.lower()
            missing = [flag for flag in ("secure", "httponly", "samesite") if flag not in lowered]
            if missing:
                findings.append({"title": "Cookie security flags missing", "description": f"A cookie is missing: {', '.join(missing)}.", "owasp": "A04"})
    except httpx.HTTPError:
        pass
    return findings
