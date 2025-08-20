-- Complete schema expansion based on technical specification

-- Enhanced core tables
CREATE TABLE IF NOT EXISTS core.users (
    user_id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES core.tenants(tenant_id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    sso_provider TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enhanced entities
CREATE TABLE IF NOT EXISTS entities.entities (
    entity_id SERIAL PRIMARY KEY,
    type TEXT NOT NULL, -- brand, competitor, organization
    name TEXT NOT NULL,
    same_as TEXT[], -- Array of SameAs URLs
    wikidata_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enhanced deployment tracking
CREATE TABLE IF NOT EXISTS deploy.jobs (
    job_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
    action TEXT NOT NULL, -- publish, rollback, schedule
    target_path TEXT,
    status TEXT NOT NULL DEFAULT 'queued',
    response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

-- Enhanced analytics
CREATE TABLE IF NOT EXISTS analytics.sessions (
    session_id TEXT PRIMARY KEY,
    site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
    ai_source TEXT, -- perplexity, gemini, bing_copilot, chatgpt
    utm_source TEXT,
    gclid TEXT,
    cid TEXT, -- GA4 client ID
    ts TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analytics.conversions (
    conv_id SERIAL PRIMARY KEY,
    session_id TEXT REFERENCES analytics.sessions(session_id) ON DELETE CASCADE,
    goal TEXT NOT NULL,
    value NUMERIC(12,2) DEFAULT 0,
    ts TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Prompt clusters for organization
CREATE TABLE IF NOT EXISTS tracking.clusters (
    cluster_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    keywords TEXT[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Add cluster_id FK to prompts table
ALTER TABLE tracking.prompts 
ADD CONSTRAINT fk_prompts_cluster 
FOREIGN KEY (cluster_id) REFERENCES tracking.clusters(cluster_id) ON DELETE SET NULL;

-- Content source documents tracking
CREATE TABLE IF NOT EXISTS content.source_docs (
    doc_id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    content_hash TEXT,
    last_crawled TIMESTAMPTZ DEFAULT now()
);

-- Add source_doc_id to blocks
ALTER TABLE content.blocks 
ADD COLUMN source_doc_id INTEGER REFERENCES content.source_docs(doc_id) ON DELETE SET NULL;

-- API keys and integrations
CREATE TABLE IF NOT EXISTS core.integrations (
    integration_id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES core.tenants(tenant_id) ON DELETE CASCADE,
    service_type TEXT NOT NULL, -- wordpress, webflow, shopify, hubspot, stripe
    credentials JSONB NOT NULL, -- encrypted API keys/tokens
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Quota tracking for billing
CREATE TABLE IF NOT EXISTS core.quotas (
    quota_id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES core.tenants(tenant_id) ON DELETE CASCADE,
    resource_type TEXT NOT NULL, -- prompts, generations, publishes
    current_usage INTEGER DEFAULT 0,
    monthly_limit INTEGER NOT NULL,
    reset_date DATE NOT NULL DEFAULT date_trunc('month', CURRENT_DATE + INTERVAL '1 month'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_answers_engine_timestamp ON tracking.answers(engine_id, answer_id DESC);
CREATE INDEX IF NOT EXISTS idx_citations_url ON tracking.citations(normalized_domain);
CREATE INDEX IF NOT EXISTS idx_sessions_ai_source ON analytics.sessions(ai_source, ts DESC);
CREATE INDEX IF NOT EXISTS idx_bot_hits_site_timestamp ON telemetry.bot_hits(site_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_scores_site_cluster ON score.scores(site_id, cluster_id, ts DESC);

-- Insert default engines
INSERT INTO tracking.engines (name, capabilities) VALUES 
('gemini', '{"search": true, "citations": true}'),
('perplexity', '{"search": true, "citations": true}'),
('bing_copilot', '{"search": true, "citations": true}'),
('chatgpt', '{"search": true, "citations": true}'),
('claude', '{"search": true, "citations": true}')
ON CONFLICT DO NOTHING;