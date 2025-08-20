from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from backend.common.config import get_settings

app = FastAPI(title="OmniFunnel • deployer")
settings = get_settings()

app.add_middleware(
	CORSMiddleware,
	allow_origins=[str(o) for o in (settings.cors_origins or [])] or ["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class PublishRequest(BaseModel):
	site_id: int
	target_path: str
	blocks: list[dict] = []
	schemas: list[dict] = []


@app.get("/health")
async def health() -> Dict[str, Any]:
	return {"status": "ok", "service": "deployer"}


@app.post("/v1/content/publish")
async def publish(req: PublishRequest) -> Dict[str, Any]:
	return {"job_id": 1, "status": "queued", "target_path": req.target_path}


@app.get("/v1/content/versions")
async def versions(site_id: int) -> Dict[str, Any]:
	return {"site_id": site_id, "versions": []}
