from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    scans: Mapped[list["Scan"]] = relationship(back_populates="user")


class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    target_url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    authorization_confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    submitting_ip: Mapped[str] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user: Mapped[User | None] = relationship(back_populates="scans")
    findings: Mapped[list["Finding"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    technologies: Mapped[list["Technology"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    cves: Mapped[list["ScanCve"]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    scan_id: Mapped[UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    cvss_score: Mapped[float | None]
    cve_id: Mapped[str | None] = mapped_column(String(32), index=True)
    owasp_category: Mapped[str] = mapped_column(String(8))
    template_id: Mapped[str | None] = mapped_column(String(255))
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    remediation: Mapped[str | None] = mapped_column(Text)
    kev_known_exploited: Mapped[bool] = mapped_column(default=False)
    scan: Mapped[Scan] = relationship(back_populates="findings")


class Technology(Base):
    __tablename__ = "technologies"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    scan_id: Mapped[UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(100))
    cpe: Mapped[str | None] = mapped_column(String(512), index=True)
    source: Mapped[str] = mapped_column(String(30), default="nuclei")
    scan: Mapped[Scan] = relationship(back_populates="technologies")
    cves: Mapped[list["ScanCve"]] = relationship(back_populates="technology", cascade="all, delete-orphan")


class NvdCache(Base):
    __tablename__ = "nvd_cache"
    cache_key: Mapped[str] = mapped_column(String(768), primary_key=True)
    response_body: Mapped[list] = mapped_column(JSON, default=list)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_error: Mapped[str | None] = mapped_column(Text)


class KevCache(Base):
    __tablename__ = "kev_cache"
    feed_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    response_body: Mapped[list] = mapped_column(JSON, default=list)
    cve_ids: Mapped[list] = mapped_column(JSON, default=list)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_error: Mapped[str | None] = mapped_column(Text)


class ScanCve(Base):
    __tablename__ = "scan_cves"
    __table_args__ = (UniqueConstraint("scan_id", "technology_id", "cve_id", name="uq_scan_technology_cve"),)
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    scan_id: Mapped[UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    technology_id: Mapped[UUID] = mapped_column(ForeignKey("technologies.id", ondelete="CASCADE"), index=True)
    cve_id: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    scan: Mapped[Scan] = relationship(back_populates="cves")
    technology: Mapped[Technology] = relationship(back_populates="cves")
