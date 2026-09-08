from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from .scoring import sort_findings

TEMPLATE_DIR = Path(__file__).parent / "templates"
REPORT_TEMPLATE = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
).get_template("report.html")


def report_html(scan) -> str:
    return REPORT_TEMPLATE.render(
        target=scan.target_url,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        summary="This executive summary is a placeholder for the AI-enriched report narrative.",
        technologies=scan.technologies,
        findings=sort_findings(scan.findings),
    )


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
