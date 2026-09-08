from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Scan
from .auth import TokenRequest, issue_token
from .reporting import pdf_response, report_html, sbom_json
from .schemas import ScanAccepted, ScanCreate, ScanReport, ScanStatus
from .security import reject_unsafe_target
from .tasks import run_scan

app = FastAPI(title="SentinelScan API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/token")
def create_token(payload: TokenRequest) -> dict[str, str]:
    return {"access_token": issue_token(payload.email), "token_type": "bearer"}


@app.post("/api/scan", response_model=ScanAccepted, status_code=status.HTTP_202_ACCEPTED)
@app.post("/scan", response_model=ScanAccepted, status_code=status.HTTP_202_ACCEPTED, include_in_schema=False)
def create_scan(payload: ScanCreate, request: Request, db: Session = Depends(get_db)) -> ScanAccepted:
    if not payload.authorization_confirmed:
        raise HTTPException(status_code=400, detail="Authorization confirmation is required")
    target_url = reject_unsafe_target(str(payload.target_url))
    client_ip = request.client.host if request.client else "unknown"
    scan = Scan(target_url=target_url, status="queued", progress=0, authorization_confirmed_at=datetime.now(timezone.utc), submitting_ip=client_ip)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    try:
        run_scan.delay(str(scan.id))
    except Exception as exc:
        scan.status, scan.progress, scan.error_message = "failed", 100, "Scan queue is unavailable"
        db.commit()
        raise HTTPException(status_code=503, detail="Scan queue is unavailable") from exc
    return ScanAccepted(scan_id=scan.id, status=scan.status, status_url=f"/api/scan/{scan.id}/status")


@app.get("/api/scan/{scan_id}/status", response_model=ScanStatus)
@app.get("/scan/{scan_id}/status", response_model=ScanStatus, include_in_schema=False)
def scan_status(scan_id: UUID, db: Session = Depends(get_db)) -> ScanStatus:
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanStatus(scan_id=scan.id, target_url=scan.target_url, status=scan.status, progress=scan.progress, error=scan.error_message, created_at=scan.created_at)


@app.get("/api/scan/{scan_id}/report", response_model=ScanReport)
def scan_report(scan_id: UUID, db: Session = Depends(get_db)) -> ScanReport:
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.status != "done":
        raise HTTPException(status_code=409, detail="Report is not ready")
    return ScanReport(scan_id=scan.id, target_url=scan.target_url, status=scan.status, executive_summary="Scan completed. Review the prioritized findings below.", technologies=scan.technologies, findings=scan.findings, pdf_url=f"/api/scan/{scan.id}/report.pdf", sbom_url=f"/api/scan/{scan.id}/sbom")


@app.get("/api/scan/{scan_id}/report.pdf")
def download_report(scan_id: UUID, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.status != "done":
        raise HTTPException(status_code=409, detail="Report is not ready")
    return pdf_response(scan)


@app.get("/api/scan/{scan_id}/sbom")
def download_sbom(scan_id: UUID, db: Session = Depends(get_db)) -> Response:
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.status != "done":
        raise HTTPException(status_code=409, detail="SBOM is not ready")
    return Response(content=sbom_json(scan), media_type="application/vnd.cyclonedx+json", headers={"Content-Disposition": "attachment; filename=sentinelscan-sbom.json"})


@app.exception_handler(Exception)
async def unhandled_error(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
