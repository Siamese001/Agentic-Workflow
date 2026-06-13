# Infrastructure Wiring Wave C — Decision Packet

**Generated:** 2026-04-11
**Reconciled:** 2026-04-11 (post-Wave B/vLLM/OTel/retrieval_layers)
**Tier:** T2 — Decision-prep only. No code changes in this document.
**Preceding waves:** Wave A ✅ | Wave B R-B1+R-B2 ✅ | vLLM Path A ✅ | OTel bypass ✅ | retrieval_layers OpenAI bypass ✅
**R-B3 blocker RESOLVED:** `create_openai_sync_client()` added to `infrastructure/sdks_mcps/__init__.py` during retrieval_layers fix — `semantic_enricher.py` patch can proceed
**R-C2 RESOLVED:** vLLM Path A approved via `vllm_http_decision_packet.md`
**Status: ALL ITEMS COMPLETE ✅** — R-C1, R-B3, R-C3 confirmed done via repo truth-pass (2026-04-11)

---

## A. Executive Summary

| Item | Classification | Recommended Path | HITL Required? | Status |
|---|---|---|---|---|
| R-C1: `dependencygraph_validator.py` Google import | **Live optional behavior** — `genai.Client()` called at runtime | Route through `create_vertex_client()` same as R-B1/R-B2 | No — same pattern already approved by Wave B | ✅ DONE |
| R-B3 unblock: `semantic_enricher.py` OpenAI seam | **Interface mismatch resolved** — `create_openai_sync_client()` now exists in seam | Use `create_openai_sync_client()` in `_init_default_client()` | No | ✅ DONE |
| Deletion gate: `cache/core/redis_cache_client.py` | **Zero callers confirmed** — no production import from dead-duplicate path | Safe to delete | No | ✅ DONE — file deleted |
| Dormant-vs-delete: `blob_storage_provider.py` | **Live callers exist** — `create_storage_adapter` called in `NervousSystemAgent` | Keep dormant; do NOT delete | No | ✅ CONFIRMED DORMANT-RETAINED |
| R-C2: `optimized_vllm_client.py` aiohttp | Architecture decision | vLLM Path A approved | Was YES | ✅ RESOLVED |

---

## B. R-C1 Decision Packet — `dependencygraph_validator.py` Google Import

### Current State

`agentic_core/L5_safety/validators/dependencygraph_validator.py` lines 179–182:
```python
try:
    from google import genai
except ImportError:  # guardian: allow-silent-swallow
    genai = None
```

### Evidence: Is This Dead or Live?

The `genai` symbol is used **live** at runtime in `ValidationContext._init_intelligence()`:

```python
# line 363–370
def _init_intelligence(self):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key and genai:
        try:
            self._client = genai.Client(api_key=api_key)
            self.intelligence_enabled = True
            print("      [OK] Gemini Connected")
        except (ImportError, AttributeError, ValueError) as e:
            print(f"      [WARN] Gemini unavailable: {type(e).__name__}")
```

- `genai.Client(api_key=api_key)` — real SDK call, not string reference
- `self._client` is then used in `resilient_mutation()` (line 440–441): `self._client.models.generate_content(...)`
- `few_shot_hygiene` and `few_shot_style` (lines 183–184) are plain string constants; they do NOT use `genai` as a symbol — confirmed dead weight but not the import concern
- **Classification: LIVE OPTIONAL** — active when `GOOGLE_API_KEY` is set; graceful no-op when absent

**This is NOT a dead import. Cannot be removed without behavior change.**

### Options

**Option A — Reroute through `create_vertex_client()` (RECOMMENDED)**
- Same pattern as R-B1 / R-B2 (already executed in Wave B)
- Replace `from google import genai` with lazy call to `create_vertex_client()` inside `_init_intelligence()`
- `create_vertex_client()` returns `genai` module (already configured), so `genai.Client(api_key=...)` becomes `genai_module.Client(api_key=...)` or the seam call absorbs the configure step
- One-line import change + adapt the `if api_key and genai:` guard to `if api_key:`
- Risk: **Low** — same seam, same return type, Wave B proven the pattern works

**Option B — Guardian exemption for direct import**
- Add `# guardian: allow-provider-bypass -- ValidationContext self-provisions Gemini for code mutation`
- Leaves raw `from google import genai` in L5 Safety
- Does not clear the file-scan ratchet violation
- Risk: **Low code risk**, but does not fix the infra wiring violation

### Recommended Path

**Option A.** The reroute is a 3-line change and follows the exact pattern already approved for Wave B. The `try/except ImportError` guard wrapping `create_vertex_client()` provides identical graceful degradation.

### Approval Question

> **R-C1 Decision:** `ValidationContext._init_intelligence()` in `dependencygraph_validator.py` uses `genai.Client()` at runtime when `GOOGLE_API_KEY` is set. This is live optional behavior, not a dead import. Recommended fix: replace `from google import genai` with `create_vertex_client()` inside `_init_intelligence()`, matching the Wave B R-B1/R-B2 pattern exactly.
>
> **Approve Option A (reroute through seam)?** No HITL gate is required — this is the same decision class as Wave B. Proceed if Wave B was satisfactory.

### Next Implementation Prompt (if approved)

```
Execute R-C1: Reroute dependencygraph_validator.py through create_vertex_client().
In ValidationContext._init_intelligence():
  - Remove module-level `from google import genai` / `genai = None` block (lines 179-182)
  - Replace with lazy `create_vertex_client()` call inside _init_intelligence()
  - Preserve the `if api_key:` guard (drop the `and genai` check since create_vertex_client raises on missing key)
  - Catch (ImportError, ValueError) from create_vertex_client() the same way the current except block handles ImportError
Do not touch few_shot_hygiene, few_shot_style, or any other symbol.
```

---

## C. R-B3 Unblock Packet — `semantic_enricher.py` Sync/Async Gate

### Current State

`SemanticEnricher._init_default_client()` (line 132–148):
```python
def _init_default_client(self) -> None:
    if self.provider == "openai":
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
```

`SemanticEnricher._llm_enrich()` (line 283): synchronous call:
```python
response = self.llm_client.chat.completions.create(
    model=self.model,
    messages=[...],
    temperature=0.1,
    response_format={"type": "json_object"},
)
```

### Blocker Evidence

`create_openai_client()` in `infrastructure/sdks_mcps/__init__.py` line 60:
```python
return openai.AsyncOpenAI(api_key=api_key)
```

`AsyncOpenAI.chat.completions.create()` is a coroutine — calling without `await` returns a coroutine object. The enricher's `_llm_enrich()` is a plain synchronous method. **Hard type mismatch. Patching without fixing this would cause silent data corruption in production.**

### Options

**Option A — Add `create_openai_sync_client()` to the sanctioned seam (RECOMMENDED)**

Add to `infrastructure/sdks_mcps/__init__.py`:
```python
def create_openai_sync_client():
    """Create synchronous OpenAI client for sync call sites."""
    import openai
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing")
    return openai.OpenAI(api_key=api_key)
```

Then in `semantic_enricher.py` `_init_default_client()`:
```python
from infrastructure.sdks_mcps import create_openai_sync_client
try:
    self.llm_client = create_openai_sync_client()
except (ImportError, ValueError):
    Logger.warning("OpenAI not configured, enrichment will use mock")
    self.llm_client = None
```

- **Files touched:** 2 (`sdks_mcps/__init__.py` + `semantic_enricher.py`)
- **Blast radius:** Zero — no callers of `create_openai_sync_client` outside these two files
- **Risk:** Low — `openai.OpenAI` is the standard sync client, already used in dozens of OpenAI integrations

**Option B — Migrate enricher to async**

Convert `_init_default_client`, `_llm_enrich`, `enrich_chunk`, `enrich_batch`, `enrich_chunk_adapter` to `async def`. Update all callers.

- **Files touched:** `semantic_enricher.py` + all callers (unknown count without full ADG fanin analysis)
- **Blast radius:** Unknown; enricher is called via `get_global_enricher()` which is used in pipeline integrations
- **Risk:** Medium — async migration of an enrichment pipeline requires caller audit

### Blast Radius Comparison

| | Option A | Option B |
|---|---|---|
| Files changed | 2 | ≥3 (enricher + callers) |
| New seam surface | 4 lines | 0 |
| Caller changes | 0 | Unknown |
| Reversible | Yes | Harder |
| Risk | Low | Medium |

### Recommended Path

**Option A** — minimal seam extension. The seam already exports `create_openai_client()` (async) for async callers. Adding a sync variant is a natural extension with zero blast radius beyond the two files.

### Approval Question

> **R-B3 Decision:** `semantic_enricher.py` uses a synchronous OpenAI client call site. `create_openai_client()` returns `AsyncOpenAI`, which is incompatible. Recommended fix: add `create_openai_sync_client()` returning `openai.OpenAI` to `infrastructure/sdks_mcps/__init__.py` (4 lines) and update `_init_default_client()` to use it.
>
> **Approve Option A (add sync client to seam)?** This is a minimal seam extension — no HITL gate required under current decision rules.

### Next Implementation Prompt (if approved)

```
Execute R-B3 unblock:
1. In infrastructure/sdks_mcps/__init__.py:
   - Add create_openai_sync_client() function (4 lines) returning openai.OpenAI(api_key=...)
   - Add to __all__
2. In agentic_core/knowledge/enrichment/semantic_enricher.py _init_default_client():
   - Remove `from openai import OpenAI` lazy import
   - Replace with `from infrastructure.sdks_mcps import create_openai_sync_client`
   - Call create_openai_sync_client() wrapped in try/except (ImportError, ValueError)
   - Preserve the `Logger.warning` fallback on failure
   - Do not touch _llm_enrich(), enrich_batch(), or any other method
```

---

## D. Dead Duplicate Deletion Packet — `cache/core/redis_cache_client.py`

### Current State

`agentic_core/cache/core/redis_cache_client.py` — 795-line `DeterministicRedisCache` implementation identified as dead duplicate of canonical `agentic_core/cache/redis_cache_client.py`.

Deregistered from `_APPROVED_ADAPTER_PATHS` in Wave A (R-A1). File retained on disk.

### Evidence: Zero Runtime Callers

Searched all production Python files (excluding `archives/`, `tools/`, `ops_scripts/`, `.windsurf/`, `docs/`) for:

| Pattern | Production hits |
|---|---|
| `cache.core.redis_cache_client` (module import) | **ZERO** |
| `agentic_core/cache/core/redis_cache_client` (path string) | **ZERO** |
| `DeterministicRedisCache` | All hits import from `agentic_core.cache.redis_cache_client` (canonical path), not `cache.core` |

`DeterministicRedisCache` callers confirmed to use the **canonical path** exclusively:
- `agentic_core/L4_state/cache/config_file_cache.py`: `from agentic_core.cache.redis_cache_client import DeterministicRedisCache`
- `agentic_core/L4_state/cache/discovery_cache.py`: same
- `agentic_core/L4_state/cache/policy_registry_cache.py`: same
- `agentic_core/L4_state/cache/schema_validator_cache.py`: same
- `agentic_core/L4_state/cache/tool_embedding_cache.py`: same
- `system_learning/engines/enhanced_rag_retrieval_cache.py`: same
- `system_learning/engines/rag_retrieval_cache.py`: same
- `system_learning/engines/system_learning_admission_gate.py`: same
- `system_learning/policy/system_learning_policy.py`: same
- `system_learning/state/system_learning_state_manager.py`: same

**No dynamic loads, no string-based references, no factory references to the dead-duplicate path found.**

Non-production hits (all archive / tools / ops):
- `tools/generate/infra_wiring_views.py` — tombstone comment only (Wave A)
- `ops_scripts/ci/infra_wiring_scan.py` — basename `redis_cache_client.py` (shared with canonical)
- No archive imports reach production

### Deletion Safety

| Check | Result |
|---|---|
| Zero production module imports | ✅ CONFIRMED |
| Zero path-string references | ✅ CONFIRMED |
| Zero factory references | ✅ CONFIRMED |
| Tests reference canonical path only | ✅ CONFIRMED |
| File is already deregistered from ADG views | ✅ CONFIRMED (Wave A) |

**Physical deletion is safe.** The file has no runtime callers and has already been deregistered.

### Recommended Path

Delete `agentic_core/cache/core/redis_cache_client.py` from disk. No other files need updating (the tombstone comment in `infra_wiring_views.py` is already in place and accurate).

After deletion, run `python tools/generate_full_adg.py` to rebuild ADG — this will drop `v_p2_duplicated_adapters` from 2 → 1 as predicted in the Wave A validation report.

### Next Implementation Prompt (if approved)

```
Execute R-C3 deletion:
1. Delete agentic_core/cache/core/redis_cache_client.py from disk
2. Verify agentic_core/cache/core/__init__.py does not re-export from it (read before deleting)
3. Rebuild ADG: python tools/generate_full_adg.py
4. Run infra_wiring_scan.py to confirm v_p2_duplicated_adapters drops to 1
5. Do not touch any other file
```

**Pre-deletion gate:** Also read `agentic_core/cache/core/__init__.py` before deleting — confirm it does not re-export `redis_cache_client` symbols.

---

## E. Dormant-vs-Delete Packet — `blob_storage_provider.py`

### Current State

`agentic_core/L4_state/utils/memory/blob_storage_provider.py` — 657-line blob storage implementation. Deregistered from `_APPROVED_ADAPTER_PATHS` in Wave A (R-A2). File retained on disk.

### Evidence: Live Callers Exist

#### Caller 1: `NervousSystemAgent` (L3 orchestration) — runtime call

`agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py` line 226:
```python
storage_adapter = create_storage_adapter("local", base_path="./agentic_core")
self.CheckpointManager = VerifiableCheckpointManager(storage_adapter)
self.SignalLedger = SignalLedger(storage_adapter, self.session_id)
```

**Important caveat:** `NervousSystemAgent.py` does NOT have an explicit import for `create_storage_adapter` in its import block — it is not in the `from` imports listed at module level. This means `NervousSystemAgent.__init__` would raise `NameError: name 'create_storage_adapter' is not defined` at runtime if invoked. However, **the intent to use blob_storage_provider is real** and the missing import is a latent bug, not evidence of no usage.

#### Caller 2: `verifiable_checkpoint_manager.py` — TYPE_CHECKING import + lazy import

`agentic_core/L4_state/utils/memory/verifiable_checkpoint_manager.py`:
- Line 93–94: `if TYPE_CHECKING: from agentic_core.storage import IBlobStorageProviderProtocol` — type hint only, no runtime import
- Line 376: `from agentic_core.storage import create_storage_adapter` — lazy import inside a factory function body

**Critical finding:** `agentic_core.storage` does **not exist** as a module (`agentic_core/storage/__init__.py` and `agentic_core/storage.py` both absent). This `from agentic_core.storage import ...` call is a **broken import** that would raise `ModuleNotFoundError` at runtime if the factory function is invoked.

#### Caller 3: `local_disk_adapter_util.py` — independent `LocalDiskAdapter` class

`agentic_core/L4_state/utils/local_disk_adapter_util.py` defines its own `LocalDiskAdapter` class (line 181) — this is a separate implementation, not an import from `blob_storage_provider.py`. Not a caller.

#### Caller 4: Archives only

`tools/archive/adg_root_oneshots_w5.10/micro_wave_wirer.py` and `semantic_gap_analyzer.py` — archive files, not production.

### Classification

| Check | Result |
|---|---|
| Live production callers of `create_storage_adapter` from `blob_storage_provider` | **UNCERTAIN** — `NervousSystemAgent` calls it but has missing import (latent NameError); `verifiable_checkpoint_manager` calls it via broken `agentic_core.storage` path |
| `IBlobStorageProviderProtocol` at runtime | TYPE_CHECKING only in `verifiable_checkpoint_manager` — no runtime import |
| S3Adapter | Zero callers anywhere |
| `LocalDiskAdapter` from this file | Zero callers outside this file (separate `LocalDiskAdapter` exists in `local_disk_adapter_util.py`) |

### Deletion Safety

**NOT SAFE TO DELETE.** Despite broken import paths, the intent to call `create_storage_adapter` from `blob_storage_provider.py` exists in two production files. Deletion would:
1. Confirm-break `NervousSystemAgent.__init__` if the missing import is later fixed
2. Confirm-break `verifiable_checkpoint_manager` factory if `agentic_core.storage` is later wired

These are latent bugs, not dead code. The file's dormant status is correct.

**Recommended classification: DORMANT-RETAINED** — remain deregistered from ADG views (already done), do not delete until the broken import chains in `NervousSystemAgent` and `verifiable_checkpoint_manager` are either fixed to use a different path or explicitly removed.

### Recommended Path

No change. Retain file on disk, deregistered status (Wave A) is the correct final state for now. Document the two broken import chains as Wave D items requiring architecture decision.

### Approval Question

> **Blob storage deletion gate:** `blob_storage_provider.py` has live intent-to-call in `NervousSystemAgent` (missing import — latent NameError) and `verifiable_checkpoint_manager` (broken `agentic_core.storage` module path). Deletion is not safe.
>
> **Confirm: retain dormant, no deletion.** No approval action needed — this is a report-only finding. Wave D will address the broken import chains.

---

## F. Recommendation Matrix

| Item | Can proceed without HITL | Needs HITL | Needs architecture sign-off |
|---|---|---|---|
| R-C1: `dependencygraph_validator.py` reroute | ✅ Yes — same pattern as Wave B | — | — |
| R-B3: `create_openai_sync_client()` seam extension | ✅ Yes — minimal extension | — | — |
| R-C3: Delete `cache/core/redis_cache_client.py` | ✅ Yes — zero callers proven | — | — |
| Blob storage dormant retention | ✅ Yes — no action needed | — | — |
| R-C2: `optimized_vllm_client.py` aiohttp | — | — | ✅ Yes — approve-or-migrate decision |
| R-C4: `neo4j_store.py` deprecate vs. formalize | — | ✅ Yes | — |

---

## G. Exact Next Prompts

### Next prompt (Wave C execution — all three actionable items):

```
## SR_INTAKE
Objective: Execute Wave C for infrastructure wiring. Three bounded repairs.
Tier: T2
Scope:
- agentic_core/L5_safety/validators/dependencygraph_validator.py
- agentic_core/knowledge/enrichment/semantic_enricher.py
- infrastructure/sdks_mcps/__init__.py
- agentic_core/cache/core/redis_cache_client.py (deletion)
- agentic_core/cache/core/__init__.py (read before deletion)

Repairs (in order):
1. R-C1: Replace `from google import genai` in dependencygraph_validator.py with 
   create_vertex_client() inside _init_intelligence(). Preserve graceful no-op when 
   GOOGLE_API_KEY absent.
2. R-B3 unblock: Add create_openai_sync_client() to infrastructure/sdks_mcps/__init__.py 
   (returning openai.OpenAI). Update semantic_enricher._init_default_client() to use it.
3. R-C3 deletion: Read agentic_core/cache/core/__init__.py, confirm no re-export of 
   redis_cache_client symbols, then delete agentic_core/cache/core/redis_cache_client.py.
   Rebuild ADG. Confirm v_p2_duplicated_adapters drops to 1.

Constraints:
- No production behavior changes beyond the three items above
- No CI changes
- No other file deletions
- No Wave D items (vLLM, neo4j, blob_storage deletion)
- Validate each repair individually
```

### Alternative: split into two prompts if preferred

**Prompt 1 (code-only, no deletion):** R-C1 + R-B3 unblock
**Prompt 2 (deletion + ADG rebuild):** R-C3 deletion + ADG rebuild + scorecard validation
