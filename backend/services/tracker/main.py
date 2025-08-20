from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
import asyncio
import hashlib
from datetime import datetime

from backend.common.config import get_settings
from backend.common.db import get_db_session
from backend.common.models import (
    Site as SiteModel, Cluster as ClusterModel, Prompt as PromptModel,
    PromptVariant as PromptVariantModel, Run as RunModel, Answer as AnswerModel,
    Citation as CitationModel, Engine as EngineModel
)
from .engines import engine_manager, Answer as EngineAnswer
from .prompt_variants import generate_prompt_variants, PromptVariant

app = FastAPI(title="OmniFunnel • Tracker Service", version="1.0.0")

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in (settings.cors_origins or [])] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class SiteCreate(BaseModel):
    domain: str
    cms_type: Optional[str] = None
    tenant_id: int


class SiteResponse(BaseModel):
    site_id: int
    domain: str
    cms_type: Optional[str]
    created_at: datetime


class ClusterCreate(BaseModel):
    name: str
    description: Optional[str] = None
    seed_prompt: str
    keywords: List[str] = []


class ClusterResponse(BaseModel):
    cluster_id: int
    name: str
    description: Optional[str]
    keywords: List[str]
    created_at: datetime


class RunRequest(BaseModel):
    engine: Optional[str] = None  # If None, runs all engines
    locale: Optional[str] = "en"
    variant_sample: int = Field(default=25, ge=1, le=100)  # How many variants to test


class RunResponse(BaseModel):
    run_id: int
    status: str
    engine: Optional[str]
    started_at: datetime
    variant_count: int


class AnswerResponse(BaseModel):
    answer_id: int
    raw_text: str
    citations: List[str]
    engine: str
    confidence: Optional[float]
    answer_hash: str
    created_at: datetime


class CitationResponse(BaseModel):
    citation_id: int
    url: str
    normalized_domain: str
    position: int


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "tracker", "engines": engine_manager.list_engines()}


@app.get("/v1/engines")
async def list_engines() -> Dict[str, Any]:
    """List all available AI engines"""
    return {
        "engines": engine_manager.list_engines(),
        "count": len(engine_manager.list_engines())
    }


@app.post("/v1/sites", response_model=SiteResponse)
async def create_site(
    site: SiteCreate, 
    db: AsyncSession = Depends(get_db_session)
) -> SiteResponse:
    """Create a new site for tracking"""
    db_site = SiteModel(
        domain=site.domain,
        cms_type=site.cms_type,
        tenant_id=site.tenant_id
    )
    db.add(db_site)
    await db.flush()
    await db.refresh(db_site)
    
    return SiteResponse(
        site_id=db_site.site_id,
        domain=db_site.domain,
        cms_type=db_site.cms_type,
        created_at=db_site.created_at
    )


@app.get("/v1/sites", response_model=List[SiteResponse])
async def list_sites(
    tenant_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> List[SiteResponse]:
    """List all sites for a tenant"""
    result = await db.execute(
        select(SiteModel).where(SiteModel.tenant_id == tenant_id)
    )
    sites = result.scalars().all()
    
    return [
        SiteResponse(
            site_id=site.site_id,
            domain=site.domain,
            cms_type=site.cms_type,
            created_at=site.created_at
        ) for site in sites
    ]


@app.post("/v1/sites/{site_id}/clusters", response_model=ClusterResponse)
async def create_cluster(
    site_id: int,
    cluster: ClusterCreate,
    db: AsyncSession = Depends(get_db_session)
) -> ClusterResponse:
    """Create a new prompt cluster for a site"""
    
    # Verify site exists
    site_result = await db.execute(select(SiteModel).where(SiteModel.site_id == site_id))
    if not site_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Create cluster
    db_cluster = ClusterModel(
        site_id=site_id,
        name=cluster.name,
        description=cluster.description,
        keywords=cluster.keywords
    )
    db.add(db_cluster)
    await db.flush()
    await db.refresh(db_cluster)
    
    # Create the seed prompt
    db_prompt = PromptModel(
        site_id=site_id,
        cluster_id=db_cluster.cluster_id,
        text=cluster.seed_prompt,
        locale="en"
    )
    db.add(db_prompt)
    await db.flush()
    
    # Generate prompt variants
    variants = generate_prompt_variants(cluster.seed_prompt, count=75)
    
    for variant in variants:
        db_variant = PromptVariantModel(
            prompt_id=db_prompt.prompt_id,
            text=variant.text,
            generation_params={
                "variant_type": variant.variant_type.value,
                "confidence": variant.confidence,
                **variant.generation_params
            }
        )
        db.add(db_variant)
    
    await db.commit()
    
    return ClusterResponse(
        cluster_id=db_cluster.cluster_id,
        name=db_cluster.name,
        description=db_cluster.description,
        keywords=db_cluster.keywords,
        created_at=db_cluster.created_at
    )


@app.get("/v1/sites/{site_id}/clusters", response_model=List[ClusterResponse])
async def list_clusters(
    site_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> List[ClusterResponse]:
    """List all clusters for a site"""
    result = await db.execute(
        select(ClusterModel).where(ClusterModel.site_id == site_id)
    )
    clusters = result.scalars().all()
    
    return [
        ClusterResponse(
            cluster_id=cluster.cluster_id,
            name=cluster.name,
            description=cluster.description,
            keywords=cluster.keywords,
            created_at=cluster.created_at
        ) for cluster in clusters
    ]


@app.post("/v1/clusters/{cluster_id}/run", response_model=RunResponse)
async def run_cluster_tracking(
    cluster_id: int,
    request: RunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
) -> RunResponse:
    """Start tracking run for a cluster across AI engines"""
    
    # Get cluster and its prompts
    cluster_result = await db.execute(select(ClusterModel).where(ClusterModel.cluster_id == cluster_id))
    cluster = cluster_result.scalar_one_or_none()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Get prompt variants for this cluster
    prompts_result = await db.execute(
        select(PromptModel).where(PromptModel.cluster_id == cluster_id)
    )
    prompts = prompts_result.scalars().all()
    
    if not prompts:
        raise HTTPException(status_code=400, detail="No prompts found for cluster")
    
    # Get variants for the first prompt (seed prompt)
    variants_result = await db.execute(
        select(PromptVariantModel).where(PromptVariantModel.prompt_id == prompts[0].prompt_id)
        .limit(request.variant_sample)
    )
    variants = variants_result.scalars().all()
    
    # Create run record
    db_run = RunModel(
        engine_id=None,  # Will be set per engine
        status="queued"
    )
    db.add(db_run)
    await db.flush()
    await db.refresh(db_run)
    
    # Schedule background task to execute the run
    background_tasks.add_task(
        execute_tracking_run,
        db_run.run_id,
        cluster_id,
        [v.text for v in variants],
        request.engine
    )
    
    return RunResponse(
        run_id=db_run.run_id,
        status="queued",
        engine=request.engine,
        started_at=db_run.started_at,
        variant_count=len(variants)
    )


@app.get("/v1/runs/{run_id}/status")
async def get_run_status(
    run_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get status of a tracking run"""
    result = await db.execute(select(RunModel).where(RunModel.run_id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Get answer count
    answers_result = await db.execute(
        select(AnswerModel).where(AnswerModel.run_id == run_id)
    )
    answers = answers_result.scalars().all()
    
    return {
        "run_id": run_id,
        "status": run.status,
        "started_at": run.started_at,
        "answer_count": len(answers),
        "cost_estimate": float(run.cost_estimate) if run.cost_estimate else 0
    }


@app.get("/v1/clusters/{cluster_id}/answers", response_model=List[AnswerResponse])
async def get_cluster_answers(
    cluster_id: int,
    engine: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
) -> List[AnswerResponse]:
    """Get recent answers for a cluster"""
    
    # Build query
    query = (
        select(AnswerModel, RunModel, EngineModel)
        .join(RunModel, AnswerModel.run_id == RunModel.run_id)
        .join(EngineModel, AnswerModel.engine_id == EngineModel.engine_id)
        .limit(limit)
        .order_by(AnswerModel.answer_id.desc())
    )
    
    if engine:
        query = query.where(EngineModel.name == engine)
    
    result = await db.execute(query)
    rows = result.all()
    
    answers = []
    for answer, run, engine_obj in rows:
        # Get citations for this answer
        citations_result = await db.execute(
            select(CitationModel).where(CitationModel.answer_id == answer.answer_id)
        )
        citations = [c.url for c in citations_result.scalars().all()]
        
        answers.append(AnswerResponse(
            answer_id=answer.answer_id,
            raw_text=answer.raw_text,
            citations=citations,
            engine=engine_obj.name,
            confidence=None,  # Would extract from token_counts if available
            answer_hash=answer.answer_hash,
            created_at=run.started_at
        ))
    
    return answers


@app.get("/v1/answers/{answer_id}/citations", response_model=List[CitationResponse])
async def get_answer_citations(
    answer_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> List[CitationResponse]:
    """Get citations for a specific answer"""
    result = await db.execute(
        select(CitationModel).where(CitationModel.answer_id == answer_id)
        .order_by(CitationModel.position)
    )
    citations = result.scalars().all()
    
    return [
        CitationResponse(
            citation_id=citation.citation_id,
            url=citation.url,
            normalized_domain=citation.normalized_domain,
            position=citation.position
        ) for citation in citations
    ]


async def execute_tracking_run(
    run_id: int, 
    cluster_id: int, 
    variant_texts: List[str], 
    target_engine: Optional[str] = None
):
    """Background task to execute the actual tracking run"""
    async with get_db_session().__anext__() as db:
        try:
            # Update run status
            run_result = await db.execute(select(RunModel).where(RunModel.run_id == run_id))
            run = run_result.scalar_one()
            run.status = "running"
            await db.commit()
            
            # Determine which engines to query
            engines_to_query = [target_engine] if target_engine else engine_manager.list_engines()
            
            # Query engines for each variant
            for variant_text in variant_texts:
                for engine_name in engines_to_query:
                    try:
                        # Get engine from database
                        engine_result = await db.execute(
                            select(EngineModel).where(EngineModel.name == engine_name)
                        )
                        engine_obj = engine_result.scalar_one_or_none()
                        if not engine_obj:
                            continue
                        
                        # Query the engine
                        answer = await engine_manager.query_engine(engine_name, variant_text)
                        
                        # Calculate answer hash
                        answer_hash = hashlib.md5(answer.raw_text.encode()).hexdigest()
                        
                        # Store answer
                        db_answer = AnswerModel(
                            run_id=run_id,
                            engine_id=engine_obj.engine_id,
                            raw_text=answer.raw_text,
                            token_counts={"length": answer.answer_length},
                            answer_hash=answer_hash
                        )
                        db.add(db_answer)
                        await db.flush()
                        await db.refresh(db_answer)
                        
                        # Store citations
                        for i, citation_url in enumerate(answer.citations):
                            domain = engine_manager.get_engine(engine_name).normalize_domain(citation_url)
                            db_citation = CitationModel(
                                answer_id=db_answer.answer_id,
                                url=citation_url,
                                normalized_domain=domain,
                                position=i + 1
                            )
                            db.add(db_citation)
                        
                        await db.commit()
                        
                        # Small delay to respect rate limits
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"Error querying {engine_name} with '{variant_text}': {e}")
                        continue
            
            # Update run status to completed
            run.status = "completed"
            await db.commit()
            
        except Exception as e:
            # Update run status to failed
            run_result = await db.execute(select(RunModel).where(RunModel.run_id == run_id))
            run = run_result.scalar_one()
            run.status = "failed"
            await db.commit()
            print(f"Tracking run {run_id} failed: {e}")


@app.on_event("startup")
async def startup():
    """Initialize the tracker service"""
    print("Tracker service starting up...")
    print(f"Available engines: {engine_manager.list_engines()}")


@app.on_event("shutdown")
async def shutdown():
    """Clean shutdown"""
    print("Tracker service shutting down...")
    from backend.common.db import close_connections
    await close_connections()
