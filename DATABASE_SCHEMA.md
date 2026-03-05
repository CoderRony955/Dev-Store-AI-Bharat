# Dev-Store Database Schema

Complete schema for all tables in the Dev-Store AI/ML Resource Discovery Platform.

---

## TABLE 1: `resources` ✅ (Exists — needs 6 new columns)

```sql
CREATE TABLE resources (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    category        VARCHAR(50) NOT NULL,       -- 'api' | 'model' | 'dataset' | 'solution'
    source_url      VARCHAR(500),
    license         VARCHAR(100),
    price_type      VARCHAR(20) DEFAULT 'free', -- 'free' | 'paid'
    stars           INTEGER DEFAULT 0,
    downloads       INTEGER DEFAULT 0,
    activity_score  FLOAT DEFAULT 0.0,

    -- New columns to add
    author          VARCHAR(255),
    tags            TEXT,                       -- JSON array string: ["nlp","vision"]
    version         VARCHAR(50),
    thumbnail_url   VARCHAR(500),
    readme_url      VARCHAR(500),
    rank_score      FLOAT DEFAULT 0.0,          -- cached ranking score

    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME
);
```

---

## TABLE 2: `categories`

```sql
CREATE TABLE categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slug            VARCHAR(100) UNIQUE NOT NULL, -- 'api' | 'model' | 'dataset' | 'solution'
    label           VARCHAR(100) NOT NULL,         -- 'APIs' | 'Models' | 'Datasets'
    description     TEXT,
    resource_count  INTEGER DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## TABLE 3: `tags`

```sql
CREATE TABLE tags (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) UNIQUE NOT NULL, -- 'nlp', 'vision', 'audio'
    slug            VARCHAR(100) UNIQUE NOT NULL,
    usage_count     INTEGER DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## TABLE 4: `resource_tags` (Many-to-Many)

```sql
CREATE TABLE resource_tags (
    resource_id     INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    tag_id          INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (resource_id, tag_id)
);
```

---

## TABLE 5: `embeddings`

```sql
CREATE TABLE embeddings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id     INTEGER UNIQUE NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    vector          TEXT NOT NULL,              -- JSON float array (placeholder for OpenSearch)
    model_used      VARCHAR(100) DEFAULT 'placeholder', -- 'text-embedding-ada-002' etc.
    dimensions      INTEGER DEFAULT 384,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME
);
```

---

## TABLE 6: `bundles`

```sql
CREATE TABLE bundles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    use_case        VARCHAR(255),               -- 'Image Classification', 'Sentiment Analysis'
    graph_json      TEXT,                       -- Full React Flow nodes+edges JSON (used by /blueprint/[bundleId])
    is_featured     BOOLEAN DEFAULT FALSE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## TABLE 7: `bundle_resources` (Many-to-Many)

```sql
CREATE TABLE bundle_resources (
    bundle_id       INTEGER NOT NULL REFERENCES bundles(id) ON DELETE CASCADE,
    resource_id     INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    role            VARCHAR(50),               -- 'api' | 'model' | 'dataset'
    order_index     INTEGER DEFAULT 0,         -- order in blueprint graph
    PRIMARY KEY (bundle_id, resource_id)
);
```

---

## TABLE 8: `boilerplate_requests`

```sql
CREATE TABLE boilerplate_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id     INTEGER REFERENCES resources(id) ON DELETE SET NULL,
    bundle_id       INTEGER REFERENCES bundles(id) ON DELETE SET NULL,
    language        VARCHAR(50) DEFAULT 'python', -- 'python' | 'node' | 'go'
    framework       VARCHAR(50),                  -- 'fastapi' | 'express' | 'flask'
    generated_code  TEXT,                         -- cached JSON output
    ip_hash         VARCHAR(64),                  -- anonymized requester
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## TABLE 9: `search_logs`

```sql
CREATE TABLE search_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    query           VARCHAR(500) NOT NULL,
    category        VARCHAR(50),
    price_type      VARCHAR(20),
    results_count   INTEGER DEFAULT 0,
    clicked_id      INTEGER REFERENCES resources(id) ON DELETE SET NULL,
    session_id      VARCHAR(100),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## TABLE 10: `ingestion_logs`

```sql
CREATE TABLE ingestion_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          VARCHAR(100) NOT NULL,         -- 'github' | 'huggingface' | 'manual'
    status          VARCHAR(50) DEFAULT 'pending', -- 'pending' | 'running' | 'done' | 'failed'
    records_fetched  INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_skipped  INTEGER DEFAULT 0,
    error_message   TEXT,
    started_at      DATETIME,
    finished_at     DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## TABLE 11: `rankings_cache`

```sql
CREATE TABLE rankings_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key       VARCHAR(255) UNIQUE NOT NULL, -- 'ranked_api_free', 'ranked_model_paid'
    data_json       TEXT NOT NULL,                -- cached ranked JSON response
    expires_at      DATETIME NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Entity Relationship Overview

```
resources ──────────── resource_tags ──── tags
    │
    ├───────────────── embeddings
    │
    ├───────────────── bundle_resources ── bundles
    │
    ├───────────────── boilerplate_requests
    │
    └───────────────── search_logs (clicked_id)

ingestion_logs  (standalone)
rankings_cache  (standalone)
categories      (standalone)
```

---

## Implementation Priority

| Priority | Table               | Phase   | Reason                                  |
|----------|---------------------|---------|-----------------------------------------|
| 1        | `resources`         | Now     | Already exists — add 6 new columns      |
| 2        | `tags` + `resource_tags` | Phase 4 | Used by search and filter          |
| 3        | `bundles` + `bundle_resources` | Phase 4 | Blueprint page needs it      |
| 4        | `embeddings`        | Phase 5 | RAG / semantic search                   |
| 5        | `boilerplate_requests` | Phase 6 | Boilerplate generator               |
| 6        | `ingestion_logs`    | Phase 4 | Ingestion pipeline tracking             |
| 7        | `search_logs`       | Phase 7 | Analytics and usage tracking            |
| 8        | `rankings_cache`    | Phase 3 | Performance — cache ranked results      |
| 9        | `categories`        | Any     | Nice to have — dynamic category config  |
