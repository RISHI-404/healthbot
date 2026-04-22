"""SQLAlchemy async database engine and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings


# Create async engine
if settings.is_sqlite:
    from sqlalchemy.pool import StaticPool

    # StaticPool forces all async sessions to share a single underlying
    # SQLite connection, which completely eliminates "database is locked"
    # errors caused by concurrent writers.  SQLite's asyncio event-loop
    # serialisation ensures writes never actually race.
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.APP_DEBUG,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.APP_DEBUG,
        pool_size=20,
        max_overflow=10,
    )

# Session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db():
    """Dependency that provides a database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables and configure SQLite for concurrent async access."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        if settings.is_sqlite:
            # WAL + synchronous=NORMAL: safe and fast for concurrent access
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))