from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_phase_2a_schema() -> None:
    """Add the Phase 2A columns/tables to existing hackathon databases."""
    from .models import KevCache, NvdCache, ScanCve

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE technologies ADD COLUMN IF NOT EXISTS cpe VARCHAR(512)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_technologies_cpe ON technologies (cpe)"))
        Base.metadata.create_all(bind=connection, tables=[KevCache.__table__, NvdCache.__table__, ScanCve.__table__])
