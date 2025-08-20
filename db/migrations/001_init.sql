-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS tracking;
CREATE SCHEMA IF NOT EXISTS entities;
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS deploy;
CREATE SCHEMA IF NOT EXISTS telemetry;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS score;

-- Minimal core tables
CREATE TABLE IF NOT EXISTS core.tenants (
	tenant_id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	plan TEXT NOT NULL DEFAULT 'starter',
	created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.sites (
	site_id SERIAL PRIMARY KEY,
	tenant_id INTEGER REFERENCES core.tenants(tenant_id) ON DELETE CASCADE,
	domain TEXT NOT NULL,
	cms_type TEXT,
	created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tracking essentials
CREATE TABLE IF NOT EXISTS tracking.engines (
	engine_id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	capabilities JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS tracking.prompts (
	prompt_id SERIAL PRIMARY KEY,
	site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
	cluster_id INTEGER,
	text TEXT NOT NULL,
	locale TEXT
);

CREATE TABLE IF NOT EXISTS tracking.prompt_variants (
	variant_id SERIAL PRIMARY KEY,
	prompt_id INTEGER REFERENCES tracking.prompts(prompt_id) ON DELETE CASCADE,
	text TEXT NOT NULL,
	generation_params JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS tracking.runs (
	run_id SERIAL PRIMARY KEY,
	engine_id INTEGER REFERENCES tracking.engines(engine_id) ON DELETE SET NULL,
	started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
	status TEXT NOT NULL DEFAULT 'queued',
	cost_estimate NUMERIC(12,4) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tracking.answers (
	answer_id SERIAL PRIMARY KEY,
	run_id INTEGER REFERENCES tracking.runs(run_id) ON DELETE CASCADE,
	variant_id INTEGER REFERENCES tracking.prompt_variants(variant_id) ON DELETE SET NULL,
	engine_id INTEGER REFERENCES tracking.engines(engine_id) ON DELETE SET NULL,
	raw_text TEXT,
	token_counts JSONB,
	answer_hash TEXT
);

CREATE TABLE IF NOT EXISTS tracking.citations (
	citation_id SERIAL PRIMARY KEY,
	answer_id INTEGER REFERENCES tracking.answers(answer_id) ON DELETE CASCADE,
	url TEXT,
	normalized_domain TEXT,
	entity_id INTEGER,
	position INTEGER
);

-- Content basics
CREATE TABLE IF NOT EXISTS content.blocks (
	block_id SERIAL PRIMARY KEY,
	site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
	type TEXT NOT NULL,
	json_payload JSONB NOT NULL,
	version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS content.schemas (
	schema_id SERIAL PRIMARY KEY,
	site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
	jsonld JSONB NOT NULL,
	version INTEGER NOT NULL DEFAULT 1,
	path TEXT
);

-- Telemetry minimal
CREATE TABLE IF NOT EXISTS telemetry.bot_hits (
	hit_id SERIAL PRIMARY KEY,
	site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
	user_agent TEXT,
	ip INET,
	path TEXT,
	ts TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Score minimal
CREATE TABLE IF NOT EXISTS score.scores (
	score_id SERIAL PRIMARY KEY,
	site_id INTEGER REFERENCES core.sites(site_id) ON DELETE CASCADE,
	cluster_id INTEGER,
	total NUMERIC(5,2) NOT NULL DEFAULT 0,
	subscores JSONB NOT NULL DEFAULT '{}'::jsonb,
	ts TIMESTAMPTZ NOT NULL DEFAULT now()
);

