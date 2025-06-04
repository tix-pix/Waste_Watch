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
    description="API для приёма данных о железе и краш-репортах из UE5",
    version="1.0.0"
)

# Настраиваем шаблоны Jinja2
templates = Jinja2Templates(directory="app/templates")

# CORS (разрешаем всё, для внутреннего использования)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# При старте создаём таблицы
@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


# --- Эндпойнты для Hardware --- #

@app.post("/api/hardware", response_model=schemas.HardwareSnapshotResponse)
async def post_hardware(hw: schemas.HardwareSnapshotCreate, db: AsyncSession = Depends(database.get_db)):
    """
    Принимает JSON с «снимком» железа, сохраняет в БД и возвращает объект в формате Pydantic.
    """
    db_obj = await crud.create_hardware_snapshot(db, hw)
    # Конвертируем SQLAlchemy-объект в dict, соответствующий HardwareSnapshotResponse
    return {
        "id": db_obj.id,
        "playerId": db_obj.player_id,
        "timestamp": db_obj.timestamp,
        "cpu": {
            "vendor": db_obj.cpu_vendor,
            "physicalCores": db_obj.cpu_physical,
            "logicalCores": db_obj.cpu_logical
        },
        "memory": {
            "totalMB": db_obj.total_ram_mb,
            "availableMB": db_obj.avail_ram_mb
        },
        "gpu": {
            "name": db_obj.gpu_name,
            "videoMemoryMB": db_obj.gpu_vram_mb
        },
        "os": {
            "version": db_obj.os_version,
            "is64Bit": bool(db_obj.is_64bit)
        },
        "locale": db_obj.locale
    }


@app.get("/api/hardware", response_model=List[schemas.HardwareSnapshotResponse])
async def get_hardware(db: AsyncSession = Depends(database.get_db)):
    """
    Возвращает список всех аппаратных снимков в формате Pydantic.
    """
    items = await crud.get_hardware_snapshots(db)
    result = []
    for db_obj in items:
        result.append({
            "id": db_obj.id,
            "playerId": db_obj.player_id,
            "timestamp": db_obj.timestamp,
            "cpu": {
                "vendor": db_obj.cpu_vendor,
                "physicalCores": db_obj.cpu_physical,
                "logicalCores": db_obj.cpu_logical
            },
            "memory": {
                "totalMB": db_obj.total_ram_mb,
                "availableMB": db_obj.avail_ram_mb
            },
            "gpu": {
                "name": db_obj.gpu_name,
                "videoMemoryMB": db_obj.gpu_vram_mb
            },
            "os": {
                "version": db_obj.os_version,
                "is64Bit": bool(db_obj.is_64bit)
            },
            "locale": db_obj.locale
        })
    return result


# --- Эндпойнты для Crash --- #

@app.post("/api/crash", response_model=schemas.CrashReportResponse)
async def post_crash(cr: schemas.CrashReportCreate, db: AsyncSession = Depends(database.get_db)):
    """
    Принимает JSON с данными о вылете, сохраняет в БД и возвращает объект в формате Pydantic.
    """
    db_obj = await crud.create_crash_report(db, cr)
    return {
        "id": db_obj.id,
        "playerId": db_obj.player_id,
        "timestamp": db_obj.timestamp,
        "hardwareId": db_obj.hardware_id,
        "crashType": db_obj.crash_type,
        "crashDescription": db_obj.crash_description,
        "dumpFile": db_obj.dump_file,
        "logText": db_obj.log_text
    }


@app.get("/api/crashes", response_model=List[schemas.CrashReportResponse])
async def get_crashes(db: AsyncSession = Depends(database.get_db)):
    """
    Возвращает список всех отчётов о крашах.
    """
    items = await crud.get_crash_reports(db)
    result = []
    for db_obj in items:
        result.append({
            "id": db_obj.id,
            "playerId": db_obj.player_id,
            "timestamp": db_obj.timestamp,
            "hardwareId": db_obj.hardware_id,
            "crashType": db_obj.crash_type,
            "crashDescription": db_obj.crash_description,
            "dumpFile": db_obj.dump_file,
            "logText": db_obj.log_text
        })
    return result


# --- HTML-маршруты (Jinja2) --- #

@app.get("/view/hardware", response_class=HTMLResponse)
async def view_hardware(request: Request, db: AsyncSession = Depends(database.get_db)):
    items = await crud.get_hardware_snapshots(db)
    hw_list = []
    for h in items:
        hw_list.append({
            "id": h.id,
            "playerId": h.player_id,
            "timestamp": h.timestamp,
            "cpu": {
                "vendor": h.cpu_vendor,
                "physicalCores": h.cpu_physical,
                "logicalCores": h.cpu_logical
            },
            "memory": {
                "totalMB": h.total_ram_mb,
                "availableMB": h.avail_ram_mb
            },
            "gpu": {
                "name": h.gpu_name,
                "videoMemoryMB": h.gpu_vram_mb
            },
            "os": {
                "version": h.os_version,
                "is64Bit": bool(h.is_64bit)
            },
            "locale": h.locale
        })
    return templates.TemplateResponse("hardware_list.html", {"request": request, "items": hw_list})


@app.get("/view/crashes", response_class=HTMLResponse)
async def view_crashes(request: Request, db: AsyncSession = Depends(database.get_db)):
    items = await crud.get_crash_reports(db)
    cr_list = []
    for c in items:
        cr_list.append({
            "id": c.id,
            "playerId": c.player_id,
            "timestamp": c.timestamp,
            "crashType": c.crash_type,
            "crashDescription": c.crash_description,
            "dumpFile": c.dump_file or "",
            "logText": c.log_text or ""
        })
    return templates.TemplateResponse("crash_list.html", {"request": request, "items": cr_list})


# --- (Опционально) загрузка дампа файла --- #
@app.post("/api/upload-dump")
async def upload_dump(file: UploadFile = File(...)):
    """
    Пример приёма бинарного файла (дампа). Сохраняем в UPLOAD_DIR и возвращаем путь.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    return {"filename": file.filename, "path": file_path}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
