# app/main.py
import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas, crud, database

# Создаём папки для файлов (например, дампов)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/srv/ue5-logger/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Инициализируем приложение и базу
app = FastAPI(
    title="UE5 Logger API",
    description="API для приёма данных о железе и крешах из UE5",
    version="1.0.0"
)

# CORS (если фронтенд будет на другом домене)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в продакшене лучше ограничивать домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# При старте создаём таблицы, если нет
@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


# --- Эндпойнты для hardware --- #

@app.post("/api/hardware", response_model=schemas.HardwareSnapshotResponse)
async def post_hardware(hw: schemas.HardwareSnapshotCreate, db: AsyncSession = Depends(database.get_db)):
    """
    Принимает JSON с «срезом» железа, сохраняет в БД и возвращает сохранённый объект.
    """
    return await crud.create_hardware_snapshot(db, hw)


@app.get("/api/hardware", response_model=List[schemas.HardwareSnapshotResponse])
async def get_hardware(db: AsyncSession = Depends(database.get_db)):
    """
    Возвращает список всех аппаратных снимков.
    """
    return await crud.get_hardware_snapshots(db)


# --- Эндпойнты для crash --- #

@app.post("/api/crash", response_model=schemas.CrashReportResponse)
async def post_crash(cr: schemas.CrashReportCreate, db: AsyncSession = Depends(database.get_db)):
    """
    Принимает JSON с данными о вылете, сохраняет в БД и возвращает сохранённый объект.
    """
    return await crud.create_crash_report(db, cr)


@app.get("/api/crashes", response_model=List[schemas.CrashReportResponse])
async def get_crashes(db: AsyncSession = Depends(database.get_db)):
    """
    Возвращает список всех отчётов о крешах.
    """
    return await crud.get_crash_reports(db)


# --- Эндпойнт для загрузки файлов (опционально) --- #
@app.post("/api/upload-dump")
async def upload_dump(file: UploadFile = File(...)):
    """
    Пример, как можно принимать бинарный файл (дамп).
    Сохраняет его в UPLOAD_DIR и возвращает путь.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    return {"filename": file.filename, "path": file_path}


# Если запускаем напрямую
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
