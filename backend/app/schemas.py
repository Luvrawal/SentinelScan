from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ScanCreate(BaseModel):
    target_url: AnyHttpUrl
    authorization_confirmed: bool = Field(..., description="The submitter confirms authorization to scan this target.")


class ScanAccepted(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    scan_id: UUID
    status: str
    status_url: str


class ScanStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    scan_id: UUID
    target_url: str
    status: str
    progress: int
    error: str | None = None
    created_at: datetime


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    severity: str
    cvss_score: float | None
    cve_id: str | None
    owasp_category: str
    evidence: dict
    remediation: str | None
    kev_known_exploited: bool


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    version: str | None
    category: str | None
    source: str


class ScanReport(BaseModel):
    scan_id: UUID
    target_url: str
    status: str
    executive_summary: str
    technologies: list[TechnologyResponse]
    findings: list[FindingResponse]
    pdf_url: str
    sbom_url: str
