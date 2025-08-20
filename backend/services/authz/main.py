from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import time
import base64

from common.config import get_settings

app = FastAPI(title="OmniFunnel • authz")
settings = get_settings()

app.add_middleware(
	CORSMiddleware,
	allow_origins=[str(o) for o in (settings.cors_origins or [])] or ["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class TokenRequest(BaseModel):
	client_id: str | None = None
	client_secret: str | None = None
	scope: str | None = None


@app.get("/health")
async def health() -> Dict[str, Any]:
	return {"status": "ok", "service": "authz"}


@app.post("/v1/auth/token")
async def token(_: TokenRequest) -> Dict[str, Any]:
	# Stub: returns a simple opaque token (not real JWT) for MVP scaffold
	payload = f"user:demo|ts:{int(time.time())}"
	fake = base64.urlsafe_b64encode(payload.encode()).decode()
	return {"access_token": fake, "token_type": "bearer", "expires_in": 3600}

