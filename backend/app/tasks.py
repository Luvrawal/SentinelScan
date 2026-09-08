import json
import subprocess
import tempfile
from pathlib import Path

from .celery_app import celery_app
from .config import get_settings
from .db import SessionLocal
from .models import Finding, Scan, Technology
from .mapping import owasp_category
from .scoring import cvss_severity
from .security import validate_target_url, UnsafeTarget
from .technology import extract_technology
from .nvd import fetch_cves, persist_cves, technology_cpe


def update_scan(scan_id, status: str, progress: int, error: str | None = None) -> None:
    with SessionLocal() as db:
        scan = db.get(Scan, scan_id)
        if scan:
            scan.status, scan.progress, scan.error_message = status, progress, error
            db.commit()


@celery_app.task(name="sentinelscan.run_scan")
def run_scan(scan_id: str) -> None:
    settings = get_settings()
    try:
        update_scan(scan_id, "scanning", 10)
        with SessionLocal() as db:
            scan = db.get(Scan, scan_id)
            if not scan:
                return
            try:
                validate_target_url(scan.target_url)
            except UnsafeTarget as exc:
                scan.status, scan.progress, scan.error_message = "failed", 100, str(exc)
                db.commit()
                return
            with tempfile.TemporaryDirectory() as workdir:
                output = Path(workdir) / "nuclei.jsonl"
                command = [settings.nuclei_binary, "-u", scan.target_url, "-tags", "cve,exposure,misconfig,tech", "-json-export", str(output), "-silent"]
                try:
                    subprocess.run(command, check=True, timeout=settings.nuclei_timeout_seconds, capture_output=True, text=True, shell=False)
                except (OSError, subprocess.SubprocessError) as exc:
                    scan.status, scan.progress, scan.error_message = "failed", 100, f"Nuclei failed: {type(exc).__name__}"
                    db.commit()
                    return
                update_scan(scan_id, "analyzing", 70)
                seen_technologies: set[tuple[str, str | None, str]] = set()
                for line in output.read_text(encoding="utf-8").splitlines() if output.exists() else []:
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    info = item.get("info", {})
                    tags = info.get("tags", []) or []
                    cvss = info.get("classification", {}).get("cvss-score")
                    try:
                        cvss = float(cvss) if cvss is not None else None
                    except (TypeError, ValueError):
                        cvss = None
                    db.add(Finding(scan_id=scan.id, title=info.get("name", item.get("template-id", "Nuclei finding")), description=info.get("description") or "Detected by Nuclei.", severity=cvss_severity(cvss, str(info.get("severity", "Low"))), cvss_score=cvss, cve_id=(info.get("classification") or {}).get("cve-id"), owasp_category=owasp_category(tags), template_id=item.get("template-id"), evidence=item))
                    technology = extract_technology(item)
                    if technology:
                        technology_key = (technology["name"], technology["version"], technology["category"])
                        if technology_key not in seen_technologies:
                            technology_row = Technology(scan_id=scan.id, cpe=technology_cpe(Technology(**technology)), **technology)
                            db.add(technology_row)
                            db.flush()
                            try:
                                vulnerabilities = fetch_cves(db, technology_row, settings)
                                persist_cves(db, scan.id, technology_row, vulnerabilities)
                            except Exception:
                                # NVD enrichment is best-effort; the core scan remains usable.
                                pass
                            seen_technologies.add(technology_key)
                scan.status, scan.progress = "done", 100
                db.commit()
    except Exception:
        update_scan(scan_id, "failed", 100, "Unexpected scan worker failure")
