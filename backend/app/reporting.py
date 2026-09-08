from io import BytesIO

from fastapi.responses import StreamingResponse
from jinja2 import Template
from weasyprint import HTML

from .scoring import sort_findings

REPORT_TEMPLATE = Template("""<!doctype html><html><body><h1>SentinelScan report</h1><p>Target: {{ target }}</p><h2>Executive summary</h2><p>{{ summary }}</p><h2>Technology profile</h2><ul>{% for tech in technologies %}<li>{{ tech.name }} {{ tech.version or '' }}</li>{% endfor %}</ul><h2>Findings</h2>{% for item in findings %}<article><h3>{{ item.title }} ({{ item.severity }})</h3><p>{{ item.description }}</p><p>OWASP {{ item.owasp_category }}{% if item.kev_known_exploited %} · Known exploited{% endif %}</p><pre>{{ item.remediation or 'Remediation pending' }}</pre></article>{% endfor %}</body></html>""")


def report_html(scan) -> str:
    return REPORT_TEMPLATE.render(target=scan.target_url, summary="Review the prioritized findings and apply the remediation guidance.", technologies=scan.technologies, findings=sort_findings(scan.findings))


def sbom_json(scan) -> bytes:
    document = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "components": [
            {"type": "library", "name": tech.name, "version": tech.version or "unknown"}
            for tech in scan.technologies
        ],
    }
    import json
    return json.dumps(document, indent=2).encode("utf-8")


def pdf_response(scan) -> StreamingResponse:
    pdf = HTML(string=report_html(scan)).write_pdf()
    return StreamingResponse(BytesIO(pdf), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=sentinelscan-report.pdf"})
