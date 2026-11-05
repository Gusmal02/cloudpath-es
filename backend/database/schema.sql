CREATE TABLE IF NOT EXISTS exam_sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    mode TEXT NOT NULL,
    provider TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    total INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_answers (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    chosen_index INTEGER NOT NULL,
    is_correct INTEGER NOT NULL,
    answered_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES exam_sessions(id),
    UNIQUE (session_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_user_answers_session ON user_answers (session_id);

CREATE TABLE IF NOT EXISTS domain_progress (
    domain TEXT NOT NULL,
    provider TEXT NOT NULL,
    correct_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    last_updated TEXT NOT NULL,
    PRIMARY KEY (domain, provider)
);

CREATE TABLE IF NOT EXISTS session_questions (
    session_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    correct_indices TEXT NOT NULL,
    domain TEXT NOT NULL,
    provider TEXT NOT NULL,
    PRIMARY KEY (session_id, question_id),
    FOREIGN KEY (session_id) REFERENCES exam_sessions(id)
);

CREATE TABLE IF NOT EXISTS architectures (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    nodes_json TEXT NOT NULL DEFAULT '[]',
    edges_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
