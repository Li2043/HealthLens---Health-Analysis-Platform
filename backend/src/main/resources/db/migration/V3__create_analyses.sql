CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    input_text TEXT NOT NULL,
    language VARCHAR(2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    triage_tier VARCHAR(20) NOT NULL,
    result_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analyses_user_id_created_at ON analyses (user_id, created_at DESC);
