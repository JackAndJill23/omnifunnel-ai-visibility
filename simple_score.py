#!/usr/bin/env python3
"""
Simplified Score Service for Demo
Implements the AI Visibility Score calculation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn

app = FastAPI(title="OmniFunnel • Demo Score Service")

# CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
scores = []

class ScoreCalculationRequest(BaseModel):
    site_id: int
    cluster_id: Optional[int] = None
    date_range_days: int = 30

class ScoreResponse(BaseModel):
    site_id: int
    cluster_id: Optional[int]
    total: float
    subscores: Dict[str, float]
    calculated_at: str
    engine_breakdown: Dict[str, float]
    recommendations: List[str]

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai_visibility_score"}

@app.post("/v1/calculate-score")
async def calculate_score(request: ScoreCalculationRequest):
    """Calculate AI Visibility Score"""
    
    # Generate realistic demo scores based on site_id for consistency
    import random
    random.seed(request.site_id * 100 + (request.cluster_id or 0))
    
    # Calculate component scores (demo values)
    subscores = {
        'prompt_sov': round(random.uniform(45, 85), 1),           # 30% weight
        'generative_appearance': round(random.uniform(60, 90), 1), # 20% weight
        'citation_authority': round(random.uniform(40, 80), 1),   # 15% weight
        'answer_quality': round(random.uniform(50, 85), 1),       # 10% weight
        'voice_presence': round(random.uniform(15, 40), 1),       # 5% weight
        'ai_traffic': round(random.uniform(20, 60), 1),           # 10% weight
        'ai_conversions': round(random.uniform(10, 45), 1)        # 10% weight
    }
    
    # Calculate weighted total
    weights = {
        'prompt_sov': 0.30,
        'generative_appearance': 0.20,
        'citation_authority': 0.15,
        'answer_quality': 0.10,
        'voice_presence': 0.05,
        'ai_traffic': 0.10,
        'ai_conversions': 0.10
    }
    
    total_score = sum(score * weights[component] for component, score in subscores.items())
    
    # Engine breakdown
    engine_breakdown = {
        'chatgpt': round(random.uniform(40, 85), 1),
        'claude': round(random.uniform(35, 80), 1),
        'gemini': round(random.uniform(45, 90), 1),
        'perplexity': round(random.uniform(30, 75), 1),
        'bing_copilot': round(random.uniform(25, 70), 1)
    }
    
    # Generate recommendations
    recommendations = []
    if subscores['prompt_sov'] < 60:
        recommendations.append("Increase brand mentions by optimizing content for AI queries")
    if subscores['citation_authority'] < 60:
        recommendations.append("Target higher-authority publications for backlinks and mentions")
    if subscores['answer_quality'] < 70:
        recommendations.append("Improve content structure with lists, Q&As, and clear definitions")
    if subscores['ai_traffic'] < 40:
        recommendations.append("Implement AI source tracking and attribution")
    
    low_engines = [engine for engine, score in engine_breakdown.items() if score < 50]
    if low_engines:
        recommendations.append(f"Focus optimization efforts on {', '.join(low_engines)}")
    
    if not recommendations:
        recommendations.append("Great performance! Consider expanding to additional keyword clusters")
    
    # Create score response
    score_data = {
        "site_id": request.site_id,
        "cluster_id": request.cluster_id,
        "total": round(total_score, 1),
        "subscores": subscores,
        "calculated_at": datetime.now().isoformat(),
        "engine_breakdown": engine_breakdown,
        "recommendations": recommendations
    }
    
    # Store score
    score_data["score_id"] = len(scores) + 1
    scores.append(score_data)
    
    return score_data

@app.get("/v1/score")
async def get_latest_score(site_id: int, cluster_id: Optional[int] = None):
    """Get the most recent AI Visibility Score"""
    
    # Find most recent score for this site/cluster
    site_scores = [s for s in scores if s["site_id"] == site_id]
    
    if cluster_id:
        site_scores = [s for s in site_scores if s.get("cluster_id") == cluster_id]
    else:
        site_scores = [s for s in site_scores if s.get("cluster_id") is None]
    
    if not site_scores:
        raise HTTPException(status_code=404, detail="No score found for this site/cluster")
    
    # Return most recent
    latest_score = max(site_scores, key=lambda x: x["calculated_at"])
    return latest_score

@app.get("/v1/score-history")
async def get_score_history(site_id: int, cluster_id: Optional[int] = None, days: int = 30):
    """Get historical AI Visibility Scores"""
    
    site_scores = [s for s in scores if s["site_id"] == site_id]
    
    if cluster_id:
        site_scores = [s for s in site_scores if s.get("cluster_id") == cluster_id]
    
    # Sort by date (most recent first)
    site_scores.sort(key=lambda x: x["calculated_at"], reverse=True)
    
    return site_scores

if __name__ == "__main__":
    print("Starting OmniFunnel Demo Score Service...")
    print("AI Visibility Score API: http://localhost:8004")
    uvicorn.run(app, host="0.0.0.0", port=8004)