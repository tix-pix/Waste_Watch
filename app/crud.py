# app/crud.py
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.exc import NoResultFound

from .models import HardwareSnapshot, CrashReport
from .schemas import HardwareSnapshotCreate, CrashReportCreate

# Сохранить аппаратный снимок в БД
async def create_hardware_snapshot(db, hw: HardwareSnapshotCreate):
    obj = HardwareSnapshot(
        player_id=hw.playerId,
        timestamp=hw.timestamp,
        cpu_vendor=hw.cpu.vendor,
        cpu_physical=hw.cpu.physicalCores,
        cpu_logical=hw.cpu.logicalCores,
        gpu_name=hw.gpu.name,
        gpu_vram_mb=hw.gpu.videoMemoryMB,
        total_ram_mb=hw.memory.totalMB,
        avail_ram_mb=hw.memory.availableMB,
        os_version=hw.os.version,
        is_64bit=1 if hw.os.is64Bit else 0,
        locale=hw.locale
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# Получить список всех snapshot-ов (с возможностью фильтрации)
async def get_hardware_snapshots(db):
    result = await db.execute(select(HardwareSnapshot).order_by(HardwareSnapshot.timestamp.desc()))
    return result.scalars().all()

# Сохранить отчёт о креше
async def create_crash_report(db, cr: CrashReportCreate):
    obj = CrashReport(
        player_id=cr.playerId,
        timestamp=cr.timestamp,
        hardware_id=cr.hardwareId,
        crash_type=cr.crashType,
        crash_description=cr.crashDescription,
        dump_file=cr.dumpFile,
        log_text=cr.logText
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# Получить все креши
async def get_crash_reports(db):
    result = await db.execute(select(CrashReport).order_by(CrashReport.timestamp.desc()))
    return result.scalars().all()
