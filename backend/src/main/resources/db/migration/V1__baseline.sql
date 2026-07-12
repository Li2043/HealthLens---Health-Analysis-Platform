-- Phase 1 baseline placeholder. User and analysis tables will be added in later phases.
CREATE TABLE IF NOT EXISTS schema_baseline (
    id BIGSERIAL PRIMARY KEY,
    note TEXT NOT NULL DEFAULT 'phase1'
);
