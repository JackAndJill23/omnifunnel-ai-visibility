from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import redis.asyncio as redis
from .config import get_settings


_settings = get_settings()
_engine = create_async_engine(
	_settings.database_url, 
	pool_pre_ping=True, 
	echo=_settings.environment == "development", 
	future=True,
	pool_size=5,
	max_overflow=10
)
_SessionLocal = async_sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)

# Redis connection
_redis_client = None

async def get_redis() -> redis.Redis:
	global _redis_client
	if _redis_client is None:
		_redis_client = redis.from_url(_settings.redis_url, decode_responses=True)
	return _redis_client


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
	session: AsyncSession = _SessionLocal()
	try:
		yield session
		await session.commit()
	except Exception:
		await session.rollback()
		raise
	finally:
		await session.close()


async def close_connections():
	"""Close all database and redis connections"""
	global _redis_client
	if _redis_client:
		await _redis_client.close()
	await _engine.dispose()

