# Wave B Validation Report — Infrastructure Wiring Phase 5

**Executed:** 2026-04-11
**Status: WAVE B PARTIALLY COMPLETE — R-B1 ✅ R-B2 ✅ R-B3 🔴 BLOCKED**

---

## Files Changed

| File | Change |
|---|---|
| `agentic_core/evaluation/judges/llm_judge.py` | R-B1: `GeminiJudge._get_client()` rerouted |
| `agentic_core/evaluation/judges/provider_registry.py` | R-B2: `GeminiJudgeProvider._get_client()` + `create_default_registry()` rerouted |

**`agentic_core/knowledge/enrichment/semantic_enricher.py` — NOT CHANGED (R-B3 blocked)**

---

## Exact Functions Changed

### R-B1 — `llm_judge.py`: `GeminiJudge._get_client()`

**Before:**
```python
try:
    import google.generativeai as genai
except ImportError as exc:
    raise RuntimeError(...) from exc
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError(...)
if not self._configured:
    genai.configure(api_key=api_key)
    self._configured = True
return genai.GenerativeModel(self._model)
```

**After:**
```python
from infrastructure.sdks_mcps import create_vertex_client
try:
    genai = create_vertex_client()
except (ImportError, ValueError) as exc:
    raise RuntimeError("GeminiJudge: google-genai package not installed or GOOGLE_API_KEY missing.") from exc
self._configured = True
return genai.GenerativeModel(self._model)
```

Injected-client fast-path (`if self._client is not None: return self._client`) **preserved and validated**.

### R-B2 — `provider_registry.py`: `GeminiJudgeProvider._get_client()`

Same reroute pattern as R-B1 applied to `GeminiJudgeProvider._get_client()`.

### R-B2 — `provider_registry.py`: `create_default_registry()`

**Before:** `GeminiJudgeProvider()` instantiated with no args → self-provisions via raw import.

**After:** Pre-builds sanctioned model via `create_vertex_client()` and injects:
```python
from infrastructure.sdks_mcps import create_vertex_client
genai = create_vertex_client()
default_model = os.getenv("GEMINI_MODEL", GeminiJudgeProvider.DEFAULT_MODEL)
gemini_model = genai.GenerativeModel(default_model)
gemini = GeminiJudgeProvider(gemini_client=gemini_model)
```

---

## R-B3 Gate: BLOCKED

**Reason:** Interface incompatibility between `SemanticEnricher` call site and `create_openai_client()` return type.

| Factor | Detail |
|---|---|
| `create_openai_client()` return type | `openai.AsyncOpenAI` (line 60 of `infrastructure/sdks_mcps/__init__.py`) |
| `SemanticEnricher._llm_enrich()` call | `self.llm_client.chat.completions.create(...)` — **synchronous, no `await`** (line 283) |
| Incompatibility | `AsyncOpenAI.chat.completions.create()` returns a coroutine; calling without `await` yields a coroutine object instead of a response — silent data corruption in production |

**No patch applied.** Patching would silently break real enrichment runs.

**Resolution options (for Wave C HITL packet):**
1. Add `create_openai_sync_client()` to `infrastructure/sdks_mcps/__init__.py` returning `openai.OpenAI` (sync) — minimal seam extension, no architecture change
2. Make `_init_default_client()` and `_llm_enrich()` async — broader change, requires callers to await
3. Accept current state as Wave C deferred item — `semantic_enricher.py` is in `system_learning/` adjacency, low blast radius

---

## Focused Validation Results

| Check | Result |
|---|---|
| `llm_judge.py`: `import google.generativeai` absent | ✅ CLEAN |
| `provider_registry.py`: `import google.generativeai` absent | ✅ CLEAN |
| `llm_judge.py`: `create_vertex_client` present (lines 263, 266) | ✅ FOUND |
| `provider_registry.py`: `create_vertex_client` present (lines 91, 94, 242, 244) | ✅ FOUND |
| `semantic_enricher.py`: `from openai import OpenAI` still present (line 136) | ✅ Expected — R-B3 not applied |
| `GeminiJudge` injected-client fast-path | ✅ OK |
| `GeminiJudgeProvider` injected-client fast-path | ✅ OK |
| `create_default_registry()` with no API key → `null` provider default | ✅ OK |
| Module imports without errors | ✅ OK |

---

## Remaining Blocker List After Wave B

| ID | File | Blocker | Wave |
|---|---|---|---|
| R-C1 | `agentic_core/L5_safety/validators/dependencygraph_validator.py` | Guardian exemption type + L5 direct Google import — HITL required | C |
| R-B3 | `agentic_core/knowledge/enrichment/semantic_enricher.py` | `create_openai_client()` returns `AsyncOpenAI`; enricher is sync — interface gate failed | C |
| R-C2 | `agentic_core/L3_orchestration/…/optimized_vllm_client.py` | aiohttp approve-or-migrate architecture decision — HITL required | C |
| R-C3 | `agentic_core/cache/core/redis_cache_client.py` | File-on-disk deletion gate — investigation required before deletion | C |
| R-C4 | `agentic_core/L4_state/enforcement/neo4j_store.py` | Deprecate vs. formalize decision — HITL required | C |

File-scan ratchet `apps_* direct infra access` still shows `current=3` (the 3 google-import lines in `llm_judge.py`, `provider_registry.py`, `dependencygraph_validator.py`). The scanner detects lazy imports by line content (`import google`). **After Wave B the two evaluation files no longer contain any top-level or lazy `import google` — the scanner's `current=3` will drop to 1 (only `dependencygraph_validator.py`) on next scan run.** The scorecard was not re-run as part of Wave B per scope constraints; run `python ops_scripts/ci/infra_wiring_scan.py` to refresh.

---

## Next Prompt Target

**Wave C HITL packet** covering:

1. **R-C1** (`dependencygraph_validator.py`): HITL for guardian exemption type — is `genai` import in L5 Safety a true provider bypass or a dead dead-import (the `genai` variable is only referenced in string literals)?
2. **R-B3 unblock** (`semantic_enricher.py`): HITL or decision on sync vs. async — add `create_openai_sync_client()` to seam, or migrate enricher to async
3. **R-C3** (`cache/core/redis_cache_client.py`): deletion gate — confirm zero import references before removal from disk

Do **not** implement R-C2 (`optimized_vllm_client.py`) or R-C4 (`neo4j_store.py`) without separate HITL approval.
