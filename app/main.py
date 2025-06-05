# app/main.py

import os
import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas, crud, database

# ------------------------- Инициализация приложения ------------------------- #

app = FastAPI(
    title="WasteWatch Dashboard",
    description="Dashboard для аналитики UE5-логов",
    version="1.0.0"
)

# Шаблоны Jinja2 (будем хранить dashboard.html в папке templates)
templates = Jinja2Templates(directory="app/templates")

# (опционально) если у вас будут отдельные css/js файлы, подключите их так:
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS (если понадобится с других доменов)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание таблиц при старте
@app.on_event("startup")
async def on_startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# ------------------------- API: HardwareSnapshot ------------------------- #

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

# ------------------------- API: PerformanceTelemetry ------------------------- #

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

# ------------------------- API: CrashReport ------------------------- #

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

# ------------------------- Dashboard: отдача HTML ------------------------- #

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """
    Просто рендерим dashboard.html, в котором уже подключён JS,
    делающий fetch('/api/...') к нашим эндпоинтам.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ------------------------- Запуск Uvicorn ------------------------- #

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
