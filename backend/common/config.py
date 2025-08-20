from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List, Optional
import os


class Settings(BaseSettings):
	# Core service settings
	api_host: str = os.getenv("API_HOST", "0.0.0.0")
	service_name: str = os.getenv("SERVICE_NAME", "omnifunnel")
	environment: str = os.getenv("ENVIRONMENT", "development")
	
	# Database
	database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://omnifunnel:omnifunnel@db:5432/omnifunnel")
	redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
	
	# Authentication
	jwt_secret: str = os.getenv("JWT_SECRET", "dev_jwt_secret_change_me")
	jwt_alg: str = os.getenv("JWT_ALG", "HS256")
	cors_origins: List[AnyHttpUrl] = []
	
	# AI API Keys
	openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
	anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
	google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
	pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
	
	# External integrations
	stripe_secret_key: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
	stripe_webhook_secret: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
	
	# Tracking settings
	max_prompts_per_cluster: int = int(os.getenv("MAX_PROMPTS_PER_CLUSTER", "100"))
	default_run_frequency: str = os.getenv("DEFAULT_RUN_FREQUENCY", "daily")
	
	# Rate limiting
	requests_per_minute: int = int(os.getenv("REQUESTS_PER_MINUTE", "60"))
	max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))

	class Config:
		case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()

