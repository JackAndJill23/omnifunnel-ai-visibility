#!/usr/bin/env python3
"""
Simplified Tracker Service for Demo
Runs locally to demonstrate the frontend functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
import json
import httpx
import asyncio
import re
import os

app = FastAPI(title="OmniFunnel • Demo Tracker Service")

# CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
sites = []
clusters = []
runs = []
answers = []
citations = []

# Demo data
demo_engines = ["chatgpt", "claude", "gemini", "perplexity", "bing_copilot"]

# API Keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Real AI Engine Integration
async def query_openai(prompt: str) -> Dict[str, Any]:
    """Query OpenAI ChatGPT with real API"""
    if not OPENAI_API_KEY:
        return {"response": "OpenAI API key not configured", "citations": []}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "user", "content": f"{prompt}. Please provide sources and citations."}
                    ],
                    "max_tokens": 500
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                citations = extract_citations_from_text(content)
                return {
                    "response": content,
                    "citations": citations,
                    "confidence": 0.9,
                    "engine": "chatgpt"
                }
            else:
                return {"response": f"OpenAI API error: {response.status_code}", "citations": []}
                
    except Exception as e:
        return {"response": f"OpenAI error: {str(e)}", "citations": []}

async def query_anthropic(prompt: str) -> Dict[str, Any]:
    """Query Anthropic Claude with real API"""
    if not ANTHROPIC_API_KEY:
        return {"response": "Anthropic API key not configured", "citations": []}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 500,
                    "messages": [
                        {"role": "user", "content": f"{prompt}. Please provide sources and citations."}
                    ]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["content"][0]["text"]
                citations = extract_citations_from_text(content)
                return {
                    "response": content,
                    "citations": citations,
                    "confidence": 0.88,
                    "engine": "claude"
                }
            else:
                return {"response": f"Anthropic API error: {response.status_code}", "citations": []}
                
    except Exception as e:
        return {"response": f"Anthropic error: {str(e)}", "citations": []}

async def query_google_gemini(prompt: str) -> Dict[str, Any]:
    """Query Google Gemini with real API"""
    if not GOOGLE_API_KEY:
        return {"response": "Google API key not configured", "citations": []}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{
                            "text": f"{prompt}. Please provide detailed information with sources and citations."
                        }]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": 500,
                        "temperature": 0.7
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                citations = extract_citations_from_text(content)
                return {
                    "response": content,
                    "citations": citations,
                    "confidence": 0.92,
                    "engine": "gemini"
                }
            else:
                return {"response": f"Gemini API error: {response.status_code}", "citations": []}
                
    except Exception as e:
        return {"response": f"Gemini error: {str(e)}", "citations": []}

def extract_citations_from_text(text: str) -> List[str]:
    """Extract URLs from response text"""
    url_pattern = r'https?://[^\s\[\]()]+(?:\([^\s)]*\))?[^\s\[\]().,;!?]*'
    urls = re.findall(url_pattern, text)
    
    # Clean and validate URLs
    clean_urls = []
    for url in urls:
        url = url.rstrip('.,;!?)"\'')
        if url.startswith(('http://', 'https://')) and '.' in url:
            clean_urls.append(url)
    
    return list(set(clean_urls))  # Remove duplicates

# Pydantic models
class SiteCreate(BaseModel):
    domain: str
    cms_type: Optional[str] = None
    tenant_id: int

class SiteResponse(BaseModel):
    site_id: int
    domain: str
    cms_type: Optional[str]
    created_at: str

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
    created_at: str

class RunRequest(BaseModel):
    engine: Optional[str] = None
    variant_sample: int = 25

class RunResponse(BaseModel):
    run_id: int
    status: str
    engine: Optional[str]
    started_at: str
    variant_count: int

class AnswerResponse(BaseModel):
    answer_id: int
    raw_text: str
    citations: List[str]
    engine: str
    confidence: Optional[float]
    answer_hash: str
    created_at: str


@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "service": "tracker",
        "engines": demo_engines,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "port": os.getenv("PORT", "8001"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "platform": "OmniFunnel AI Visibility",
        "service": "Tracker",
        "status": "operational",
        "endpoints": ["/health", "/v1/engines", "/v1/sites"],
        "documentation": "https://github.com/JackAndJill23/omnifunnel-ai-visibility"
    }

@app.get("/v1/engines")
async def list_engines():
    return {
        "engines": demo_engines,
        "count": len(demo_engines)
    }

@app.post("/v1/sites", response_model=SiteResponse)
async def create_site(site: SiteCreate):
    site_id = len(sites) + 1
    new_site = {
        "site_id": site_id,
        "domain": site.domain,
        "cms_type": site.cms_type,
        "tenant_id": site.tenant_id,
        "created_at": datetime.now().isoformat()
    }
    sites.append(new_site)
    
    return SiteResponse(**new_site)

@app.get("/v1/sites", response_model=List[SiteResponse])
async def list_sites(tenant_id: int):
    tenant_sites = [s for s in sites if s.get("tenant_id") == tenant_id]
    return [SiteResponse(**site) for site in tenant_sites]

@app.post("/v1/sites/{site_id}/clusters", response_model=ClusterResponse)
async def create_cluster(site_id: int, cluster: ClusterCreate):
    # Verify site exists
    site = next((s for s in sites if s["site_id"] == site_id), None)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    cluster_id = len(clusters) + 1
    new_cluster = {
        "cluster_id": cluster_id,
        "site_id": site_id,
        "name": cluster.name,
        "description": cluster.description,
        "seed_prompt": cluster.seed_prompt,
        "keywords": cluster.keywords,
        "created_at": datetime.now().isoformat()
    }
    clusters.append(new_cluster)
    
    return ClusterResponse(
        cluster_id=new_cluster["cluster_id"],
        name=new_cluster["name"],
        description=new_cluster["description"],
        keywords=new_cluster["keywords"],
        created_at=new_cluster["created_at"]
    )

@app.get("/v1/sites/{site_id}/clusters", response_model=List[ClusterResponse])
async def list_clusters(site_id: int):
    site_clusters = [c for c in clusters if c.get("site_id") == site_id]
    return [
        ClusterResponse(
            cluster_id=c["cluster_id"],
            name=c["name"],
            description=c["description"],
            keywords=c["keywords"],
            created_at=c["created_at"]
        ) for c in site_clusters
    ]

@app.post("/v1/clusters/{cluster_id}/run", response_model=RunResponse)
async def run_cluster_tracking(cluster_id: int, request: RunRequest):
    # Find cluster
    cluster = next((c for c in clusters if c["cluster_id"] == cluster_id), None)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    run_id = len(runs) + 1
    new_run = {
        "run_id": run_id,
        "cluster_id": cluster_id,
        "status": "completed",
        "engine": request.engine,
        "started_at": datetime.now().isoformat(),
        "variant_count": request.variant_sample
    }
    runs.append(new_run)
    
    # Generate REAL AI answers using actual APIs
    engines_to_test = [request.engine] if request.engine else ["chatgpt", "claude"]  # Focus on working engines
    
    for i, engine in enumerate(engines_to_test):
        answer_id = len(answers) + 1
        
        # Query real AI engines
        if engine == "chatgpt":
            ai_response = await query_openai(cluster['seed_prompt'])
        elif engine == "claude":
            ai_response = await query_anthropic(cluster['seed_prompt'])
        elif engine == "gemini":
            ai_response = await query_google_gemini(cluster['seed_prompt'])
        else:
            # Fallback to demo for engines not yet implemented (Perplexity, Bing Copilot)
            ai_response = {
                "response": f"Demo response from {engine.upper()} for '{cluster['seed_prompt']}': This is a comprehensive analysis showing key insights and recommendations based on current industry data and research.",
                "citations": [f"https://demo-{engine}.com/source1", f"https://example-{engine}.org/source2", f"https://research-{engine}.edu/source3"],
                "confidence": 0.8,
                "engine": engine
            }
        
        real_answer = {
            "answer_id": answer_id,
            "run_id": run_id,
            "cluster_id": cluster_id,
            "engine": engine,
            "raw_text": ai_response["response"],
            "citations": ai_response["citations"],
            "confidence": ai_response.get("confidence", 0.8),
            "answer_hash": f"hash_{answer_id}_{engine}",
            "created_at": datetime.now().isoformat()
        }
        answers.append(real_answer)
        
        # Add citations
        for j, url in enumerate(ai_response["citations"]):
            citation_id = len(citations) + 1
            domain = url.split("//")[1].split("/")[0] if "//" in url else url
            citations.append({
                "citation_id": citation_id,
                "answer_id": answer_id,
                "url": url,
                "normalized_domain": domain,
                "position": j + 1
            })
    
    return RunResponse(**new_run)

@app.get("/v1/clusters/{cluster_id}/answers", response_model=List[AnswerResponse])
async def get_cluster_answers(cluster_id: int, engine: Optional[str] = None, limit: int = 50):
    cluster_answers = [a for a in answers if a.get("cluster_id") == cluster_id]
    
    if engine:
        cluster_answers = [a for a in cluster_answers if a.get("engine") == engine]
    
    return [AnswerResponse(**answer) for answer in cluster_answers[:limit]]

@app.get("/v1/answers/{answer_id}/citations")
async def get_answer_citations(answer_id: int):
    answer_citations = [c for c in citations if c.get("answer_id") == answer_id]
    return answer_citations

@app.get("/v1/runs/{run_id}/status")
async def get_run_status(run_id: int):
    run = next((r for r in runs if r["run_id"] == run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_answers = [a for a in answers if a.get("run_id") == run_id]
    
    return {
        "run_id": run_id,
        "status": run["status"],
        "started_at": run["started_at"],
        "answer_count": len(run_answers),
        "cost_estimate": 2.50
    }

if __name__ == "__main__":
    print("Starting OmniFunnel Demo Tracker Service...")
    print("This will make the frontend fully functional for testing!")
    
    # Use Railway's PORT environment variable if available
    port = int(os.getenv("PORT", 8001))
    host = "0.0.0.0"
    
    print(f"Service starting on {host}:{port}")
    print(f"Health check: http://{host}:{port}/health")
    
    uvicorn.run(app, host=host, port=port)