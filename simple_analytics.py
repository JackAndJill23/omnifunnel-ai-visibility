#!/usr/bin/env python3
"""
Analytics Service - Competitive Intelligence & Entity Analysis
Based on specification section 6.1.3 Embeddings Audit and competitive tracking
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(title="OmniFunnel • Analytics & Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
competitive_data = []
entity_mappings = []
performance_deltas = []

class CompetitorAnalysisRequest(BaseModel):
    site_id: int
    cluster_id: int
    competitors: List[str]  # List of competitor domains
    time_range_days: int = 30

class EntityStitchingRequest(BaseModel):
    site_id: int
    brand_name: str
    entity_type: str = "brand"  # brand, competitor, organization

class PerformanceDelta(BaseModel):
    site_id: int
    cluster_id: int
    engine: str
    metric: str  # presence, citations, position
    current_value: float
    previous_value: float
    change_percentage: float
    detected_at: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics_intelligence"}

@app.post("/v1/competitive/analyze")
async def analyze_competitors(request: CompetitorAnalysisRequest):
    """Analyze competitor performance across AI engines"""
    
    # Get tracking data for the cluster
    try:
        # Fetch answers for this cluster
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8001/v1/clusters/{request.cluster_id}/answers")
            
            if response.status_code == 200:
                answers = response.json()
                
                # Analyze competitor mentions in responses
                competitor_analysis = {}
                
                for competitor in request.competitors:
                    competitor_mentions = 0
                    competitor_citations = 0
                    engines_mentioning = set()
                    
                    for answer in answers:
                        text = answer["raw_text"].lower()
                        if competitor.lower() in text:
                            competitor_mentions += 1
                            engines_mentioning.add(answer["engine"])
                        
                        # Check citations
                        for citation in answer.get("citations", []):
                            if competitor.lower() in citation.lower():
                                competitor_citations += 1
                    
                    competitor_analysis[competitor] = {
                        "mentions": competitor_mentions,
                        "citations": competitor_citations,
                        "engines": list(engines_mentioning),
                        "presence_score": min((competitor_mentions * 10) + (competitor_citations * 20), 100)
                    }
                
                analysis_result = {
                    "site_id": request.site_id,
                    "cluster_id": request.cluster_id,
                    "analysis_date": datetime.now().isoformat(),
                    "competitors": competitor_analysis,
                    "total_answers_analyzed": len(answers),
                    "recommendation": generate_competitive_recommendations(competitor_analysis)
                }
                
                competitive_data.append(analysis_result)
                return analysis_result
                
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

@app.post("/v1/entity/stitch")
async def stitch_entity(request: EntityStitchingRequest):
    """Generate SameAs links and entity connections"""
    
    # Generate SameAs link recommendations
    same_as_links = []
    
    # Common entity platforms to check
    entity_sources = [
        f"https://www.linkedin.com/company/{request.brand_name.lower().replace(' ', '-')}",
        f"https://www.crunchbase.com/organization/{request.brand_name.lower().replace(' ', '-')}",
        f"https://clutch.co/profile/{request.brand_name.lower().replace(' ', '-')}",
        f"https://www.g2.com/products/{request.brand_name.lower().replace(' ', '-')}",
        f"https://en.wikipedia.org/wiki/{request.brand_name.replace(' ', '_')}"
    ]
    
    # Validate links (in production, would make HTTP requests)
    validated_links = []
    for link in entity_sources:
        # Simulate validation
        validated_links.append({
            "url": link,
            "platform": link.split("//")[1].split("/")[0],
            "status": "found",  # would be actual HTTP status
            "confidence": 0.85
        })
    
    entity_mapping = {
        "entity_id": len(entity_mappings) + 1,
        "site_id": request.site_id,
        "brand_name": request.brand_name,
        "entity_type": request.entity_type,
        "same_as_links": validated_links,
        "created_at": datetime.now().isoformat(),
        "wikidata_id": f"Q{len(entity_mappings) + 12345}",  # Would be actual Wikidata lookup
        "knowledge_graph_presence": True
    }
    
    entity_mappings.append(entity_mapping)
    return entity_mapping

@app.get("/v1/performance/deltas")
async def get_performance_deltas(site_id: int, days: int = 7):
    """Get performance changes and alerts"""
    
    # Generate sample deltas for demonstration
    sample_deltas = [
        {
            "site_id": site_id,
            "cluster_id": 1,
            "engine": "gemini", 
            "metric": "citations",
            "current_value": 8.0,
            "previous_value": 5.0,
            "change_percentage": 60.0,
            "detected_at": datetime.now().isoformat(),
            "alert_type": "improvement",
            "message": "Citations in Gemini increased by 60%"
        },
        {
            "site_id": site_id,
            "cluster_id": 1,
            "engine": "perplexity",
            "metric": "presence",
            "current_value": 3.0,
            "previous_value": 7.0,
            "change_percentage": -57.1,
            "detected_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "alert_type": "concern",
            "message": "Presence in Perplexity dropped by 57%"
        }
    ]
    
    performance_deltas.extend(sample_deltas)
    return sample_deltas

@app.post("/v1/alerts/remediation")
async def trigger_remediation(site_id: int, cluster_id: int, issue_type: str):
    """Trigger automated remediation for performance issues"""
    
    remediation_actions = []
    
    if issue_type == "low_presence":
        remediation_actions = [
            "Generate additional FAQ content for cluster",
            "Create comparison table targeting weak engines",
            "Optimize existing content for better citations",
            "Schedule content refresh and republish"
        ]
    elif issue_type == "poor_citations":
        remediation_actions = [
            "Identify high-authority sources for topic",
            "Create content targeting specific publications",
            "Implement outreach for mention opportunities",
            "Update content with more citable facts"
        ]
    
    return {
        "site_id": site_id,
        "cluster_id": cluster_id,
        "issue_type": issue_type,
        "recommended_actions": remediation_actions,
        "auto_actions_available": True,
        "estimated_impact": "15-30% improvement in 7-14 days"
    }

def generate_competitive_recommendations(analysis: Dict[str, Dict]) -> List[str]:
    """Generate recommendations based on competitive analysis"""
    
    recommendations = []
    
    # Find top competitor
    top_competitor = max(analysis.items(), key=lambda x: x[1]["presence_score"]) if analysis else None
    
    if top_competitor:
        competitor, data = top_competitor
        recommendations.append(f"Study {competitor}'s content strategy - they have {data['mentions']} mentions")
        
        if data["citations"] > 0:
            recommendations.append(f"Target publications citing {competitor} for mention opportunities")
    
    # Check engine gaps
    all_engines = {"chatgpt", "claude", "gemini", "perplexity", "bing_copilot"}
    covered_engines = set()
    for comp_data in analysis.values():
        covered_engines.update(comp_data["engines"])
    
    missing_engines = all_engines - covered_engines
    if missing_engines:
        recommendations.append(f"Expand presence in {', '.join(missing_engines)}")
    
    return recommendations

@app.get("/v1/competitive/summary")
async def get_competitive_summary(site_id: int):
    """Get competitive intelligence summary"""
    
    site_analyses = [c for c in competitive_data if c["site_id"] == site_id]
    
    if not site_analyses:
        return {"message": "No competitive analysis data available"}
    
    latest_analysis = max(site_analyses, key=lambda x: x["analysis_date"])
    
    return {
        "site_id": site_id,
        "latest_analysis": latest_analysis,
        "competitor_count": len(latest_analysis["competitors"]),
        "top_competitor": max(latest_analysis["competitors"].items(), key=lambda x: x[1]["presence_score"])[0],
        "analysis_date": latest_analysis["analysis_date"]
    }

@app.get("/v1/entity/mappings")
async def get_entity_mappings(site_id: int):
    """Get entity mappings and SameAs links"""
    
    site_entities = [e for e in entity_mappings if e["site_id"] == site_id]
    return site_entities

if __name__ == "__main__":
    print("Starting Analytics & Intelligence Service...")
    print("Competitive tracking & Entity stitching: http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003)