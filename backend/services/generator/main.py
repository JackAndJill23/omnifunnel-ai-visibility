from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import httpx
import json
import re
from datetime import datetime

from backend.common.config import get_settings
from backend.common.db import get_db_session
from backend.common.models import Block as BlockModel, Schema as SchemaModel

app = FastAPI(title="OmniFunnel • Content Generation Engine", version="1.0.0")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
OPENAI_API_KEY = settings.openai_api_key

class GenerateRequest(BaseModel):
    topic: str
    site_id: int
    formats: List[str] = Field(default=["faq", "table", "para", "jsonld"])
    tone: str = Field(default="professional")
    max_tokens: int = Field(default=2000)
    include_citations: bool = Field(default=True)

class ContentBlock(BaseModel):
    type: str  # faq, table, para, list
    title: str
    content: Dict[str, Any]
    word_count: int
    citations: List[str]
    evaluator_score: float

class SchemaBlock(BaseModel):
    type: str  # FAQPage, QAPage, HowTo, Product, etc.
    jsonld: Dict[str, Any]
    path: str

class GenerationResponse(BaseModel):
    topic: str
    site_id: int
    blocks: List[ContentBlock]
    schemas: List[SchemaBlock]
    internal_links: List[str]
    generated_at: str
    total_word_count: int
    evaluator_score: float

class ContentStructuringEngine:
    """LEO (Language Engine Optimization) - Content Structuring Engine"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_multi_format_pack(self, topic: str, site_id: int, formats: List[str]) -> Dict[str, Any]:
        """Generate multi-format content pack for AI optimization"""
        
        blocks = []
        schemas = []
        total_word_count = 0
        
        # Generate FAQ block
        if "faq" in formats:
            faq_block = await self._generate_faq_block(topic)
            blocks.append(faq_block)
            total_word_count += faq_block["word_count"]
        
        # Generate comparison table
        if "table" in formats:
            table_block = await self._generate_table_block(topic)
            blocks.append(table_block)
            total_word_count += table_block["word_count"]
        
        # Generate definitional paragraph
        if "para" in formats:
            para_block = await self._generate_paragraph_block(topic)
            blocks.append(para_block)
            total_word_count += para_block["word_count"]
        
        # Generate list format
        if "list" in formats:
            list_block = await self._generate_list_block(topic)
            blocks.append(list_block)
            total_word_count += list_block["word_count"]
        
        # Generate JSON-LD schemas
        if "jsonld" in formats:
            faq_schema = await self._generate_faq_schema(topic, blocks)
            schemas.append(faq_schema)
            
            article_schema = await self._generate_article_schema(topic)
            schemas.append(article_schema)
        
        # Calculate overall evaluator score
        evaluator_score = sum(block["evaluator_score"] for block in blocks) / len(blocks) if blocks else 0
        
        # Generate internal link recommendations
        internal_links = await self._generate_internal_links(topic)
        
        return {
            "topic": topic,
            "site_id": site_id,
            "blocks": blocks,
            "schemas": schemas,
            "internal_links": internal_links,
            "generated_at": datetime.now().isoformat(),
            "total_word_count": total_word_count,
            "evaluator_score": round(evaluator_score, 2)
        }
    
    async def _generate_faq_block(self, topic: str) -> Dict[str, Any]:
        """Generate FAQ block optimized for AI engines"""
        
        prompt = f"""Create a comprehensive FAQ about '{topic}' that would help AI engines provide better answers. 

Requirements:
- 8-12 questions and answers
- Each answer should be 50-120 words
- Include specific facts and statistics where possible
- Optimize for voice search and conversational queries
- Format as JSON with questions and answers arrays

Return only valid JSON in this format:
{{"questions": ["Q1", "Q2"], "answers": ["A1", "A2"]}}"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 1500,
                        "temperature": 0.7
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # Extract JSON from response
                    faq_data = self._extract_json(content)
                    if not faq_data:
                        # Fallback if JSON extraction fails
                        faq_data = {"questions": [f"What is {topic}?"], "answers": [f"Information about {topic}"]}
                    
                    word_count = sum(len(answer.split()) for answer in faq_data.get("answers", []))
                    citations = self._extract_citations(content)
                    
                    return {
                        "type": "faq",
                        "title": f"Frequently Asked Questions: {topic}",
                        "content": faq_data,
                        "word_count": word_count,
                        "citations": citations,
                        "evaluator_score": self._evaluate_content_quality(faq_data, "faq")
                    }
        except Exception as e:
            print(f"Error generating FAQ: {e}")
        
        # Fallback FAQ
        return {
            "type": "faq",
            "title": f"FAQ: {topic}",
            "content": {
                "questions": [f"What is {topic}?", f"How does {topic} work?"],
                "answers": [f"Overview of {topic}", f"Explanation of {topic} functionality"]
            },
            "word_count": 20,
            "citations": [],
            "evaluator_score": 60.0
        }
    
    async def _generate_table_block(self, topic: str) -> Dict[str, Any]:
        """Generate comparison table optimized for AI engines"""
        
        prompt = f"""Create a comprehensive comparison table about '{topic}' that AI engines would cite.

Requirements:
- Compare 5-8 options/solutions/tools
- Include columns: Name, Key Features, Pricing, Best For, Rating
- Each cell should be concise but informative (10-30 words)
- Include specific data points and facts
- Format as JSON

Return only valid JSON in this format:
{{"headers": ["Name", "Features", "Pricing", "Best For"], "rows": [["Item1", "Feature1", "Price1", "Use1"]]}}"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 1200,
                        "temperature": 0.5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    table_data = self._extract_json(content)
                    if not table_data:
                        table_data = {
                            "headers": ["Option", "Description"],
                            "rows": [[f"{topic} Option 1", "Description 1"]]
                        }
                    
                    word_count = sum(len(str(cell).split()) for row in table_data.get("rows", []) for cell in row)
                    citations = self._extract_citations(content)
                    
                    return {
                        "type": "table",
                        "title": f"Comparison: {topic}",
                        "content": table_data,
                        "word_count": word_count,
                        "citations": citations,
                        "evaluator_score": self._evaluate_content_quality(table_data, "table")
                    }
        except Exception as e:
            print(f"Error generating table: {e}")
        
        # Fallback table
        return {
            "type": "table",
            "title": f"Comparison: {topic}",
            "content": {
                "headers": ["Option", "Features"],
                "rows": [[f"{topic} Option", "Key features"]]
            },
            "word_count": 10,
            "citations": [],
            "evaluator_score": 50.0
        }
    
    async def _generate_paragraph_block(self, topic: str) -> Dict[str, Any]:
        """Generate definitional paragraph (50-120 words)"""
        
        prompt = f"""Write a clear, concise definition and overview of '{topic}' in exactly 80-100 words.

Requirements:
- Clear, authoritative tone
- Include key benefits and use cases
- Mention 2-3 specific examples or facts
- Optimized for AI engine citations
- No marketing fluff, just factual information"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 200,
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    
                    word_count = len(content.split())
                    citations = self._extract_citations(content)
                    
                    return {
                        "type": "para",
                        "title": f"What is {topic}?",
                        "content": {"text": content},
                        "word_count": word_count,
                        "citations": citations,
                        "evaluator_score": self._evaluate_content_quality({"text": content}, "para")
                    }
        except Exception as e:
            print(f"Error generating paragraph: {e}")
        
        # Fallback paragraph
        return {
            "type": "para",
            "title": f"About {topic}",
            "content": {"text": f"{topic} is an important concept in modern digital marketing."},
            "word_count": 10,
            "citations": [],
            "evaluator_score": 40.0
        }
    
    async def _generate_list_block(self, topic: str) -> Dict[str, Any]:
        """Generate bullet list optimized for AI engines"""
        
        prompt = f"""Create a comprehensive bullet list about '{topic}' that AI engines would find useful to cite.

Requirements:
- 6-10 key points
- Each point should be 15-25 words
- Include specific benefits, features, or facts
- Use active voice and clear language
- Format as JSON array

Return only valid JSON: {{"items": ["Point 1", "Point 2", ...]}}"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 800,
                        "temperature": 0.4
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    list_data = self._extract_json(content)
                    if not list_data:
                        list_data = {"items": [f"Key aspect of {topic}", f"Important feature of {topic}"]}
                    
                    word_count = sum(len(item.split()) for item in list_data.get("items", []))
                    citations = self._extract_citations(content)
                    
                    return {
                        "type": "list",
                        "title": f"Key Points: {topic}",
                        "content": list_data,
                        "word_count": word_count,
                        "citations": citations,
                        "evaluator_score": self._evaluate_content_quality(list_data, "list")
                    }
        except Exception as e:
            print(f"Error generating list: {e}")
        
        # Fallback list
        return {
            "type": "list",
            "title": f"About {topic}",
            "content": {"items": [f"Key feature of {topic}", f"Important aspect of {topic}"]},
            "word_count": 10,
            "citations": [],
            "evaluator_score": 45.0
        }
    
    async def _generate_faq_schema(self, topic: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate FAQPage JSON-LD schema"""
        
        # Find FAQ block
        faq_block = next((block for block in blocks if block["type"] == "faq"), None)
        
        if not faq_block:
            return {
                "type": "FAQPage",
                "jsonld": {},
                "path": f"/answers/{topic.lower().replace(' ', '-')}"
            }
        
        # Build FAQPage schema
        faq_items = []
        questions = faq_block["content"].get("questions", [])
        answers = faq_block["content"].get("answers", [])
        
        for q, a in zip(questions, answers):
            faq_items.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a
                }
            })
        
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        }
        
        return {
            "type": "FAQPage",
            "jsonld": schema,
            "path": f"/answers/{topic.lower().replace(' ', '-')}-faq"
        }
    
    async def _generate_article_schema(self, topic: str) -> Dict[str, Any]:
        """Generate Article JSON-LD schema"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"Complete Guide to {topic}",
            "description": f"Comprehensive information about {topic} including key features, benefits, and recommendations.",
            "author": {
                "@type": "Organization",
                "name": "AI SEO Expert"
            },
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat()
        }
        
        return {
            "type": "Article", 
            "jsonld": schema,
            "path": f"/answers/{topic.lower().replace(' ', '-')}"
        }
    
    async def _generate_internal_links(self, topic: str) -> List[str]:
        """Generate internal link recommendations"""
        
        # Generate related topic suggestions
        related_topics = [
            f"{topic} best practices",
            f"{topic} implementation guide", 
            f"{topic} comparison",
            f"{topic} pricing",
            f"{topic} reviews"
        ]
        
        return [f"/answers/{t.lower().replace(' ', '-')}" for t in related_topics]
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from AI response text"""
        try:
            # Look for JSON blocks
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except:
            return None
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract URLs from content"""
        url_pattern = r'https?://[^\s\[\]()]+(?:\([^\s)]*\))?[^\s\[\]().,;!?]*'
        urls = re.findall(url_pattern, text)
        return [url.rstrip('.,;!?)"\'') for url in urls if url.startswith(('http://', 'https://'))]
    
    def _evaluate_content_quality(self, content: Dict[str, Any], content_type: str) -> float:
        """Evaluate content for 'citatability' score"""
        
        score = 50.0  # Base score
        
        if content_type == "faq":
            questions = content.get("questions", [])
            answers = content.get("answers", [])
            
            # More questions = better
            score += min(len(questions) * 5, 30)
            
            # Check answer quality
            for answer in answers:
                words = len(answer.split())
                if 50 <= words <= 120:  # Optimal length
                    score += 5
                if any(keyword in answer.lower() for keyword in ["specific", "example", "data", "research"]):
                    score += 3
        
        elif content_type == "table":
            headers = content.get("headers", [])
            rows = content.get("rows", [])
            
            score += min(len(headers) * 3, 15)
            score += min(len(rows) * 2, 20)
            
        elif content_type == "para":
            text = content.get("text", "")
            words = len(text.split())
            
            if 80 <= words <= 120:  # Optimal length
                score += 20
            elif 50 <= words <= 150:
                score += 10
            
        elif content_type == "list":
            items = content.get("items", [])
            score += min(len(items) * 4, 25)
        
        return min(score, 100.0)

# Global content engine
content_engine = ContentStructuringEngine()

@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "content_generator", "features": ["faq", "table", "para", "list", "jsonld"]}

@app.post("/v1/content/generate", response_model=GenerationResponse)
async def generate_content(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db_session)
) -> GenerationResponse:
    """Generate multi-format content pack optimized for AI engines"""
    
    # Generate content
    result = await content_engine.generate_multi_format_pack(
        topic=req.topic,
        site_id=req.site_id,
        formats=req.formats
    )
    
    # Store blocks in database
    for block_data in result["blocks"]:
        db_block = BlockModel(
            site_id=req.site_id,
            type=block_data["type"],
            json_payload=block_data["content"],
            version=1
        )
        db.add(db_block)
    
    # Store schemas in database
    for schema_data in result["schemas"]:
        db_schema = SchemaModel(
            site_id=req.site_id,
            jsonld=schema_data["jsonld"],
            version=1,
            path=schema_data["path"]
        )
        db.add(db_schema)
    
    await db.commit()
    
    return GenerationResponse(**result)

@app.get("/v1/content/blocks")
async def get_content_blocks(
    site_id: int,
    content_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """Get content blocks for a site"""
    
    query = db.select(BlockModel).where(BlockModel.site_id == site_id)
    if content_type:
        query = query.where(BlockModel.type == content_type)
    
    result = await db.execute(query)
    blocks = result.scalars().all()
    
    return [
        {
            "block_id": block.block_id,
            "type": block.type,
            "content": block.json_payload,
            "version": block.version
        }
        for block in blocks
    ]

@app.get("/v1/content/schemas")
async def get_schemas(
    site_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """Get JSON-LD schemas for a site"""
    
    result = await db.execute(
        db.select(SchemaModel).where(SchemaModel.site_id == site_id)
    )
    schemas = result.scalars().all()
    
    return [
        {
            "schema_id": schema.schema_id,
            "type": schema.jsonld.get("@type", "Unknown"),
            "jsonld": schema.jsonld,
            "path": schema.path,
            "version": schema.version
        }
        for schema in schemas
    ]

@app.post("/v1/content/evaluate")
async def evaluate_content(content: Dict[str, Any], content_type: str) -> Dict[str, float]:
    """Evaluate content for citatability score"""
    
    score = content_engine._evaluate_content_quality(content, content_type)
    
    return {
        "evaluator_score": score,
        "content_type": content_type,
        "recommendations": [
            "Add specific examples and data points" if score < 70 else "Good structure and clarity",
            "Optimize length for voice search" if score < 80 else "Well-optimized length"
        ]
    }
