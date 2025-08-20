"""
Database models for OmniFunnel AI Visibility Platform
Based on technical specification schemas
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey, JSON, ARRAY
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()

# Core schema models
class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "core"}
    
    tenant_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    plan = Column(String, nullable=False, default="starter")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    sites = relationship("Site", back_populates="tenant")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "core"}
    
    user_id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("core.tenants.tenant_id", ondelete="CASCADE"))
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False, default="viewer")
    sso_provider = Column(String)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")


class Site(Base):
    __tablename__ = "sites"
    __table_args__ = {"schema": "core"}
    
    site_id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("core.tenants.tenant_id", ondelete="CASCADE"))
    domain = Column(String, nullable=False)
    cms_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="sites")
    clusters = relationship("Cluster", back_populates="site")


# Tracking schema models
class Engine(Base):
    __tablename__ = "engines"
    __table_args__ = {"schema": "tracking"}
    
    engine_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    capabilities = Column(JSONB, default={})


class Cluster(Base):
    __tablename__ = "clusters"
    __table_args__ = {"schema": "tracking"}
    
    cluster_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(Text)
    keywords = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="clusters")
    prompts = relationship("Prompt", back_populates="cluster")


class Prompt(Base):
    __tablename__ = "prompts"
    __table_args__ = {"schema": "tracking"}
    
    prompt_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    cluster_id = Column(Integer, ForeignKey("tracking.clusters.cluster_id", ondelete="SET NULL"))
    text = Column(Text, nullable=False)
    locale = Column(String)
    
    # Relationships
    cluster = relationship("Cluster", back_populates="prompts")
    variants = relationship("PromptVariant", back_populates="prompt")


class PromptVariant(Base):
    __tablename__ = "prompt_variants"
    __table_args__ = {"schema": "tracking"}
    
    variant_id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("tracking.prompts.prompt_id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    generation_params = Column(JSONB, default={})
    
    # Relationships
    prompt = relationship("Prompt", back_populates="variants")
    answers = relationship("Answer", back_populates="variant")


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = {"schema": "tracking"}
    
    run_id = Column(Integer, primary_key=True)
    engine_id = Column(Integer, ForeignKey("tracking.engines.engine_id", ondelete="SET NULL"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False, default="queued")
    cost_estimate = Column(Numeric(12, 4), default=0)
    
    # Relationships
    answers = relationship("Answer", back_populates="run")


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = {"schema": "tracking"}
    
    answer_id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("tracking.runs.run_id", ondelete="CASCADE"))
    variant_id = Column(Integer, ForeignKey("tracking.prompt_variants.variant_id", ondelete="SET NULL"))
    engine_id = Column(Integer, ForeignKey("tracking.engines.engine_id", ondelete="SET NULL"))
    raw_text = Column(Text)
    token_counts = Column(JSONB)
    answer_hash = Column(String)
    
    # Relationships
    run = relationship("Run", back_populates="answers")
    variant = relationship("PromptVariant", back_populates="answers")
    citations = relationship("Citation", back_populates="answer")


class Citation(Base):
    __tablename__ = "citations"
    __table_args__ = {"schema": "tracking"}
    
    citation_id = Column(Integer, primary_key=True)
    answer_id = Column(Integer, ForeignKey("tracking.answers.answer_id", ondelete="CASCADE"))
    url = Column(Text)
    normalized_domain = Column(String)
    entity_id = Column(Integer)
    position = Column(Integer)
    
    # Relationships
    answer = relationship("Answer", back_populates="citations")


# Entities schema models
class Entity(Base):
    __tablename__ = "entities"
    __table_args__ = {"schema": "entities"}
    
    entity_id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)  # brand, competitor, organization
    name = Column(String, nullable=False)
    same_as = Column(ARRAY(String))  # SameAs URLs
    wikidata_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Content schema models
class SourceDoc(Base):
    __tablename__ = "source_docs"
    __table_args__ = {"schema": "content"}
    
    doc_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    url = Column(String, nullable=False)
    title = Column(String)
    content_hash = Column(String)
    last_crawled = Column(DateTime(timezone=True), server_default=func.now())


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = {"schema": "content"}
    
    block_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    source_doc_id = Column(Integer, ForeignKey("content.source_docs.doc_id", ondelete="SET NULL"))
    type = Column(String, nullable=False)  # faq, table, list, para
    json_payload = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False, default=1)


class Schema(Base):
    __tablename__ = "schemas"
    __table_args__ = {"schema": "content"}
    
    schema_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    jsonld = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    path = Column(String)


# Deploy schema models
class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "deploy"}
    
    job_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    action = Column(String, nullable=False)  # publish, rollback, schedule
    target_path = Column(String)
    status = Column(String, nullable=False, default="queued")
    response = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


# Telemetry schema models
class BotHit(Base):
    __tablename__ = "bot_hits"
    __table_args__ = {"schema": "telemetry"}
    
    hit_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    user_agent = Column(String)
    ip = Column(INET)
    path = Column(String)
    ts = Column(DateTime(timezone=True), server_default=func.now())


# Analytics schema models
class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {"schema": "analytics"}
    
    session_id = Column(String, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    ai_source = Column(String)  # perplexity, gemini, bing_copilot, chatgpt
    utm_source = Column(String)
    gclid = Column(String)
    cid = Column(String)  # GA4 client ID
    ts = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversions = relationship("Conversion", back_populates="session")


class Conversion(Base):
    __tablename__ = "conversions"
    __table_args__ = {"schema": "analytics"}
    
    conv_id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey("analytics.sessions.session_id", ondelete="CASCADE"))
    goal = Column(String, nullable=False)
    value = Column(Numeric(12, 2), default=0)
    ts = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="conversions")


# Score schema models
class Score(Base):
    __tablename__ = "scores"
    __table_args__ = {"schema": "score"}
    
    score_id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("core.sites.site_id", ondelete="CASCADE"))
    cluster_id = Column(Integer)
    total = Column(Numeric(5, 2), nullable=False, default=0)
    subscores = Column(JSONB, nullable=False, default={})
    ts = Column(DateTime(timezone=True), server_default=func.now())


# Core integrations and quotas
class Integration(Base):
    __tablename__ = "integrations"
    __table_args__ = {"schema": "core"}
    
    integration_id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("core.tenants.tenant_id", ondelete="CASCADE"))
    service_type = Column(String, nullable=False)  # wordpress, webflow, shopify, hubspot, stripe
    credentials = Column(JSONB, nullable=False)  # encrypted API keys/tokens
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Quota(Base):
    __tablename__ = "quotas"
    __table_args__ = {"schema": "core"}
    
    quota_id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("core.tenants.tenant_id", ondelete="CASCADE"))
    resource_type = Column(String, nullable=False)  # prompts, generations, publishes
    current_usage = Column(Integer, default=0)
    monthly_limit = Column(Integer, nullable=False)
    reset_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())