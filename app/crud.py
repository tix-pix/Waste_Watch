# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

# --- HardwareSnapshot --- #

async def create_hardware_snapshot(db: AsyncSession, hw: schemas.HardwareSnapshotCreate):
    db_obj = models.HardwareSnapshot(
        player_guid=hw.playerGUID,
        timestamp=hw.timestamp,
        cpu_brand=hw.cpu.brand,
        cpu_physical=hw.cpu.physicalCores,
        cpu_logical=hw.cpu.logicalCores,
        total_ram_mb=hw.memory.totalMB,
        available_ram_mb=hw.memory.availableMB,
        gpu_name=hw.gpu.name,
        gpu_vram_mb=hw.gpu.vramMB,
        os_name=hw.os.name,
        os_version=hw.os.version,
        is_64bit=hw.os.is64Bit,
        rhi=hw.rhi
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_hardware_snapshots(db: AsyncSession):
    result = await db.execute(select(models.HardwareSnapshot))
    return result.scalars().all()

# --- PerformanceTelemetry --- #

async def create_performance(db: AsyncSession, perf: schemas.PerformanceCreate):
    db_obj = models.PerformanceTelemetry(
        player_guid=perf.playerGUID,
        timestamp=perf.timestamp,
        cpu_load_percent=perf.cpuLoadPercent,
        gpu_load_percent=perf.gpuLoadPercent,
        fps=perf.fps
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_performances(db: AsyncSession):
    result = await db.execute(select(models.PerformanceTelemetry))
    return result.scalars().all()

# --- CrashReport --- #

async def create_crash_report(db: AsyncSession, cr: schemas.CrashReportCreate):
    db_obj = models.CrashReport(
        player_guid=cr.playerGUID,
        timestamp=cr.timestamp,
        crash_type=cr.crashType,
        description=cr.description,
        log_text=cr.logText,
        dump_base64=cr.dumpBase64
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_crash_reports(db: AsyncSession):
    result = await db.execute(select(models.CrashReport))
    return result.scalars().all()
