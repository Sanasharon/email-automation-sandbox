-- migrations/008_add_analytics_cache.sql
CREATE TABLE IF NOT EXISTS analytics_cache (
  id serial PRIMARY KEY,
  key text NOT NULL UNIQUE,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_analytics_cache_key ON analytics_cache (key);