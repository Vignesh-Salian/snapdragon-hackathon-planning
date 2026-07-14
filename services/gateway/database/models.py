"""SQLite persistence for the HemaGrid backend hub.

Two tables per spec: blood_inventory and telemetry_logs. WAL mode is enabled on
every connection so telemetry writes and dashboard reads don't lock each other.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_PATH = os.getenv("HEMAGRID_DB", "hemagrid.db")
ENGINE = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # FastAPI serves sync routes off a threadpool
    future=True,
)


@event.listens_for(ENGINE, "connect")
def _enable_wal(dbapi_conn, _record):
    # PRAGMA per-connection: WAL for concurrency, NORMAL sync is the WAL sweet spot.
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.close()


SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, expire_on_commit=False, future=True)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class BloodInventory(Base):
    __tablename__ = "blood_inventory"
    __table_args__ = (UniqueConstraint("hospital_id", "blood_type", name="uq_hospital_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hospital_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    blood_type: Mapped[str] = mapped_column(String, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    def as_dict(self) -> dict:
        return {
            "hospital_id": self.hospital_id,
            "blood_type": self.blood_type,
            "units": self.units,
            "capacity": self.capacity,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"
    __table_args__ = (
        CheckConstraint("status in ('SAFE','WARNING','COMPROMISED')", name="ck_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    uptime_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    humidity: Mapped[float] = mapped_column(Float, nullable=True)
    shock_g: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="SAFE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)


# Standard 8 ABO/Rh groups + three demo hospitals, seeded so the dashboard has
# something to render the moment the backend starts (no external deps).
BLOOD_TYPES = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
SEED_HOSPITALS = {
    "KMC-MANIPAL": [40, 120, 20, 90, 30, 70, 8, 25],
    "AIIMS-DELHI": [55, 150, 15, 110, 40, 80, 5, 30],
    "APOLLO-BLR": [12, 60, 5, 45, 18, 35, 3, 14],
}


def init_db() -> None:
    """Create tables and seed demo inventory once. Idempotent."""
    Base.metadata.create_all(ENGINE)
    with SessionLocal() as db:
        if db.query(BloodInventory).first() is not None:
            return  # already seeded
        for hospital_id, units in SEED_HOSPITALS.items():
            for blood_type, u in zip(BLOOD_TYPES, units):
                db.add(BloodInventory(hospital_id=hospital_id, blood_type=blood_type, units=u))
        db.commit()
