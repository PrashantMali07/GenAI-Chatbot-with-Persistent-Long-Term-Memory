CREATE EXTENSION IF NOT EXISTS vector;

-- Raw long-term memory (plain text, no embeddings)
-- Scoped by user_id so memory persists across all threads for a given user.
CREATE TABLE long_term_memory_raw (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    TEXT NOT NULL,
    thread_id  TEXT NOT NULL,
    summary    TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_ltm_raw_user_id ON long_term_memory_raw (user_id);
CREATE INDEX idx_ltm_raw_thread_id ON long_term_memory_raw (thread_id);

-- Vector long-term memory — OpenAI embeddings (text-embedding-3-small = 1536 dims)
-- Scoped by user_id for cross-session semantic recall.
CREATE TABLE long_term_memory_vector (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    TEXT NOT NULL,
    thread_id  TEXT NOT NULL,
    summary    TEXT NOT NULL,
    embedding  VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_ltm_vec_user_id ON long_term_memory_vector (user_id);
CREATE INDEX idx_ltm_vec_thread_id ON long_term_memory_vector (thread_id);
CREATE INDEX idx_ltm_vec_embedding ON long_term_memory_vector
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Tracks incremental summarization progress per (user, thread) pair.
-- Compound primary key allows the same thread_id to be reused across users safely.
CREATE TABLE thread_summary_state (
    user_id                        TEXT NOT NULL,
    thread_id                      TEXT NOT NULL,
    last_summarized_message_count  INTEGER NOT NULL DEFAULT 0,
    last_summary                   TEXT,
    updated_at                     TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, thread_id)
);