# app/schemas.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# --- аппаратный «снимок» ---
class CPUInfo(BaseModel):
    vendor: str
    physicalCores: int
    logicalCores: int

class MemoryInfo(BaseModel):
    totalMB: int
    availableMB: int

class GPUInfo(BaseModel):
    name: str
    videoMemoryMB: int

class OSInfo(BaseModel):
    version: str
    is64Bit: bool

class HardwareSnapshotCreate(BaseModel):
    playerId: str
    timestamp: datetime
    cpu: CPUInfo
    memory: MemoryInfo
    gpu: GPUInfo
    os: OSInfo
    locale: Optional[str] = None

class HardwareSnapshotResponse(BaseModel):
    id: int
    playerId: str
    timestamp: datetime
    cpu: CPUInfo
    memory: MemoryInfo
    gpu: GPUInfo
    os: OSInfo
    locale: Optional[str]

    class Config:
        orm_mode = True

# --- схема для крешей ---
class CrashReportCreate(BaseModel):
    playerId: str
    timestamp: datetime
    hardwareId: Optional[int] = None
    crashType: str
    crashDescription: Optional[str] = ""
    dumpFile: Optional[str] = None   # можно передавать фейковый путь или URL
    logText: Optional[str] = None

class CrashReportResponse(BaseModel):
    id: int
    playerId: str
    timestamp: datetime
    hardwareId: Optional[int]
    crashType: str
    crashDescription: Optional[str]
    dumpFile: Optional[str]
    logText: Optional[str]

    class Config:
        orm_mode = True
