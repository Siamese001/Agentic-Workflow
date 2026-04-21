# Environment Variable Reference

Canonical reference for every environment variable consumed by the
Agentic-Workflow runtime. The `.env` file should contain **assignments only**
— all doctrine, rationale, and routing semantics live here.

**SSOTs cited below must not be duplicated into `.env`.** Thresholds,
constants, and algorithmic behavior are code, not config.

---

## 1. File layout

| File              | Tracked in git? | Purpose                                   |
|-------------------|:--------------:|--------------------------------------------|
| `.env`            | ❌ (gitignored) | Real secrets + local overrides            |
| `.env.example`    | ✅              | Committed template with placeholders       |
| Pydantic schema   | ✅              | `apps_shared/config/environment_config.py` |
| Required-var list | ✅              | `apps_shared/utils/environment_util.py`    |

Enforcement: `.gitignore` ignores `.env*` and allowlists `.env.example`.

---

## 2. Variables by category

### 2.1 Core LLM providers (required)

| Var                 | Used by                                                 | Source                                    |
|---------------------|---------------------------------------------------------|-------------------------------------------|
| `OPENAI_API_KEY`    | OpenAI SDK clients, embeddings, function calling        | https://platform.openai.com/api-keys      |
| `ANTHROPIC_API_KEY` | Claude SDK clients, consensus jury                      | https://console.anthropic.com/            |
| `GOOGLE_API_KEY`    | Gemini REST + embeddings (SSOT — covers all Google AI)  | https://aistudio.google.com/app/apikey    |

`GOOGLE_API_KEY` is the **sole** Google-family key. `GEMINI_API_KEY` is
retired — do not reintroduce.

### 2.2 Model pinning (deployment-variable)

| Var                | Purpose                                                   |
|--------------------|-----------------------------------------------------------|
| `GEMINI_MODEL`     | High-risk-score tier (routing `S > 26`)                   |
| `GEMINI_PRO_MODEL` | Retry-exhaust / hard-override / consensus gates           |
| `OPENAI_MODEL`     | Default OpenAI chat model (fallback `gpt-4o`)             |

**Routing SSOT is NOT here.** See §4.

### 2.3 MCP / integration tokens (optional)

| Var                      | Purpose                                                   |
|--------------------------|-----------------------------------------------------------|
| `NOTION_TOKEN`           | Notion MCP bearer token (internal integration)            |
| `NOTION_MCP_DATABASE_ID` | Overrides default MCP Registry database                   |
| `GITHUB_TOKEN`           | GitHub MCP / GitKraken / PR operations (scopes: `repo`, `read:org`) |
| `FIGMA_TOKEN`            | Figma design-system integration                           |
| `FIGMA_TEAM_ID`          | Figma team scope                                          |

### 2.4 Redis

| Var                | Purpose                                                 |
|--------------------|---------------------------------------------------------|
| `REDIS_URL`        | Primary connection string (L1 working memory, L3 index) |
| `REDIS_HOST`       | Legacy — retained for components that split host/port   |
| `REDIS_PORT`       | Legacy — retained for components that split host/port   |
| `LANGCACHE_REDIS_KEY` | Optional Redis Cloud LangCache credential             |
| `LANGCACHE_ID`     | Optional Redis Cloud LangCache namespace                |

### 2.5 Embedding service

| Var                 | Purpose                                                                            |
|---------------------|------------------------------------------------------------------------------------|
| `EMBEDDING_ENABLED` | Master flag for local FAISS/GPU embedding                                          |
| `EMBEDDING_DEVICE`  | `cuda` or `cpu`. `faiss-gpu` has no CUDA 12.8 Windows wheel — CPU fallback if absent |

### 2.6 HIVE MIND — persistent store (Phase 17-21 meta-learning + D2 cache)

**Three-tier memory hierarchy:**

| Tier | Role              | Backend                                        |
|:----:|-------------------|------------------------------------------------|
| L1   | Working memory    | Redis (24h TTL via `HIVE_MIND_WORKING_MEMORY_TTL`) |
| L2   | Semantic cache    | GPTCache + ChromaDB local FAISS (`SEMANTIC_CACHE_D2_*`) |
| L3   | Long-term DNA     | ChromaDB persistent + Redis index (7d TTL via `HIVE_MIND_LONG_TERM_TTL`) |

Vector DB is **ChromaDB, local, no remote key.** Pinecone is retired.

**Variables:**

| Var                                  | Default     | Role                                                                 |
|--------------------------------------|-------------|----------------------------------------------------------------------|
| `HIVE_MIND_STRICT_MODE`              | `false`     | `true` → raise `CriticalInfrastructureError` on Redis/ChromaDB failure; `false` → graceful degradation |
| `SEMANTIC_CACHE_D2_ENABLED`          | `1`         | D2 feature flag — `1` enables L2 persistent cache; `0` disables L2 (L1+L3 still work); must be `1` in canary/prod |
| `EMBEDDING_MODEL_ID`                 | `bge-m3-v1` | Pins the embedding model ID; MUST match L2-persisted entries |
| `HIVE_MIND_EMBEDDING_MODEL_VERSION`  | `bge-m3-v1` | Same value surfaced to trace metadata — bump in lockstep with `EMBEDDING_MODEL_ID` and invalidate L2 first |
| `HIVE_MIND_RETRIEVAL_CONFIG_HASH`    | `default`   | Opaque tag embedded in cache-key material — change when retrieval semantics change |
| `HIVE_MIND_MIN_CONFIDENCE`           | `0.98`      | Similarity threshold for auto-recall (higher = stricter) |
| `HIVE_MIND_TRACE_SAMPLING_RATE`      | `1.0`       | Trace sampling; drop to `0.1` for high-volume canary |
| `HIVE_MIND_PROMOTION_THRESHOLD`      | `0.8`       | Traces with `feedback_score >= this` promote from L1 to L3 |
| `HIVE_MIND_WORKING_MEMORY_TTL`       | `86400`     | L1 TTL in seconds (24h) |
| `HIVE_MIND_LONG_TERM_TTL`            | `604800`    | L3 TTL in seconds (7d) |

**Implementation SSOT:** `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`
**Rollout guide:** `docs/runbooks/d2_semantic_cache_production_rollout.md`

### 2.7 Application

| Var                | Purpose                                                 |
|--------------------|---------------------------------------------------------|
| `LOG_LEVEL`        | `DEBUG` / `INFO` / `WARNING` / `ERROR`                  |
| `DEBUG`            | `true` / `false`                                        |
| `PYTHONUNBUFFERED` | Set `1` so stdout/stderr are unbuffered                 |
| `PYTHONUTF8`       | Set `1` to force UTF-8 on Windows                       |

---

## 3. Retired / deprecated — **do NOT reintroduce**

| Retired var                  | Rationale                                                             |
|------------------------------|-----------------------------------------------------------------------|
| `GEMINI_API_KEY`             | Consolidated into `GOOGLE_API_KEY`                                    |
| `BRAVE_API_KEY` / `BRAVE_SEARCH_API_KEY` | No live consumer. `enhanced_http` MCP is the HTTP authority |
| `PINECONE_API_KEY`           | ChromaDB is the production vector DB (local, no remote key)           |
| `DATABASE_URL`               | Legacy PostgreSQL MCP stub; `adg_sqlite` MCP is the live authority    |
| `MISTRALAI_API_KEY` / `COHERE_API_KEY` / `GROQ_API_KEY` / `TOGETHER_API_KEY` / `FIREWORKS_API_KEY` | No live consumer; reintroduce only when a provider is wired into code |
| `SOVEREIGN_HIGH_CONFIDENCE` / `SOVEREIGN_MEDIUM_CONFIDENCE` | Governance invariants, not config — moved to code SSOT (see §4) |
| `SIGNAL_EXCELLENT_MIN` / `SIGNAL_HIGH_MIN` / `SIGNAL_MEDIUM_MIN` / `SIGNAL_LOW_MIN` | Orphan fields with no live consumer |

---

## 4. Routing & sovereignty thresholds — **code SSOT**

Routing thresholds and tier decisions **must not be in `.env`**. They are
governance invariants and live in code.

**Canonical SSOT:** `agentic_core/L0_routing/config/path_constants.py`

```python
HEALING_CONFIDENCE_X: float = 0.80  # conf > X  → DETERMINISTIC (agent mutates, no LLM)
HEALING_CONFIDENCE_Y: float = 0.50  # conf <= Y → GEMINI 2.5 Pro recovery

SSOT_SCORE_THRESHOLD_DET:  int = 13   # S <= 13 → DETERMINISTIC
SSOT_SCORE_THRESHOLD_QWEN: int = 26   # 13 < S <= 26 → QWEN (WSL vLLM Qwen2.5-14B-Instruct-AWQ)
                                      # S > 26 → GEMINI (flash by default)
```

**Routing algorithm:** `ops_scripts/dev_tools/L0_routing_scripts/_ssot_routing.py`

**Tier behavior:**

| Tier             | Trigger                                     | Executor                                                         |
|------------------|---------------------------------------------|------------------------------------------------------------------|
| DETERMINISTIC    | `S ≤ 13` or `conf > 0.80`                   | Agent performs mutation directly — no LLM call                   |
| QWEN             | `13 < S ≤ 26` and Qwen not prohibited       | `Qwen2.5-14B-Instruct-AWQ` via WSL vLLM subprocess (`L2_execution/healers/qwen_vllm_inference.py`) |
| GEMINI (flash)   | `S > 26`                                    | `GEMINI_MODEL` (default `gemini-3-flash-preview`) via Gemini REST |
| GEMINI Pro       | Retry-exhaust / hard-override / consensus   | `GEMINI_PRO_MODEL` (default `gemini-2.5-pro`)                    |
| FAIL_CLOSED      | Both Qwen and Gemini prohibited             | Escalate to human                                                |

The only LLM-related knobs legitimately in `.env` are `GEMINI_MODEL` and
`GEMINI_PRO_MODEL` — those are deployment-variable (model version upgrades,
regional availability, A/B testing).

---

## 5. Quick start

Native Python + MCP workspace (no docker-compose).

```bash
# 1. Copy the template and fill in your secrets
cp .env.example .env            # POSIX
copy .env.example .env          # Windows

# 2. venv + deps
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # POSIX
pip install -r requirements.txt

# 3. Start Redis (hot cache for ADG + L1/L3 memory)
redis-server                    # or: wsl redis-server

# 4. Regenerate ADG snapshot + ingest Redis hot cache
python tools/generate_full_adg.py
python tools/adg/adg_redis_ingest.py --force

# 5. Verify health before T2/T3 work
python tools/adg/adg_redis_ingest.py --check
```

MCP servers are auto-launched by Windsurf per `.windsurf/mcp_config.json`.
No ports to expose; stdio transport only.

---

## 6. Key rotation

When rotating a secret: update `.env`, restart any long-running process that
read it (MCP servers, background workers), and revoke the old credential at
the provider. Git history has been purged of prior `.env` commits — see
`docs/runbooks/` for the rotation runbook if/when one is added.
