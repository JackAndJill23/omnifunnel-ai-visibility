#!/usr/bin/env python3
"""
GEO (Generative Engine Optimization) Service
Tracks Google AI Overviews, Bing Copilot, and generative search features
Based on specification section 6.3
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime
import uvicorn
import re

app = FastAPI(title="OmniFunnel • GEO Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
generative_triggers = []
content_gaps = []
sge_monitoring = []

class GenerativeTriggerCheck(BaseModel):
    query: str
    site_id: int
    engines: List[str] = ["google_ai_overview", "bing_copilot", "google_sge"]

class ContentGapRequest(BaseModel):
    site_id: int
    cluster_id: int
    missing_engines: List[str]

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "service": "geo_tracker",
        "features": ["ai_overviews", "sge_monitoring", "content_gaps", "trigger_detection"]
    }

@app.post("/v1/geo/check-triggers")
async def check_generative_triggers(request: GenerativeTriggerCheck):
    """Check if queries trigger AI Overviews/SGE/Copilot"""
    
    results = {}
    
    for engine in request.engines:
        if engine == "google_ai_overview":
            trigger_result = await check_google_ai_overview(request.query)
        elif engine == "bing_copilot":
            trigger_result = await check_bing_copilot(request.query)
        elif engine == "google_sge":
            trigger_result = await check_google_sge(request.query)
        else:
            trigger_result = {"triggered": False, "reason": "Engine not supported"}
        
        results[engine] = trigger_result
    
    # Store results
    trigger_data = {
        "query": request.query,
        "site_id": request.site_id,
        "results": results,
        "checked_at": datetime.now().isoformat(),
        "total_triggers": sum(1 for r in results.values() if r.get("triggered", False))
    }
    
    generative_triggers.append(trigger_data)
    return trigger_data

@app.post("/v1/geo/content-gaps")
async def analyze_content_gaps(request: ContentGapRequest):
    """Analyze content gaps for missing AI engine appearances"""
    
    # Get current cluster performance
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8001/v1/clusters/{request.cluster_id}/answers")
            
            if response.status_code == 200:
                answers = response.json()
                
                # Analyze engine coverage
                engines_with_answers = set(answer["engine"] for answer in answers)
                missing_engines = set(request.missing_engines) - engines_with_answers
                
                # Generate content recommendations for missing engines
                recommendations = []
                
                for engine in missing_engines:
                    if engine == "gemini":
                        recommendations.append({
                            "engine": engine,
                            "content_type": "structured_data",
                            "recommendation": "Create detailed comparison tables - Gemini favors structured data",
                            "priority": "high",
                            "estimated_impact": "25-40% improvement in Gemini presence"
                        })
                    elif engine == "perplexity":
                        recommendations.append({
                            "engine": engine,
                            "content_type": "research_citations",
                            "recommendation": "Add more academic and research citations - Perplexity values authoritative sources",
                            "priority": "medium",
                            "estimated_impact": "15-30% improvement in Perplexity citations"
                        })
                    elif engine == "bing_copilot":
                        recommendations.append({
                            "engine": engine,
                            "content_type": "conversational_qa",
                            "recommendation": "Create conversational Q&A format - Bing Copilot prefers dialogue structure",
                            "priority": "medium",
                            "estimated_impact": "20-35% improvement in Bing Copilot presence"
                        })
                
                gap_analysis = {
                    "site_id": request.site_id,
                    "cluster_id": request.cluster_id,
                    "analyzed_at": datetime.now().isoformat(),
                    "total_engines_tested": len(engines_with_answers),
                    "missing_engines": list(missing_engines),
                    "coverage_percentage": (len(engines_with_answers) / (len(engines_with_answers) + len(missing_engines))) * 100,
                    "recommendations": recommendations,
                    "auto_generation_available": True
                }
                
                content_gaps.append(gap_analysis)
                return gap_analysis
                
    except Exception as e:
        return {"error": f"Gap analysis failed: {str(e)}"}

@app.get("/v1/geo/sge-monitoring")
async def get_sge_monitoring(site_id: int, days: int = 7):
    """Monitor SGE (Search Generative Experience) presence"""
    
    # Sample SGE monitoring data
    sge_data = [
        {
            "date": (datetime.now() - timedelta(days=i)).isoformat(),
            "query": "ai seo tools",
            "sge_triggered": i % 3 == 0,  # Simulate intermittent triggering
            "brand_mentioned": i % 4 == 0,
            "position": i + 1 if i % 4 == 0 else None,
            "competitor_mentioned": ["semrush.com", "ahrefs.com"][i % 2] if i % 2 == 0 else None
        }
        for i in range(days)
    ]
    
    sge_monitoring.extend(sge_data)
    
    # Calculate summary metrics
    total_triggers = sum(1 for d in sge_data if d["sge_triggered"])
    brand_appearances = sum(1 for d in sge_data if d["brand_mentioned"])
    
    return {
        "site_id": site_id,
        "monitoring_period_days": days,
        "total_sge_triggers": total_triggers,
        "brand_appearances": brand_appearances,
        "appearance_rate": (brand_appearances / total_triggers * 100) if total_triggers > 0 else 0,
        "daily_data": sge_data,
        "competitor_alerts": [
            {
                "competitor": "semrush.com",
                "mentions": 3,
                "threat_level": "medium"
            }
        ]
    }

async def check_google_ai_overview(query: str) -> Dict[str, Any]:
    """Check if query triggers Google AI Overview"""
    
    # In production, this would use actual Google Search API or scraping
    # For demo, simulate trigger detection
    
    trigger_keywords = ["how to", "what is", "best", "vs", "comparison", "guide"]
    triggers = any(keyword in query.lower() for keyword in trigger_keywords)
    
    return {
        "triggered": triggers,
        "confidence": 0.85 if triggers else 0.2,
        "trigger_type": "ai_overview" if triggers else None,
        "detected_features": ["featured_snippet", "ai_generated"] if triggers else [],
        "checked_at": datetime.now().isoformat()
    }

async def check_bing_copilot(query: str) -> Dict[str, Any]:
    """Check if query triggers Bing Copilot response"""
    
    # Simulate Bing Copilot trigger detection
    conversational_indicators = ["help me", "can you", "i need", "explain", "tell me"]
    triggers = any(indicator in query.lower() for indicator in conversational_indicators) or len(query.split()) > 5
    
    return {
        "triggered": triggers,
        "confidence": 0.8 if triggers else 0.3,
        "response_type": "conversational" if triggers else None,
        "features": ["citations", "follow_up_questions"] if triggers else [],
        "checked_at": datetime.now().isoformat()
    }

async def check_google_sge(query: str) -> Dict[str, Any]:
    """Check Search Generative Experience (SGE) triggers"""
    
    # SGE typically triggers for informational queries
    informational_patterns = ["what", "how", "why", "when", "where", "best", "top", "guide"]
    triggers = any(pattern in query.lower() for pattern in informational_patterns)
    
    return {
        "triggered": triggers,
        "confidence": 0.75 if triggers else 0.25,
        "sge_type": "informational" if triggers else None,
        "expected_features": ["ai_snapshot", "source_links", "follow_up"] if triggers else [],
        "checked_at": datetime.now().isoformat()
    }

@app.post("/v1/geo/auto-optimize")
async def auto_optimize_for_generative(site_id: int, cluster_id: int, target_engine: str):
    """Automatically optimize content for specific generative engine"""
    
    optimization_strategies = {
        "google_ai_overview": {
            "content_types": ["faq", "definition", "step_by_step"],
            "structure": "Use clear headings and bullet points",
            "length": "Keep answers between 40-80 words",
            "citations": "Include 2-3 authoritative sources"
        },
        "bing_copilot": {
            "content_types": ["conversational_qa", "detailed_explanations"],
            "structure": "Use natural language and dialogue format",
            "length": "Longer form content (100-200 words per answer)",
            "citations": "Include diverse source types"
        },
        "google_sge": {
            "content_types": ["comprehensive_guides", "comparison_tables"],
            "structure": "Use structured data and clear hierarchies",
            "length": "Mix of short answers and detailed explanations",
            "citations": "Focus on high-authority academic and news sources"
        }
    }
    
    strategy = optimization_strategies.get(target_engine, {})
    
    return {
        "site_id": site_id,
        "cluster_id": cluster_id,
        "target_engine": target_engine,
        "optimization_strategy": strategy,
        "auto_actions": [
            "Generate optimized content blocks",
            "Update existing content structure", 
            "Add engine-specific schema markup",
            "Schedule content refresh"
        ],
        "estimated_timeline": "3-7 days for implementation",
        "expected_improvement": "20-45% increase in presence"
    }

@app.get("/v1/geo/trigger-history")
async def get_trigger_history(site_id: int):
    """Get historical trigger data"""
    
    site_triggers = [t for t in generative_triggers if t["site_id"] == site_id]
    return site_triggers

@app.get("/v1/geo/gaps")
async def get_content_gaps(site_id: int):
    """Get content gap analysis results"""
    
    site_gaps = [g for g in content_gaps if g["site_id"] == site_id]
    return site_gaps

if __name__ == "__main__":
    print("Starting GEO (Generative Engine Optimization) Service...")
    print("AI Overviews & SGE tracking: http://localhost:8006")
    uvicorn.run(app, host="0.0.0.0", port=8006)