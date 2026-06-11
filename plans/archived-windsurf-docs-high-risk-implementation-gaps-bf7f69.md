---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\high-risk-implementation-gaps-bf7f69.md'
original_relative_path: 'high-risk-implementation-gaps-bf7f69.md'
source_sha256: 474f9a50f6e039780a27759cb6f8fae003d99edad4a3324d89a0d0fafa0acea7
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# High-Risk Implementation Gaps — Cross-Cutting Hardening

Addresses the highest-risk cross-cutting gaps found in the AST scan that do not fit neatly into the five domain plans but have systemic blast radius.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State (AST Scan Findings)

This plan covers risks that span multiple subsystems. Each gap was discovered during the deep AST scan and poses production-level risk.

---

## Gap Catalogue

### G1 — Ghost Import Swallower in `rag_orchestrator.py` (CRITICAL)

**File:** `agentic_core/knowledge/engine/rag_orchestrator.py` lines 22–45

```python
try:
    from agentic_core.semantic_memory.embeddings.core_embedder import ...
except ImportError:
    ACTION_VERBS, STRONG_VERBS = {}, []
    TextDocumentLoader = None
    ...
```

The entire RAG orchestrator silently degrades to empty taxonomies and null loaders if `agentic_core.semantic_memory` doesn't exist. The swallowing `ImportError` makes this invisible at startup. At runtime, `ingest()` silently returns nothing; `retrieve()` returns the fallback `"No relevant knowledge found."` sentinel.

**Fix:** Remove `try/except ImportError` and replace with canonical imports. Fail loudly. See Agentic RAG plan Phase 1.

---

### G2 — `asyncio.create_task` in Sync `__init__` (RUNTIME CRASH)

**File:** `agentic_core/L2_execution/config/hybrid_retriever_config.py` line 172

```python
self._init_task = asyncio.create_task(self._load_or_rebuild_local_index())
```

This will raise `RuntimeError: no current event loop` in any synchronous construction context (tests, module-level instantiation, non-async main). There is no event loop guard.

**Fix:** See Hybrid RAG plan Phase 2-A. Replace with lazy async init triggered on first `hybrid_search()` call.

---

### G3 — `query_planner.py` NameError on Construction (RUNTIME CRASH)

**File:** `agentic_core/L1_cognition/engines/query_planner.py` lines 21–22

```python
def __init__(self, engine: SubAtomicEngine | None = None, cache: semantic_cache | None = None):
    self.engine = engine or SubAtomicEngine(gemini_client=None)
    self.cache = cache or semantic_cache()
```

`SubAtomicEngine` and `semantic_cache` are referenced without any import statement in the file. This is a `NameError` on the first construction. The planner cannot be instantiated.

**Fix:** Add correct imports. See Agentic RAG plan Phase 1-B.

---

### G4 — `MetaLearningChangePackage` Constructor Mismatch (BREAKING BUG)

**File:** `system_learning/ports/meta_outcome_bus_hook.py` lines 89–101

```python
package = MetaLearningChangePackage(
    change_type="healing_outcome",   # field does not exist
    payload={...},
    proposal_only=True,              # field does not exist
)
```

Actual `MetaLearningChangePackage` in `meta_learning_bus.py` is a frozen dataclass with fields `(trace_id, kind, payload, package_hash)`. This raises `TypeError` on every healing outcome publication. The bus has never successfully received a package.

**Fix:** See System Learning plan Phase 1. Single-file fix; highest-priority bug in the codebase.

---

### G5 — `get_context_for_task` Sync-Calls `async def retrieve` (SILENT FAILURE)

**File:** `agentic_core/knowledge/engine/rag_orchestrator.py` line 308

```python
retrievals = self.retrieve(Task, domain=domain)  # async def called without await
```

Returns a coroutine object. `context_parts` loop iterates over the coroutine, producing nothing. Callers receive the header string only: `"### RELEVANT SOVEREIGN KNOWLEDGE"`.

**Fix:** See Agentic RAG plan Phase 1-C. Convert to `async` or add `asyncio.get_event_loop().run_until_complete(...)` wrapper.

---

### G6 — Healing Confidence Threshold Defined in Two Places (INVARIANT BREACH)

| File | X | Y |
|------|---|---|
| `healing_tier_config.py` | 0.80 | 0.50 |
| `qwen_meta_learning.py` | 0.75 | 0.40 |

Both files define `HEALING_CONFIDENCE_X` and `HEALING_CONFIDENCE_Y`. The router uses `healing_tier_config.py`. The meta-learning protection asserts `qwen_meta_learning.py` values. These will diverge under future maintenance.

**Fix:** See Qwen/Gemini plan Phase 1-B. Remove definitions from `qwen_meta_learning.py`; import from `healing_tier_config.py`.

---

### G7 — Three Separate BM25 Implementations (MAINTENANCE RISK)

| File | Engine | Tokenizer |
|------|--------|-----------|
| `bm25_store.py` | `rank_bm25.BM25Okapi` | `str.split()` |
| `hybrid_retriever_config.py` | `rank_bm25.BM25Okapi` | `ASTAwareTokenizer` |
| `hybrid_scorer_types.py` | Bespoke (no `rank_bm25`) | `re.findall` |

Any bug fix must be applied to all three. Any performance improvement is invisible to two of three paths.

**Fix:** See Hybrid RAG plan Phase 1. Consolidate to `Bm25Store` + `ASTAwareTokenizer`.

---

### G8 — Silent Swallowers Without Guardian Comments

**Pattern found in multiple files:**
- `agentic_core/knowledge/engine/rag_orchestrator.py` lines 115–119: bare `except (ImportError, Exception)` with no guardian comment.
- `hybrid_retriever_config.py` lines 191–192: `# guardian: allow-silent-swallow` present but swallows index corruption silently.
- `drift_monitor.py` line 176: bare `except Exception: pass` — drift persistence failure disappears.

**Fix plan:**
1. All `except Exception: pass` blocks must have `# guardian: allow-silent-swallow` with a logged message.
2. `drift_monitor._persist()` must at minimum log the exception before swallowing.
3. `rag_orchestrator.py` initialization failure must emit `logger.critical(...)` before falling back.

**Acceptance criteria:**
- Architecture test: AST scan of all `except` blocks; assert no bare `pass` without guardian comment.

---

### G9 — `DriftAlert.alert_id` is `uuid.uuid4()` (Non-Deterministic in Tests)

**File:** `agentic_core/utils/workflow_engines/drift_monitor.py` — all `check_alerts()` methods

Every `DriftAlert` gets a random UUID. Snapshot-based regression tests cannot assert alert IDs. Duplicate alerts cannot be deduplicated deterministically.

**Fix:** Add optional `id_factory: Callable[[], str] = uuid.uuid4` parameter to `check_alerts()`. Tests inject `lambda: "test-alert-001"`.

---

### G10 — `healing_provider_adapters.py` Discards Model Response (DATA LOSS)

**File:** `agentic_core/L2_execution/healers/healing_provider_adapters.py`

`invoke_qwen_vllm` calls `client.chat.completions.create(...)` without capturing the return value. Same for `invoke_gemini`. `InvocationRecord` never contains the model's actual output. Downstream systems (meta-learning bus, audit trail, response parsing) operate on `None`.

**Fix:** See Qwen/Gemini plan Phase 1-A. Single-line captures: `completion = client.chat.completions.create(...)`.

---

## Prioritised Fix Matrix

| Gap | Severity | Effort | Plan Reference |
|-----|----------|--------|---------------|
| G4 — MetaLearningChangePackage mismatch | CRITICAL (breaking) | 1 file, 15 lines | System Learning P1 |
| G3 — query_planner NameError | CRITICAL (crash) | 1 file, 3 lines | Agentic RAG P1-B |
| G2 — asyncio.create_task in sync init | HIGH (crash) | 1 file, 10 lines | Hybrid RAG P2-A |
| G5 — async called without await | HIGH (silent failure) | 1 file, 3 lines | Agentic RAG P1-C |
| G10 — response discarded in adapters | HIGH (data loss) | 2 files, 5 lines | Qwen/Gemini P1-A |
| G1 — ghost import swallower | HIGH (silent degradation) | 1 file, 15 lines | Agentic RAG P1-A |
| G6 — threshold drift | MEDIUM (invariant) | 2 files, 5 lines | Qwen/Gemini P1-B |
| G8 — silent swallowers | MEDIUM (observability) | 5 files, audit | All plans |
| G7 — BM25 fragmentation | MEDIUM (maintenance) | 3 files | Hybrid RAG P1 |
| G9 — non-deterministic alert ID | LOW (test brittleness) | 1 file, 3 lines | Eval/Drift P1-A |

---

## Cross-Cutting Invariant Test

Create `tests/architecture/test_cross_cutting_invariants.py`:

1. **Single threshold source**: `ast.parse` all `.py` files; assert `HEALING_CONFIDENCE_X` defined only in `healing_tier_config.py`.
2. **No bare `except: pass`**: AST walk all except handlers; assert none have `pass` as sole body without guardian comment.
3. **No ghost import swallowing**: assert no `except ImportError: ... = None` pattern without `logger.critical`.
4. **MetaLearningChangePackage constructor**: assert `DefaultMetaOutcomeBusHook` uses `.create()` factory, not direct construction.
5. **Response capture**: assert `invoke_qwen_vllm` and `invoke_gemini` in adapters assign the API return value to a variable.

All five invariants are AST-based (no regex).

**Evidence file:** `docs/reports/sub/phase_cross_cutting_gaps_evidence.md`

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

