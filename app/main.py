# app/main.py
import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas, crud, database

# Папка для сохранения дампов (если понадобится)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/srv/ue5-logger/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="UE5 Logger API",
    description="API для приёма данных о железе, perf-телеметрии и крэшей из UE5",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# --- HardwareSnapshot Endpoints --- #

@app.post("/api/hardware", response_model=schemas.HardwareSnapshotResponse)
async def post_hardware(hw: schemas.HardwareSnapshotCreate, db: AsyncSession = Depends(database.get_db)):
    db_obj = await crud.create_hardware_snapshot(db, hw)
    return {
        "id": db_obj.id,
        "playerGUID": db_obj.player_guid,
        "timestamp": db_obj.timestamp,
        "cpu": {
            "brand": db_obj.cpu_brand,
            "physicalCores": db_obj.cpu_physical,
            "logicalCores": db_obj.cpu_logical
        },
        "memory": {
            "totalMB": db_obj.total_ram_mb,
            "availableMB": db_obj.available_ram_mb
        },
        "gpu": {
            "name": db_obj.gpu_name,
            "vramMB": db_obj.gpu_vram_mb
        },
        "os": {
            "name": db_obj.os_name,
            "version": db_obj.os_version,
            "is64Bit": db_obj.is_64bit
        },
        "rhi": db_obj.rhi
    }

@app.get("/api/hardware", response_model=List[schemas.HardwareSnapshotResponse])
async def get_hardware(db: AsyncSession = Depends(database.get_db)):
    items = await crud.get_hardware_snapshots(db)
    result = []
    for o in items:
        result.append({
            "id": o.id,
            "playerGUID": o.player_guid,
            "timestamp": o.timestamp,
            "cpu": {
                "brand": o.cpu_brand,
                "physicalCores": o.cpu_physical,
                "logicalCores": o.cpu_logical
            },
            "memory": {
                "totalMB": o.total_ram_mb,
                "availableMB": o.available_ram_mb
            },
            "gpu": {
                "name": o.gpu_name,
                "vramMB": o.gpu_vram_mb
            },
            "os": {
                "name": o.os_name,
                "version": o.os_version,
                "is64Bit": o.is_64bit
            },
            "rhi": o.rhi
        })
    return result

# --- PerformanceTelemetry Endpoints --- #

@app.post("/api/performance", response_model=schemas.PerformanceResponse)
async def post_performance(perf: schemas.PerformanceCreate, db: AsyncSession = Depends(database.get_db)):
    db_obj = await crud.create_performance(db, perf)
    return {
        "id": db_obj.id,
        "playerGUID": db_obj.player_guid,
        "timestamp": db_obj.timestamp,
        "cpuLoadPercent": db_obj.cpu_load_percent,
        "gpuLoadPercent": db_obj.gpu_load_percent,
        "fps": db_obj.fps,
        "snapshot_id": db_obj.snapshot_id
    }

@app.get("/api/performance", response_model=List[schemas.PerformanceResponse])
async def get_performance(db: AsyncSession = Depends(database.get_db)):
    items = await crud.get_performances(db)
    result = []
    for o in items:
        result.append({
            "id": o.id,
            "playerGUID": o.player_guid,
            "timestamp": o.timestamp,
            "cpuLoadPercent": o.cpu_load_percent,
            "gpuLoadPercent": o.gpu_load_percent,
            "fps": o.fps,
            "snapshot_id": o.snapshot_id
        })
    return result

# --- CrashReport Endpoints --- #

@app.post("/api/crash", response_model=schemas.CrashReportResponse)
async def post_crash(cr: schemas.CrashReportCreate, db: AsyncSession = Depends(database.get_db)):
    db_obj = await crud.create_crash_report(db, cr)
    return {
        "id": db_obj.id,
        "playerGUID": db_obj.player_guid,
        "timestamp": db_obj.timestamp,
        "crashType": db_obj.crash_type,
        "description": db_obj.description,
        "logText": db_obj.log_text,
        "dumpBase64": db_obj.dump_base64
    }

@app.get("/api/crashes", response_model=List[schemas.CrashReportResponse])
async def get_crashes(db: AsyncSession = Depends(database.get_db)):
    items = await crud.get_crash_reports(db)
    result = []
    for o in items:
        result.append({
            "id": o.id,
            "playerGUID": o.player_guid,
            "timestamp": o.timestamp,
            "crashType": o.crash_type,
            "description": o.description,
            "logText": o.log_text,
            "dumpBase64": o.dump_base64
        })
    return result

# --- HTML Routes (Jinja2) --- #

@app.get("/view/hardware", response_class=HTMLResponse)
async def view_hardware(request: Request, db: AsyncSession = Depends(database.get_db)):
    items = await crud.get_hardware_snapshots(db)
    hw_list = []
    for o in items:
        hw_list.append({
            "id": o.id,
            "playerGUID": o.player_guid,
            "timestamp": o.timestamp,
            "cpu": {
                "brand": o.cpu_brand,
                "physicalCores": o.cpu_physical,
                "logicalCores": o.cpu_logical
            },
            "memory": {
                "totalMB": o.total_ram_mb,
                "availableMB": o.available_ram_mb
            },
            "gpu": {
                "name": o.gpu_name,
                "vramMB": o.gpu_vram_mb
            },
            "os": {
                "name": o.os_name,
                "version": o.os_version,
                "is64Bit": o.is_64bit
            },
            "rhi": o.rhi
        })
    return templates.TemplateResponse("hardware_list.html", {"request": request, "items": hw_list})

@app.get("/view/crashes", response_class=HTMLResponse)
async def view_crashes(request: Request, db: AsyncSession = Depends(database.get_db)):
    items = await crud.get_crash_reports(db)
    cr_list = []
    for o in items:
        cr_list.append({
            "id": o.id,
            "playerGUID": o.player_guid,
            "timestamp": o.timestamp,
            "crashType": o.crash_type,
            "description": o.description or "",
            "logText": (o.log_text[:100] + "...") if o.log_text else "-",
            "hasDump": bool(o.dump_base64)
        })
    return templates.TemplateResponse("crash_list.html", {"request": request, "items": cr_list})

# --- (Опционально) upload dump route --- #

@app.post("/api/upload-dump")
async def upload_dump(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    return {"filename": file.filename, "path": file_path}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
