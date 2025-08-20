from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio
from collections import defaultdict

from backend.common.config import get_settings
from backend.common.db import get_db_session
from backend.common.models import (
    Site as SiteModel, Cluster as ClusterModel, Answer as AnswerModel,
    Citation as CitationModel, Engine as EngineModel, Score as ScoreModel,
    PromptVariant as PromptVariantModel, Session as SessionModel,
    Conversion as ConversionModel
)

app = FastAPI(title="OmniFunnel • AI Visibility Score Service", version="1.0.0")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in (settings.cors_origins or [])] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreResponse(BaseModel):
    site_id: int
    cluster_id: Optional[int]
    total: float
    subscores: Dict[str, float]
    calculated_at: datetime
    engine_breakdown: Dict[str, float]
    recommendations: List[str]


class ScoreCalculationRequest(BaseModel):
    site_id: int
    cluster_id: Optional[int] = None
    date_range_days: int = 30


# Domain authority mapping for citation scoring
DOMAIN_AUTHORITY_SCORES = {
    'wikipedia.org': 95,
    'gov': 90,
    'edu': 85,
    'forbes.com': 80,
    'nytimes.com': 80,
    'reuters.com': 78,
    'bloomberg.com': 75,
    'techcrunch.com': 70,
    'medium.com': 60,
    'linkedin.com': 65,
    'github.com': 70,
    'stackoverflow.com': 75,
    # Default scores by TLD
    'com': 40,
    'org': 50,
    'net': 35,
    'io': 45,
}


class AIVisibilityScoreCalculator:
    """
    AI Visibility Score™ calculation engine
    Score range: 0-100 with weighted components per technical specification
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # Configurable weights (sum to 100%)
        self.weights = {
            'prompt_sov': 0.30,           # 30% - Prompt Share of Voice
            'generative_appearance': 0.20, # 20% - Generative appearance rate
            'citation_authority': 0.15,   # 15% - Citation authority mix
            'answer_quality': 0.10,       # 10% - Answer quality proxy
            'voice_presence': 0.05,       # 5% - Voice assistant presence
            'ai_traffic': 0.10,           # 10% - AI traffic attribution
            'ai_conversions': 0.10        # 10% - AI conversion attribution
        }
    
    async def calculate_score(
        self, 
        site_id: int, 
        cluster_id: Optional[int] = None,
        days: int = 30
    ) -> ScoreResponse:
        """Calculate comprehensive AI Visibility Score"""
        
        # Date range for calculations
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Calculate each component
        prompt_sov = await self._calculate_prompt_sov(site_id, cluster_id, start_date, end_date)
        generative_rate = await self._calculate_generative_appearance_rate(site_id, cluster_id, start_date, end_date)
        citation_authority = await self._calculate_citation_authority(site_id, cluster_id, start_date, end_date)
        answer_quality = await self._calculate_answer_quality(site_id, cluster_id, start_date, end_date)
        voice_presence = await self._calculate_voice_presence(site_id, cluster_id, start_date, end_date)
        ai_traffic = await self._calculate_ai_traffic(site_id, start_date, end_date)
        ai_conversions = await self._calculate_ai_conversions(site_id, start_date, end_date)
        
        # Calculate weighted total
        subscores = {
            'prompt_sov': prompt_sov,
            'generative_appearance': generative_rate,
            'citation_authority': citation_authority,
            'answer_quality': answer_quality,
            'voice_presence': voice_presence,
            'ai_traffic': ai_traffic,
            'ai_conversions': ai_conversions
        }
        
        total_score = sum(
            score * self.weights[component] 
            for component, score in subscores.items()
        )
        
        # Engine breakdown
        engine_breakdown = await self._calculate_engine_breakdown(site_id, cluster_id, start_date, end_date)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(subscores, engine_breakdown)
        
        # Store score in database
        await self._store_score(site_id, cluster_id, total_score, subscores)
        
        return ScoreResponse(
            site_id=site_id,
            cluster_id=cluster_id,
            total=round(total_score, 2),
            subscores={k: round(v, 2) for k, v in subscores.items()},
            calculated_at=datetime.utcnow(),
            engine_breakdown={k: round(v, 2) for k, v in engine_breakdown.items()},
            recommendations=recommendations
        )
    
    async def _calculate_prompt_sov(self, site_id: int, cluster_id: Optional[int], start_date: datetime, end_date: datetime) -> float:
        """Calculate Prompt Share of Voice (30% weight)"""
        
        # Get total prompt variants tested
        query = select(func.count(distinct(PromptVariantModel.variant_id)))
        if cluster_id:
            query = query.join(PromptModel).where(PromptModel.cluster_id == cluster_id)
        else:
            query = query.join(PromptModel).join(ClusterModel).where(ClusterModel.site_id == site_id)
        
        result = await self.db.execute(query)
        total_variants = result.scalar() or 1
        
        # Get variants where brand was mentioned (simplified - would need brand detection)
        # For now, we'll use citation count as a proxy
        citations_query = select(func.count(distinct(CitationModel.citation_id))).select_from(
            CitationModel.join(AnswerModel).join(PromptVariantModel)
        )
        if cluster_id:
            citations_query = citations_query.join(PromptModel).where(PromptModel.cluster_id == cluster_id)
        else:
            citations_query = citations_query.join(PromptModel).join(ClusterModel).where(ClusterModel.site_id == site_id)
        
        citations_result = await self.db.execute(citations_query)
        brand_mentions = citations_result.scalar() or 0
        
        # Calculate percentage
        prompt_sov = min((brand_mentions / total_variants) * 100, 100)
        return prompt_sov
    
    async def _calculate_generative_appearance_rate(self, site_id: int, cluster_id: Optional[int], start_date: datetime, end_date: datetime) -> float:
        """Calculate rate of queries that trigger generative answers"""
        
        # Count total answers generated
        query = select(func.count(AnswerModel.answer_id))
        if cluster_id:
            # Join through prompt variants to cluster
            query = query.join(PromptVariantModel).join(PromptModel).where(PromptModel.cluster_id == cluster_id)
        else:
            # Join to site through clusters
            query = query.join(PromptVariantModel).join(PromptModel).join(ClusterModel).where(ClusterModel.site_id == site_id)
        
        query = query.where(AnswerModel.raw_text.isnot(None))  # Has actual response
        
        result = await self.db.execute(query)
        answers_with_content = result.scalar() or 0
        
        # For demo, assume 80% baseline appearance rate
        # In production, this would track actual trigger rates
        baseline_rate = 80
        actual_rate = min(baseline_rate + (answers_with_content / 100), 100)
        
        return actual_rate
    
    async def _calculate_citation_authority(self, site_id: int, cluster_id: Optional[int], start_date: datetime, end_date: datetime) -> float:
        """Calculate weighted authority of citation sources"""
        
        # Get all citations
        query = select(CitationModel.normalized_domain, func.count(CitationModel.citation_id))
        if cluster_id:
            query = query.join(AnswerModel).join(PromptVariantModel).join(PromptModel).where(PromptModel.cluster_id == cluster_id)
        else:
            query = query.join(AnswerModel).join(PromptVariantModel).join(PromptModel).join(ClusterModel).where(ClusterModel.site_id == site_id)
        
        query = query.group_by(CitationModel.normalized_domain)
        
        result = await self.db.execute(query)
        citations = result.all()
        
        if not citations:
            return 0
        
        # Calculate weighted authority score
        total_weight = 0
        total_citations = 0
        
        for domain, count in citations:
            authority = self._get_domain_authority(domain)
            total_weight += authority * count
            total_citations += count
        
        if total_citations == 0:
            return 0
        
        return (total_weight / total_citations) / 100 * 100  # Normalize to 0-100
    
    def _get_domain_authority(self, domain: str) -> int:
        """Get domain authority score"""
        domain = domain.lower()
        
        # Check exact matches first
        if domain in DOMAIN_AUTHORITY_SCORES:
            return DOMAIN_AUTHORITY_SCORES[domain]
        
        # Check TLD-based scoring
        tld = domain.split('.')[-1]
        return DOMAIN_AUTHORITY_SCORES.get(tld, 30)  # Default score
    
    async def _calculate_answer_quality(self, site_id: int, cluster_id: Optional[int], start_date: datetime, end_date: datetime) -> float:
        """Calculate answer quality proxy based on length, structure, citations"""
        
        query = select(
            AnswerModel.raw_text,
            func.count(CitationModel.citation_id).label('citation_count')
        ).select_from(
            AnswerModel.outerjoin(CitationModel)
        )
        
        if cluster_id:
            query = query.join(PromptVariantModel).join(PromptModel).where(PromptModel.cluster_id == cluster_id)
        else:
            query = query.join(PromptVariantModel).join(PromptModel).join(ClusterModel).where(ClusterModel.site_id == site_id)
        
        query = query.group_by(AnswerModel.answer_id, AnswerModel.raw_text)
        
        result = await self.db.execute(query)
        answers = result.all()
        
        if not answers:
            return 0
        
        quality_scores = []
        for text, citation_count in answers:
            if not text:
                continue
                
            # Length score (optimal 100-500 words)
            word_count = len(text.split())
            length_score = min(word_count / 300 * 100, 100) if word_count <= 300 else max(100 - (word_count - 300) / 200 * 50, 50)
            
            # Citation score
            citation_score = min(citation_count * 20, 100)
            
            # Structure score (simple heuristics)
            structure_score = 0
            if any(marker in text.lower() for marker in ['1.', '2.', '•', '-', '*']):
                structure_score += 30  # Has lists
            if any(marker in text for marker in ['?', ':']):
                structure_score += 20  # Has questions/definitions
            
            # Combined quality score
            quality = (length_score * 0.4 + citation_score * 0.4 + structure_score * 0.2)
            quality_scores.append(quality)
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    async def _calculate_voice_presence(self, site_id: int, cluster_id: Optional[int], start_date: datetime, end_date: datetime) -> float:
        """Calculate voice assistant presence - placeholder for future implementation"""
        # This would integrate with voice assistant APIs
        # For now, return a baseline score
        return 25.0
    
    async def _calculate_ai_traffic(self, site_id: int, start_date: datetime, end_date: datetime) -> float:
        """Calculate AI-attributed traffic percentage"""
        
        # Count total sessions
        total_sessions_query = select(func.count(SessionModel.session_id)).where(
            SessionModel.site_id == site_id,
            SessionModel.ts >= start_date,
            SessionModel.ts <= end_date
        )
        total_result = await self.db.execute(total_sessions_query)
        total_sessions = total_result.scalar() or 1
        
        # Count AI-sourced sessions
        ai_sessions_query = select(func.count(SessionModel.session_id)).where(
            SessionModel.site_id == site_id,
            SessionModel.ai_source.isnot(None),
            SessionModel.ts >= start_date,
            SessionModel.ts <= end_date
        )
        ai_result = await self.db.execute(ai_sessions_query)
        ai_sessions = ai_result.scalar() or 0
        
        # Calculate percentage
        ai_traffic_percentage = (ai_sessions / total_sessions) * 100
        return min(ai_traffic_percentage, 100)
    
    async def _calculate_ai_conversions(self, site_id: int, start_date: datetime, end_date: datetime) -> float:
        """Calculate AI-attributed conversion rate"""
        
        # Get AI sessions with conversions
        query = select(
            func.count(distinct(SessionModel.session_id)).label('ai_sessions'),
            func.count(distinct(ConversionModel.conv_id)).label('ai_conversions')
        ).select_from(
            SessionModel.outerjoin(ConversionModel)
        ).where(
            SessionModel.site_id == site_id,
            SessionModel.ai_source.isnot(None),
            SessionModel.ts >= start_date,
            SessionModel.ts <= end_date
        )
        
        result = await self.db.execute(query)
        data = result.first()
        
        if not data or data.ai_sessions == 0:
            return 0
        
        # Calculate conversion rate and normalize to 0-100 scale
        conversion_rate = (data.ai_conversions / data.ai_sessions) * 100
        return min(conversion_rate * 10, 100)  # Scale up for score impact
    
    async def _calculate_engine_breakdown(self, site_id: int, cluster_id: Optional[int], start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Calculate score breakdown by AI engine"""
        
        query = select(
            EngineModel.name,
            func.count(AnswerModel.answer_id).label('answer_count'),
            func.count(CitationModel.citation_id).label('citation_count')
        ).select_from(
            EngineModel.join(AnswerModel).outerjoin(CitationModel)
        )
        
        if cluster_id:
            query = query.join(PromptVariantModel).join(PromptModel).where(PromptModel.cluster_id == cluster_id)
        else:
            query = query.join(PromptVariantModel).join(PromptModel).join(ClusterModel).where(ClusterModel.site_id == site_id)
        
        query = query.group_by(EngineModel.engine_id, EngineModel.name)
        
        result = await self.db.execute(query)
        engine_data = result.all()
        
        engine_scores = {}
        for engine_name, answer_count, citation_count in engine_data:
            # Simple scoring based on activity
            score = min((answer_count * 10) + (citation_count * 5), 100)
            engine_scores[engine_name] = score
        
        return engine_scores
    
    def _generate_recommendations(self, subscores: Dict[str, float], engine_breakdown: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations based on scores"""
        recommendations = []
        
        # Check each subscore for improvement opportunities
        if subscores['prompt_sov'] < 50:
            recommendations.append("Increase brand mentions by optimizing content for AI queries")
        
        if subscores['citation_authority'] < 60:
            recommendations.append("Target higher-authority publications for backlinks and mentions")
        
        if subscores['answer_quality'] < 70:
            recommendations.append("Improve content structure with lists, Q&As, and clear definitions")
        
        if subscores['ai_traffic'] < 30:
            recommendations.append("Implement AI source tracking and attribution")
        
        # Engine-specific recommendations
        low_engines = [engine for engine, score in engine_breakdown.items() if score < 40]
        if low_engines:
            recommendations.append(f"Focus optimization efforts on {', '.join(low_engines)}")
        
        if not recommendations:
            recommendations.append("Great performance! Consider expanding to additional keyword clusters")
        
        return recommendations
    
    async def _store_score(self, site_id: int, cluster_id: Optional[int], total: float, subscores: Dict[str, float]):
        """Store calculated score in database"""
        score_record = ScoreModel(
            site_id=site_id,
            cluster_id=cluster_id,
            total=total,
            subscores=subscores
        )
        self.db.add(score_record)
        await self.db.commit()


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "ai_visibility_score"}


@app.post("/v1/calculate-score", response_model=ScoreResponse)
async def calculate_score(
    request: ScoreCalculationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
) -> ScoreResponse:
    """Calculate AI Visibility Score for a site/cluster"""
    
    calculator = AIVisibilityScoreCalculator(db)
    score = await calculator.calculate_score(
        site_id=request.site_id,
        cluster_id=request.cluster_id,
        days=request.date_range_days
    )
    
    return score


@app.get("/v1/score", response_model=ScoreResponse)
async def get_latest_score(
    site_id: int,
    cluster_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db_session)
) -> ScoreResponse:
    """Get the most recent AI Visibility Score"""
    
    query = select(ScoreModel).where(ScoreModel.site_id == site_id)
    if cluster_id:
        query = query.where(ScoreModel.cluster_id == cluster_id)
    else:
        query = query.where(ScoreModel.cluster_id.is_(None))
    
    query = query.order_by(ScoreModel.ts.desc())
    
    result = await self.db.execute(query)
    score_record = result.scalar_one_or_none()
    
    if not score_record:
        raise HTTPException(status_code=404, detail="No score found for this site/cluster")
    
    return ScoreResponse(
        site_id=score_record.site_id,
        cluster_id=score_record.cluster_id,
        total=float(score_record.total),
        subscores=score_record.subscores,
        calculated_at=score_record.ts,
        engine_breakdown={},  # Would need additional query
        recommendations=[]  # Would regenerate
    )


@app.get("/v1/score-history")
async def get_score_history(
    site_id: int,
    cluster_id: Optional[int] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """Get historical AI Visibility Scores"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(ScoreModel).where(
        ScoreModel.site_id == site_id,
        ScoreModel.ts >= start_date
    )
    
    if cluster_id:
        query = query.where(ScoreModel.cluster_id == cluster_id)
    else:
        query = query.where(ScoreModel.cluster_id.is_(None))
    
    query = query.order_by(ScoreModel.ts.desc())
    
    result = await self.db.execute(query)
    scores = result.scalars().all()
    
    return [
        {
            "score_id": score.score_id,
            "total": float(score.total),
            "subscores": score.subscores,
            "calculated_at": score.ts
        }
        for score in scores
    ]


@app.on_event("startup")
async def startup():
    """Initialize the score service"""
    print("AI Visibility Score service starting up...")


@app.on_event("shutdown")
async def shutdown():
    """Clean shutdown"""
    print("AI Visibility Score service shutting down...")
    from backend.common.db import close_connections
    await close_connections()
