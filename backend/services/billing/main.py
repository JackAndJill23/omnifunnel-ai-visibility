from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from backend.common.config import get_settings

app = FastAPI(title="OmniFunnel • billing")
settings = get_settings()

app.add_middleware(
	CORSMiddleware,
	allow_origins=[str(o) for o in (settings.cors_origins or [])] or ["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, Any]:
	return {"status": "ok", "service": "billing"}
