from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# --- DATABASE INFRASTRUCTURE: ASYNC ENGINE ---

# Production-grade async engine for scalability
# Connect pool size optimized for high-concurrency discovery engine
connect_args = {}
if settings.SQLALCHEMY_DATABASE_URI.startswith("postgresql"):
    connect_args = {
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    connect_args=connect_args
)


# Async session factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db() -> None:
    """
    Initialize database tables. 
    In production, this should ideally be handled by Alembic migrations.
    """
    from app.models.sql_models import Base
    try:
        async with engine.begin() as conn:
            # Using a lambda to satisfy some strict type checkers
            await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database init error: {e}")
        raise e

async def get_db():
    """
    Dependency for obtaining an asynchronous database session.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
