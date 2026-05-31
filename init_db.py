import asyncio
from backend.core.config import settings
from backend.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

async def init_db():
    print(f"Initializing DB at {settings.DATABASE_URL}")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized.")

if __name__ == "__main__":
    asyncio.run(init_db())
