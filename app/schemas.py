# app/schemas.py

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# --- Схемы для HardwareSnapshot --- #

class CPUInfo(BaseModel):
    brand: str
    physicalCores: int
    logicalCores: int

class MemoryInfo(BaseModel):
    totalMB: int
    availableMB: int

class GPUInfo(BaseModel):
    name: str
    vramMB: int

class OSInfo(BaseModel):
    name: str
    version: str
    is64Bit: bool

class HardwareSnapshotCreate(BaseModel):
    playerGUID: str
    timestamp: datetime
    cpu: CPUInfo
    memory: MemoryInfo
    gpu: GPUInfo
    os: OSInfo
    rhi: str

class HardwareSnapshotResponse(BaseModel):
    id: int
    playerGUID: str
    timestamp: datetime
    cpu: CPUInfo
    memory: MemoryInfo
    gpu: GPUInfo
    os: OSInfo
    rhi: str

    class Config:
        model_config = {"from_attributes": True}


# --- Схемы для PerformanceTelemetry --- #

class PerformanceCreate(BaseModel):
    playerGUID: str
    timestamp: datetime
    cpuLoadPercent: float
    gpuLoadPercent: int
    fps: float

class PerformanceResponse(BaseModel):
    id: int
    playerGUID: str
    timestamp: datetime
    cpuLoadPercent: float
    gpuLoadPercent: int
    fps: float
    snapshot_id: Optional[int] = None

    class Config:
        model_config = {"from_attributes": True}


# --- Схемы для CrashReport --- #

class CrashReportCreate(BaseModel):
    playerGUID: str
    timestamp: datetime
    crashType: str
    description: Optional[str] = None
    logText: Optional[str] = None
    dumpBase64: Optional[str] = None

class CrashReportResponse(BaseModel):
    id: int
    playerGUID: str
    timestamp: datetime
    crashType: str
    description: Optional[str] = None
    logText: Optional[str] = None
    dumpBase64: Optional[str] = None

    class Config:
        model_config = {"from_attributes": True}
