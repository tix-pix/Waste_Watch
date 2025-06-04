# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Путь к файлу SQLite (он появится рядом с этим скриптом)
DATABASE_URL = "sqlite+aiosqlite:///./ue5_logger.db"

# Асинхронный движок
engine = create_async_engine(
    DATABASE_URL, echo=False, future=True
)

# Сессии для CRUD
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Функция-утилита, чтобы получать сессию в эндпоинтах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
