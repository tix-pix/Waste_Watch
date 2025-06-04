# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class HardwareSnapshot(Base):
    __tablename__ = "hardware_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    player_guid = Column(String, index=True)
    timestamp = Column(DateTime, index=True)

    cpu_brand = Column(String)
    cpu_physical = Column(Integer)
    cpu_logical = Column(Integer)

    total_ram_mb = Column(Integer)
    available_ram_mb = Column(Integer)

    gpu_name = Column(String)
    gpu_vram_mb = Column(Integer)

    os_name = Column(String)
    os_version = Column(String)
    is_64bit = Column(Boolean)

    rhi = Column(String)

    # Связь с perf-данными
    performances = relationship("PerformanceTelemetry", back_populates="snapshot", cascade="all, delete-orphan")

class PerformanceTelemetry(Base):
    __tablename__ = "performance_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    player_guid = Column(String, index=True)
    timestamp = Column(DateTime, index=True)

    cpu_load_percent = Column(Float)
    gpu_load_percent = Column(Integer)
    fps = Column(Float)

    # ссылка на hardware_snapshot (если нужно связывать):
    snapshot_id = Column(Integer, ForeignKey("hardware_snapshots.id"), nullable=True)
    snapshot = relationship("HardwareSnapshot", back_populates="performances")

class CrashReport(Base):
    __tablename__ = "crash_reports"

    id = Column(Integer, primary_key=True, index=True)
    player_guid = Column(String, index=True)
    timestamp = Column(DateTime, index=True)

    crash_type = Column(String)
    description = Column(String)
    log_text = Column(String)
    dump_base64 = Column(String)
