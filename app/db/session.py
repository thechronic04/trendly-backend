from datetime import datetime, timezone
import os
import socket
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# --- DATABASE INFRASTRUCTURE: ASYNC ENGINE ---


def _ensure_ipv4_db_url(url: str) -> str:
    if not url.startswith("postgresql"):
        return url
    try:
        at_idx = url.rfind("@")
        slash_idx = url.find("/", at_idx)
        host_port = url[at_idx + 1 : slash_idx]
        if ":" in host_port:
            host, port_str = host_port.rsplit(":", 1)
            port = int(port_str)
        else:
            host = host_port
            port = 5432

        results = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if results:
            ipv4 = results[0][4][0]
            new_url = url.replace(f"@{host_port}", f"@{ipv4}:{port}")
            print(f"Forced IPv4 resolution: {host} -> {ipv4}")
            return new_url
    except Exception as e:
        print(f"IPv4 resolution failed for {url.split('@')[-1]}: {e}")
    return url


_db_url = str(settings.SQLALCHEMY_DATABASE_URI)

if os.getenv("VERCEL"):
    print("Vercel environment detected. Checking IPv4 resolution...")
    _db_url = _ensure_ipv4_db_url(_db_url)

# Log the host being used (without password)
try:
    _readable_host = _db_url.split("@")[-1]
    print(f"Connecting to DB host: {_readable_host}")
except:
    pass

connect_args = {}
if _db_url.startswith("postgresql"):
    connect_args = {
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    }

engine = create_async_engine(
    _db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
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
