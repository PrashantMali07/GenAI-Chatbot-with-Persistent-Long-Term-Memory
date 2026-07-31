CREATE EXTENSION IF NOT EXISTS vector;

-- Raw long-term memory (plain text, no embeddings)
CREATE TABLE long_term_memory_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_ltm_raw_thread_id ON long_term_memory_raw (thread_id);

-- Vector long-term memory — OpenAI embeddings (text-embedding-3-small = 1536 dims)
CREATE TABLE long_term_memory_vector (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE thread_summary_state (
    thread_id TEXT PRIMARY KEY,
    last_summarized_message_count INTEGER NOT NULL DEFAULT 0,
    last_summary TEXT,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_ltm_vec_thread_id ON long_term_memory_vector (thread_id);
CREATE INDEX idx_ltm_vec_embedding ON long_term_memory_vector
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);