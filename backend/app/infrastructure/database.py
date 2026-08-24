from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Async engine for non-blocking, high-performance database operations
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# Dependency injection for FastAPI endpoints
async def get_db() -> AsyncSession:
    """Yields an asynchronous SQLAlchemy session to endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
