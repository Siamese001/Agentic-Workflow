---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\bge-review-apps-qna-cache-init-9a4c2e.md'
original_relative_path: 'bge-review-apps-qna-cache-init-9a4c2e.md'
source_sha256: c155fb2154ac7f2ae8164aca6b49b995f60d61418183d157a10d4f37737984c1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
description: BGE review successor plan for apps_qna L4 semantic-cache Chroma initialization
tags: [bge-review, apps_qna, chromadb, l4-cache, parent-plan]
status: In Progress
created: 2026-06-08
branch: codex/BGE-review
supersedes:
  - apps-qna-l4-chromadb-init-p0-a7e4c3
blocks:
  - bge-review-apps-qna-c0-chroma-migration-f9a3b2
---

# BGE Review: apps_qna L4 Cache Initialization

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: NONE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-08

## Context

Situation: `apps_qna` still has embedding and retrieval cleanup work, but its old P0 Chroma initialization plan is retired in Notion and points at a legacy Cursor archive path.

Complication: The dependent `apps_qna` C0 Chroma migration must not run until the parent L4 cache substrate is initialized and verified in the active BGE review branch.

Question: What parent work must complete before the `apps_qna_interview_cards` flat index can migrate off `C:/AgenticEmbeddings`?

Answer: Complete the L4 cache parent waves first: directory/client initialization, BGE-M3 collection setup, then cache integration verification.

## Supersedes

| Plan | Status | Reason |
|---|---|---|
| `apps-qna-l4-chromadb-init-p0-a7e4c3` | Retired | Legacy pre-rebaseline plan; this active BGE review plan carries the parent dependency forward on `codex/BGE-review`. |

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | P1.1-P1.3 | Directory setup and Chroma client init | 4k | BGE review branch stays isolated | DONE | Layout dirs exist; Chroma PersistentClient starts; tests pass |
| W2 | P2.1-P2.3 | BGE-M3 `l2_semantic_cache` collection setup | 5k | W1 complete | DONE | Collection metadata/dimension verified |
| W3 | P3.1-P3.3 | apps_qna cache integration and smoke verification | 4k | W2 complete | DONE | Cache hit/miss path verified |

### Phase Progress

| Phase | Title | Status | Notes |
|---|---|---|---|
| P1.1 | Create canonical directories | DONE | `VECTOR_CACHE_LAYOUT.ensure_directories()` exercised |
| P1.2 | Initialize ChromaDB client | DONE | `PersistentClient(path='artifacts/cache/l2/chroma')` starts |
| P1.3 | Verify path override behavior | DONE | `CHROMA_PERSIST_DIR` test added |
| P2.1 | Create semantic cache collection | DONE | `l2_semantic_cache` creation uses a reusable BGE-M3 collection contract |
| P2.2 | Configure BGE-M3 embedding function | DONE | `SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-m3")` verified |
| P2.3 | Align similarity threshold | DONE | Collection metadata records `similarity_threshold=0.95` |
| P3.1 | Wire apps_qna L4 usage proof | DONE | `apps_qna.cache.r1b_semantic` probes L4 through `SemanticCacheManager.recall` |
| P3.2 | Functional cache test | DONE | R1B L4 hit/miss/unavailable paths verified as advisory-only |
| P3.3 | Smoke test | DONE | Restored synthetic-mini fixture; apps_qna smoke path passes |

## Wave Details

### W1: Directory Setup and Chroma Init

Scope:
- `agentic_core/L4_state/cache/gptcache_client.py`
- `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`
- `tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py`

Completed behavior:
- L2 cache initialization creates canonical layout directories before opening SQLite or Chroma.
- Chroma path can be isolated with `CHROMA_PERSIST_DIR` for tests and migrations.
- L2 cache init treats `ImportError` as recoverable.
- Missing Chroma collection probes tolerate not-found exceptions and still create the collection.

Verification:
- `python -m pytest -p pytest_timeout tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py -q`
- `python -m pytest -p pytest_timeout tests/unit/L4_state/cache/test_vector_cache_layout.py tests/unit/agentic_core/L4_state/config/test_chroma_paths.py -q`
- `python -c "from agentic_core.L4_state.utils.client.chroma_client import chromadb_module as chromadb; c=chromadb.PersistentClient(path='artifacts/cache/l2/chroma'); print([col.name for col in c.list_collections()])"`

### W2: BGE-M3 Collection Setup

Scope:
- Confirm `l2_semantic_cache` collection metadata and compatibility guard.
- Add focused tests for collection creation and dimension handling if missing.
- Do not migrate `apps_qna_interview_cards` yet.

Completed behavior:
- `l2_semantic_cache` is created through one reusable collection contract.
- Collection metadata records cosine space, `BAAI/bge-m3`, 1024 dimensions, and the active `0.95` threshold.
- Metadata-declared incompatible dimensions trigger the same delete/recreate guard as sampled embeddings.
- `clear()` recreates the collection through the BGE-M3 contract path instead of a bare Chroma collection.

Verification:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py -q -k "bgem3_collection or migration_guard or clear_recreates"`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py -q`

### W3: Cache Integration Verification

Scope:
- Prove app-facing cache paths can use the initialized L4 substrate.
- Run focused apps_qna smoke or cache integration tests.

Completed behavior:
- `SemanticCacheManager` no longer forces the legacy `artifacts/gptcache` directory when constructing `GPTCacheClient`, allowing the native client to use the W1/W2 canonical layout.
- `apps_qna.cache.r1b_semantic.r1b_lookup` performs a read-only L4 semantic-cache probe through `SemanticCacheManager.recall`.
- R1B remains advisory-only: cache hits populate `suggestion`, never `result`, so no silent terminal return is introduced.
- The missing synthetic-mini smoke fixture was restored and shaped to the current strict templates.
- Existing `apps_qna.c0_adapter` flat-index tests still pass; no child C0 migration was performed in the parent plan.

Verification:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_qna/test_r1b_semantic_l4.py tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py::test_semantic_cache_manager_initializes_gptcache -q`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/apps_qna/test_acceptance.py::TestCache -q`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/agentic_core/L4_state/cache/test_gptcache_wired.py -q`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/apps_qna/test_smoke_minimal.py -q`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_timeout tests/unit/apps_qna/test_c0_adapter_real_fetch.py -q`

## Dependencies

| Dependency | Status | Notes |
|---|---|---|
| BGE review branch | Ready | `codex/BGE-review` |
| Notion Plans registration | Registered | https://app.notion.com/p/37927693f55c81c5a735e36189849fa2 |
| Child C0 migration plan | Unblocked | Parent W1-W3 complete; child may start at W0 |

## Definition Of Done

- [x] W1 directories and Chroma client init verified.
- [x] W2 `l2_semantic_cache` collection creation verified.
- [x] W2 BGE-M3 1024-dim compatibility verified.
- [x] W3 cache hit/miss path verified.
- [x] Child migration plan unblocked only after W3 completion.

PLAN_CREATED: slug=bge-review-apps-qna-cache-init-9a4c2e path=.claude/plans/bge-review-apps-qna-cache-init-9a4c2e.md status=In Progress
