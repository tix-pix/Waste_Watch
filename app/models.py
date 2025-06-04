# app/models.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class HardwareSnapshot(Base):
    __tablename__ = "hardware_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    cpu_vendor = Column(String)
    cpu_physical = Column(Integer)
    cpu_logical = Column(Integer)

    gpu_name = Column(String)
    gpu_vram_mb = Column(Integer)

    total_ram_mb = Column(Integer)
    avail_ram_mb = Column(Integer)

    os_version = Column(String)
    is_64bit = Column(Integer)  # 0 или 1
    locale = Column(String, nullable=True)

    # Отношение к crash-записям (внешний ключ устанавливается там)
    crashes = relationship("CrashReport", back_populates="hardware")


class CrashReport(Base):
    __tablename__ = "crash_reports"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    hardware_id = Column(Integer, ForeignKey("hardware_snapshots.id"), nullable=True)
    crash_type = Column(String)
    crash_description = Column(Text, nullable=True)
    dump_file = Column(String, nullable=True)     # путь на диске или URL
    log_text = Column(Text, nullable=True)

    hardware = relationship("HardwareSnapshot", back_populates="crashes")
