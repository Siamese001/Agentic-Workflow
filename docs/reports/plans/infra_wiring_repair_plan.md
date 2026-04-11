# Infrastructure Wiring Repair Plan — Phase 4

**Generated:** 2026-04-11
**Findings source:** `docs/reports/plans/infra_wiring_findings.md` + `artifacts/infra_wiring_findings.json`
**ADG snapshot at plan time:** `adg_indexed_04112026_1604.sqlite`
**Scope:** Planning only. No code changes in this document.
**Stop condition:** After repair plan is written. No CI changes, no scorecard regeneration.

---

## A. Executive Summary

Phase 3 findings produced 10 distinct violations across 7 P1 rows, 5 P2 rows, and 2 P3 rows.
This plan organises them into 4 execution waves ordered strictly by **risk reduction**, not
by convenience or file proximity.

**Current state before any repairs:**
```
compliance_score:          96%
violations.p1 (ADG):        4   (2 zero-caller + 2 not-on-spine)
violations.p2 (ADG):        5   (3 mixed-usage + 2 duplicated-adapters)
violations.p3 (ADG):        6   (isolated experimental)
file_scan_violations:       3   (all google-import bypasses)
ratchets_blocking:          3
```

**Target state after Wave A + Wave B:**
```
compliance_score:          ~99%
violations.p1 (ADG):        0
violations.p2 (ADG):        3   (ceiling-accepted items remain)
violations.p3 (ADG):        6   (no change — quarantined by design)
file_scan_violations:       0
ratchets_blocking:          0
```

Wave C and D items do not affect ADG counts — they are architecture-decision gated or at
accepted ceilings.

**Decision rules applied throughout:**
- Delete (or deregister) over preserve for dead-duplicate zero-caller adapters.
- Reroute through existing sanctioned seam over inventing a new seam.
- Fail-closed on provider bypass; no exemptions without prior artifact support.
- Accepted-ceiling P2 items are NOT first-wave work.
- No CI ratchet changes until Phase 4 repairs are committed and ADG rebuild confirms clean.

---

## B. Patch Queue — Ordered by Risk Reduction

| Rank | Repair ID | Finding ID | Files changed | Type | HITL? | Risk reduction |
|---|---|---|---|---|---|---|
| 1 | R-A1 | F-P1-005, F-P2-004 | `infra_wiring_scan.py`, `infra_wiring_views.py` | Registry deregistration | No | Eliminates dead Redis duplicate, clears 2 ADG rows |
| 2 | R-A2 | F-P1-004, F-P1-006 | Same registries | Registry reclassification | No | Eliminates dormant S3 adapter from spine expectation, clears 2 ADG rows |
| 3 | R-B1 | F-P1-001 | `llm_judge.py` | Reroute through sanctioned seam | No | Eliminates Gemini API key bypass in evaluation harness |
| 4 | R-B2 | F-P1-002 | `provider_registry.py` | Reroute + factory fix | No | Eliminates duplicate provider bypass; fixes `create_default_registry()` |
| 5 | R-B3 | F-P2-002 | `semantic_enricher.py` | Remove lazy import fallback | No | Eliminates lazy OpenAI self-provisioning in enricher |
| 6 | R-C1 | F-P1-003 | `dependencygraph_validator.py` | Guardian type fix + policy decision | YES | Fixes misguarded L5 Google dependency |
| 7 | R-C2 | F-P1-007 | `optimized_vllm_client.py` | Architecture decision only | YES | Resolves aiohttp ADG blind spot |
| 8 | R-C3 | F-P1-004 §FB | `blob_storage_provider.py` | S3 usage investigation gate | YES | Confirms whether boto3 is orphaned or secretly used |
| 9 | R-C4 | §FE | `neo4j_store.py` | Deprecate-vs-formalize decision | YES | Resolves neo4j P3 fate |
| 10 | R-D1 | F-P2-003 | `apps_tracing_mixin.py` | OTel reroute | No | Structural hygiene only — accepted ceiling |
| 11 | R-D2 | F-P2-001 | `retrieval_layers.py` | Mixed-usage accepted | No | Accepted ceiling; no first-wave action |
| 12 | R-D3 | F-P2-004/005, F-P3-001/002 | — | Document-only | No | No action; maintain ceilings |

---

## C. Wave Breakdown

### Wave A — Registry-Only, No HITL, No Runtime Code Change
**Findings:** F-P1-004, F-P1-005, F-P1-006, F-P2-004
**Files touched:** `ops_scripts/ci/infra_wiring_scan.py`, `tools/generate/infra_wiring_views.py`
**No production Python files changed.**

Removes two dead adapters from the sanctioned registry. ADG rebuild after Wave A will show
`v_p1_zero_caller_infra = 0`, `v_p1_not_on_spine = 0`, `v_p2_duplicated_adapters = 1`.

### Wave B — Provider/Control-Plane Reroutes, No HITL
**Findings:** F-P1-001, F-P1-002, F-P2-002
**Files touched:** `llm_judge.py`, `provider_registry.py`, `semantic_enricher.py`
**Three production files changed; all are in adapter/evaluation layer.**

Reroutes all lazy `import google.generativeai` and `from openai import OpenAI` through the
pre-existing sanctioned seams (`infrastructure/sdks_mcps`). No new seams invented.
ADG view counts do not change (lazy imports permanently ADG-invisible), but file-scan
violations drop from 3 → 0.

### Wave C — HITL or Architecture Decision Required
**Findings:** F-P1-003, F-P1-007, §FB, §FE
**Blocked by explicit decision points — do not execute until HITL is complete.**

Each item has an open ambiguity from the findings report that must be resolved first.
Details in §F below.

### Wave D — Accepted Ceiling / Deferred
**Findings:** F-P2-001, F-P2-003, F-P2-004, F-P2-005, F-P3-001, F-P3-002
**No code changes. Document as accepted ceilings.**

These items are at or below their enforcement ceilings. They do not block Wave A/B. They must
not be bundled into the first PR.

---

## D. Per-Item Remediation Details

---

### R-A1 — Deregister Dead Redis Duplicate
**Finding:** F-P1-005 (zero-caller) + F-P2-004 (duplicated-adapter)
**Severity:** P1 HARDENING FAIL
**Remediation type:** Registry correction — no production code change

**Evidence baseline:**
- `agentic_core/cache/core/redis_cache_client.py` — ADG node 1492, caller_count=0, layer=L_SHARED
- `agentic_core/cache/redis_cache_client.py` (canonical, without `/core/`) — actively called, has `import redis` at module level (line 15)
- The `/core/` variant has a full `DeterministicRedisCache` implementation with lazy `import redis as _redis` inside `_connect()`, plus `check_redis_health_via_mcp()` and `check_redis_health()` utilities — it is NOT a trivial file, but has zero callers
- ADG: `v_p1_zero_caller_infra` row confirmed, `v_p2_duplicated_adapters = 2` confirmed

**Why this is the smallest safe fix:**
Removing from the registry entries makes the zero-caller and not-on-spine ADG views stop
surfacing it. No runtime code is touched. The file remains on disk (non-destructive first step).
File deletion is a separate follow-up step after the ADG rebuild confirms the registry change is clean.

**Registry changes required:**

In `ops_scripts/ci/infra_wiring_scan.py`, `SANCTIONED_ADAPTER_FILES`:
```python
# REMOVE this line:
"agentic_core/cache/core/redis_cache_client.py",
# ADD this comment in its place, or simply delete the entry:
# REMOVED 2026-04-11: dead duplicate — canonical path is agentic_core/cache/redis_cache_client.py (F-P1-005)
```

In `tools/generate/infra_wiring_views.py`, `_APPROVED_ADAPTER_PATHS`:
```python
# REMOVE this line:
"agentic_core/cache/core/redis_cache_client.py",
```

**Prerequisites:** None.
**HITL required:** No.
**ADG view delta after repair + rebuild:**
- `v_p1_zero_caller_infra`: 2 → 1 (blob_storage_provider remains until R-A2)
- `v_p1_not_on_spine`: 2 → 1
- `v_p2_duplicated_adapters`: 2 → 1
**Scorecard delta:** `violations.p1` partially reduced (−1 zero-caller, −1 not-on-spine). Full reduction waits for R-A2.
**Does NOT reduce real risk:** The file itself is dead and harmless. This is structural hygiene, but it unblocks the ratchet BLOCK on `zero-caller infra`.
**File deletion:** Schedule as a follow-up after ADG rebuild confirms clean. Do not delete in the same PR as the registry change.

---

### R-A2 — Reclassify blob_storage_provider.py as DORMANT
**Finding:** F-P1-004 (zero-caller) + F-P1-006 (not-on-spine)
**Severity:** P1 HARDENING FAIL
**Remediation type:** Registry reclassification — no production code change

**Evidence baseline:**
- `agentic_core/L4_state/utils/memory/blob_storage_provider.py` — ADG node 685, caller_count=0, layer=L4
- File contains: `LocalDiskAdapter` (stdlib only), `S3Adapter` (lazy `import boto3` inside `__init__` try/except), `SignalLedger`, three tombstoned Redis classes
- `S3Adapter.__init__` at line 301: `import boto3` inside `try...except ImportError: raise ImportError(...)` — the guard re-raises, making the silent-swallow guardian comment misleading but not a code defect
- `canonical_store.py` (declared consumer) only imports `botocore.exceptions` for error handling — it does NOT import `blob_storage_provider`
- No production code calls `create_storage_adapter()` anywhere (ADG zero-caller confirmed)
- The file has **no module-level boto3 import** — boto3 surface is reached only if `S3Adapter()` is instantiated, which never happens

**Why this is the smallest safe fix:**
The file should remain on disk. `LocalDiskAdapter` has full UWG integration (`get_write_gateway()`) that is non-trivial to recreate. The repair is to remove it from the sanctioned registry so the ADG views stop expecting an active caller.
S3 is genuinely dormant — §FB investigation (R-C3) can confirm this before any deletion decision.

**Registry changes required:**

In `ops_scripts/ci/infra_wiring_scan.py`, `SANCTIONED_ADAPTER_FILES`:
```python
# REMOVE this line:
"agentic_core/L4_state/utils/memory/blob_storage_provider.py",
# Note: file moves to DORMANT classification — do not add to FORBIDDEN_DIRS
```

In `tools/generate/infra_wiring_views.py`, `_APPROVED_ADAPTER_PATHS`:
```python
# REMOVE this line:
"agentic_core/L4_state/utils/memory/blob_storage_provider.py",
```

Optionally, add to a `_DORMANT_ADAPTER_PATHS` annotation list if one exists or is created:
```python
_DORMANT_ADAPTER_PATHS = [
    "agentic_core/L4_state/utils/memory/blob_storage_provider.py",  # F-P1-004: zero callers 2026-04-11
]
```

**Prerequisites:** R-A1 should complete first (same PR acceptable).
**HITL required:** No.
**ADG view delta after repair + rebuild:**
- `v_p1_zero_caller_infra`: 1 → 0
- `v_p1_not_on_spine`: 1 → 0
- `violations.p1`: 4 → 0
- `compliance_score`: 96% → ~99%
**Ratchet BLOCK cleared:** `zero-caller infra` + `not on spine`.
**Does NOT reduce real risk:** No live boto3 surface — this is structural hygiene.
**Blocked from deletion by:** R-C3 (S3 usage investigation must confirm no callers before deletion).

---

### R-B1 — Reroute GeminiJudge through infrastructure/sdks_mcps
**Finding:** F-P1-001
**Severity:** P1 HARDENING FAIL
**Remediation type:** Code repair — reroute lazy import through existing sanctioned seam

**Evidence baseline:**
- `agentic_core/evaluation/judges/llm_judge.py:260-278`
- `GeminiJudge._get_client()` contains `import google.generativeai as genai` at line 264 (method body)
- `GeminiJudge.__init__(self, gemini_client=None, model=None)` — client injection is ALREADY SUPPORTED (line 251-254). If `gemini_client` is passed, `_get_client()` returns it immediately (line 261-262)
- `infrastructure/sdks_mcps/__init__.py:73-81`: `create_vertex_client()` calls `genai.configure(api_key=api_key)` and returns the configured `genai` module
- `_get_client()` returns `genai.GenerativeModel(self._model)` — callers invoke `.generate_content(prompt, ...)` on the result

**Why the chosen remediation is the smallest safe fix:**
The injection path (`if self._client is not None: return self._client`) is already in place.
The fix only changes the fallback path inside `_get_client()`: replace the raw
`import google.generativeai` block with a call to `create_vertex_client()` from the sanctioned seam.
This is a single-function change with no API surface change — callers that already inject
`gemini_client` are unaffected. Callers that do not inject get the sanctioned seam fallback.

**Exact change prescription** (for execution phase — do not apply now):

In `agentic_core/evaluation/judges/llm_judge.py`, function `GeminiJudge._get_client()` (line 260):

Remove lines 264-278 (the `try: import google.generativeai` block through `return genai.GenerativeModel`).
Replace with:
```python
        from infrastructure.sdks_mcps import create_vertex_client
        try:
            configured_genai = create_vertex_client()
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                f"GeminiJudge: Google Gemini not available via sanctioned seam: {exc}"
            ) from exc
        return configured_genai.GenerativeModel(self._model)
```

**Prerequisites:** `infrastructure/sdks_mcps/__init__.py:create_vertex_client()` confirmed present (verified at line 73).
**HITL required:** No.
**ADG view delta:** None — lazy imports remain ADG-invisible. File-scan violation for `llm_judge.py` drops to 0.
**Real risk reduction:** HIGH — eliminates uncontrolled Gemini API key access in evaluation harness.
**Batch:** Same PR as R-B2 (identical pattern, same module tree).

---

### R-B2 — Reroute GeminiJudgeProvider + fix create_default_registry()
**Finding:** F-P1-002
**Severity:** P1 HARDENING FAIL
**Remediation type:** Code repair — two changes in same file

**Evidence baseline:**
- `agentic_core/evaluation/judges/provider_registry.py:88-107`
- `GeminiJudgeProvider._get_client()` at line 92: `import google.generativeai as genai` (method body, identical pattern to R-B1)
- `GeminiJudgeProvider.__init__(self, gemini_client=None, model=None)` — injection already supported (lines 60-75, inferred from `self._client` usage at line 89)
- `create_default_registry()` at line 248: `GeminiJudgeProvider()` constructed with NO arguments, triggering the fallback self-provision path on first call

**Change 1 — `GeminiJudgeProvider._get_client()`** (same pattern as R-B1):

Remove the `import google.generativeai` block (lines 92-107).
Replace with:
```python
        from infrastructure.sdks_mcps import create_vertex_client
        try:
            configured_genai = create_vertex_client()
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                f"GeminiJudgeProvider: Google Gemini not available via sanctioned seam: {exc}"
            ) from exc
        return configured_genai.GenerativeModel(self._model)
```

**Change 2 — `create_default_registry()` at line 246-253**:

Replace `GeminiJudgeProvider()` (no-arg construction) with pre-built client injection:
```python
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        try:
            from infrastructure.sdks_mcps import create_vertex_client
            configured_genai = create_vertex_client()
            default_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            pre_built_model = configured_genai.GenerativeModel(default_model)
            gemini = GeminiJudgeProvider(gemini_client=pre_built_model)
            registry.register(gemini, default=True)
            _log.info("[create_default_registry] Gemini provider auto-registered (API key found)")
        except (RuntimeError, ValueError, OSError, ImportError) as exc:
            _log.warning("[create_default_registry] Gemini registration failed: %s", exc)
```

Change 2 makes the factory fail-fast if the sanctioned seam is broken at import time rather than
at first evaluation call. This surfaces misconfiguration earlier.

**Prerequisites:** `infrastructure/sdks_mcps/__init__.py:create_vertex_client()` confirmed. R-B1 should be in same PR.
**HITL required:** No.
**ADG view delta:** None. File-scan violations for `provider_registry.py` drop to 0.
**Real risk reduction:** HIGH — closes the second path of uncontrolled Gemini provisioning.
**Batch:** Same PR as R-B1.

---

### R-B3 — Remove lazy OpenAI self-provisioning in semantic_enricher.py
**Finding:** F-P2-002
**Severity:** P2 WARNING
**Remediation type:** Remove fallback lazy import; require injection or route through sanctioned seam

**Evidence baseline:**
- `agentic_core/knowledge/enrichment/semantic_enricher.py:136`
- `SemanticEnricher._init_default_client()` contains `from openai import OpenAI` inside the method body
- `SemanticEnricher.__init__(self, llm_client=None, provider="openai", ...)` — injection already supported; `_init_default_client()` only runs when `llm_client is None`
- `infrastructure/sdks_mcps/__init__.py:53-60`: `create_openai_client()` returns `openai.AsyncOpenAI(api_key=api_key)` — sanctioned seam for OpenAI

**Why this is the smallest safe fix:**
The `llm_client` injection path is already supported. The only change needed is in
`_init_default_client()`: replace `from openai import OpenAI` with a call to
`create_openai_client()` from the sanctioned seam. No API surface change.

**Exact change prescription:**

In `agentic_core/knowledge/enrichment/semantic_enricher.py`, method `_init_default_client()`:

Remove the `from openai import OpenAI` block.
Replace with:
```python
        from infrastructure.sdks_mcps import create_openai_client
        try:
            self._client = create_openai_client()
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                f"SemanticEnricher: OpenAI not available via sanctioned seam: {exc}"
            ) from exc
```

**Note:** `create_openai_client()` returns `openai.AsyncOpenAI`. If `_init_default_client` currently
returns a synchronous `OpenAI` client, the caller must use the async interface or a sync wrapper.
Verify call sites in `SemanticEnricher` before applying. If the enricher is sync-only, either
wrap with `asyncio.run()` or use `openai.OpenAI` directly — in that case, the sanctioned seam
must be extended with a `create_openai_sync_client()` function before this repair is applied.
This is the **only prerequisite gate** for R-B3.

**Prerequisites:** Verify whether `SemanticEnricher` uses sync or async OpenAI interface. If async: immediate. If sync: requires sdks_mcps seam extension first.
**HITL required:** No.
**ADG view delta:** None (lazy import still invisible). File-scan improvement: not directly tracked (file is SANCTIONED, not in FORBIDDEN).
**Real risk reduction:** MEDIUM — closes uncontrolled OpenAI provisioning in knowledge enrichment path.
**Batch:** Can be in same PR as R-B1/R-B2 or a separate PR.

---

## E. Expected ADG and Scorecard Deltas After Each Wave

### After Wave A (R-A1 + R-A2)
```
v_p1_zero_caller_infra:     2 → 0   (-2)
v_p1_not_on_spine:          2 → 0   (-2)
v_p2_duplicated_adapters:   2 → 1   (-1)
violations.p1 (ADG):        4 → 0
violations.p2 (ADG):        5 → 4   (one duplicate removed)
compliance_score:           96% → ~99%
ratchets_blocking:          3 → 1   (only file-scan google-import ratchet remains)
```

ADG rebuild required after Wave A to confirm. Registry changes take effect only after ADG is
regenerated with the updated `_APPROVED_ADAPTER_PATHS` and `SANCTIONED_ADAPTER_FILES`.

### After Wave B (R-B1 + R-B2 + R-B3)
```
file_scan_violations:       3 → 0   (all 3 google imports fixed in llm_judge + provider_registry)
                                     (semantic_enricher openai: not file-scan tracked, but risk reduced)
ratchets_blocking:          1 → 0
ADG view counts:            no change (lazy imports permanently ADG-invisible)
compliance_score:           ~99% → 100% (if file-scan ratchet is the last blocker)
```

Note: `v_p0_provider_bypass` will remain 0 after Wave B — this is expected and correct.
The ADG cannot detect method-body lazy imports. The only proof of fix is the file-scan count.

### After Wave C (pending HITL decisions)
ADG deltas are decision-dependent:
- R-C1 resolved → `dependencygraph_validator.py` file-scan violation drops to 0 (if rerouted)
- R-C2 resolved (approve) → no ADG change; `v_p1_raw_http_outside_seam` ceiling updated
- R-C2 resolved (migrate) → `optimized_vllm_client.py` moves to new HTTP adapter; ADG edge changes
- R-C3 resolved (dormant) → `blob_storage_provider.py` file can be deleted; no ADG impact
- R-C4 resolved (deprecate) → `neo4j_store.py` file deleted; ADG blind spot resolved

### After Wave D (no changes)
No delta. Ceilings documented, not broken.

---

## F. Items Blocked on HITL or Explicit Architecture Decision

---

### R-C1 — dependencygraph_validator.py Google Dependency (F-P1-003)
**HITL trigger:** Guardian type mismatch + provider import in L5 Safety + constitutional §8
**Decision question:** Remove Google dependency from L5 validator, or obtain `allow-provider-bypass` guardian approval?

**Option A (preferred — fail-closed):** Remove `from google import genai` entirely.
`genai` is used as an AI code-style checker in `few_shot_hygiene` / `few_shot_style` string
constants. The constants are prompt templates — they do NOT require a live `genai` object; the
variable `genai` only appears bound to `None` in the ImportError fallback. Search lines 187-528
to confirm whether any method actually calls `genai.<method>()` before choosing option.

**Option B (escalation path):** If the validator's AI-assisted style check is intentional and
production-critical:
1. Replace `# guardian: allow-silent-swallow` with `# guardian: allow-provider-bypass -- L5 style validator uses Gemini for code hygiene checks; degrades to null-judge when unavailable`
2. Route through `infrastructure/sdks_mcps.create_vertex_client()` instead of bare import
3. Confirm via HITL that L5 depending on external provider is explicitly approved

**Why HITL is required:** Constitutional §8 requires explicit HITL approval for any `allow-provider-bypass` guardian. The type change from `allow-silent-swallow` to `allow-provider-bypass` constitutes a new exemption declaration.

**Blocks:** File-scan violation for `dependencygraph_validator.py` (3rd google import). Without this, file-scan violations reach 0 only after R-B1 + R-B2 (which fix the other 2).

---

### R-C2 — optimized_vllm_client.py aiohttp Architecture Decision (F-P1-007)
**HITL trigger:** Architecture decision §FC — approve or migrate?
**Decision question:** Is raw `aiohttp.ClientSession` in L3 an approved production pattern or must vLLM HTTP routing go through `enhanced_http_server.py`?

**Current state:** Full `aiohttp` session lifecycle at lines 21-22, connection pooling
(20 total / 10 per host), 5-min timeout, batching, concurrency control — `SANCTIONED_UNDER_REVIEW`.

**Option A (Approve):** Add `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py`
to `_APPROVED_ADAPTER_PATHS` with lifecycle `ACTIVE_APPROVED`. Set `v_p1_raw_http_outside_seam`
CI ratchet ceiling to 1. ADG cannot verify this but file scan will no longer flag it.

**Option B (Migrate):** Require `aiohttp.ClientSession` lifecycle to move to a new or existing
approved HTTP adapter. `enhanced_http_server.py` or `api_gateway_integration.py` would host
the session pool. `optimized_vllm_client.py` becomes a thin caller. Reduces to 0 the raw HTTP
surface in L3. Higher effort, lower immediate risk.

**Why HITL is required:** Approving Option A sets a precedent for raw HTTP in L3 for all vLLM
consumers. Option B requires architectural scoping of the migration.

**Blocks:** `v_p1_raw_http_outside_seam` ratchet ceiling. Neither option can be implemented
without explicit architecture sign-off.

---

### R-C3 — S3/blob_storage_provider.py Usage Investigation Gate (§FB)
**HITL trigger:** Confirmation required before deletion decision.
**Decision question:** Is there any production path (outside the adapter itself) that uses boto3 or S3?

**Investigation required:**
1. ADG fan-out from `blob_storage_provider.py` node 685 — verify no outgoing consumers
2. File scan: `grep -r "blob_storage_provider" --include="*.py" .` to confirm no callers
3. File scan: `grep -r "create_storage_adapter" --include="*.py" .` to confirm factory is never called
4. File scan: `grep -r "S3Adapter\|boto3" --include="*.py" . --exclude-dir=agentic_core/L4_state/utils/memory` to confirm no alternate boto3 paths

**Expected result:** All 4 scans return zero matches outside the file itself. If confirmed, `blob_storage_provider.py` can be deleted (as a Wave A follow-on commit after R-A2 deregisters it).

**Blocks:** File deletion decision for `blob_storage_provider.py`. The deregistration (R-A2) can proceed without this gate; deletion cannot.

---

### R-C4 — neo4j_store.py: Deprecate vs. Formalize (§FE)
**HITL trigger:** Architectural status of Neo4j unresolved.
**Decision question:** Deprecate Neo4j or formalize it as an approved surface?

**Current state:** `agentic_core/L4_state/enforcement/neo4j_store.py` — ADG-invisible (indexing gap),
0 callers, broken guard (lines 88-93: `raise ImportError` before `GraphDatabase = None` makes
fallback dead code), EXPERIMENTAL_ISOLATED.

**Option A (Deprecate):** Add `neo4j` to `FORBIDDEN_IMPORTS`. Delete `neo4j_store.py` after
confirming 0 callers. Remove from SANCTIONED if present.

**Option B (Formalize):** Fix the guard pattern (remove `raise` before `GraphDatabase = None`),
document use case, assign a caller, add to `SANCTIONED_ADAPTER_FILES`. Add to `_APPROVED_ADAPTER_PATHS`.

**Why HITL is required:** Phase 3 finding F-P3 classified this as EXPERIMENTAL_ISOLATED, but
the ADG indexing gap means the zero-caller state cannot be structurally proven — only file-read
confirmed. The decision also sets the precedent for whether graph databases are an approved
infrastructure surface.

**Blocks:** Neo4j fate in Phase 5+ scorecard. Currently P3; could escalate or be eliminated.

---

## G. Recommended First Bounded Implementation Wave

**Execute Wave A first, in a single PR.**

Wave A is bounded by exactly 2 registry files:
- `ops_scripts/ci/infra_wiring_scan.py`
- `tools/generate/infra_wiring_views.py`

No production Python files are modified. No runtime behavior changes. Zero risk of test regression.
After Wave A PR merges, run ADG rebuild and verify:
- `v_p1_zero_caller_infra = 0`
- `v_p1_not_on_spine = 0`
- `v_p2_duplicated_adapters = 1`
- `compliance_score ≥ 99%`

**Then execute Wave B in a second PR** (R-B1 + R-B2 batched, R-B3 separate or same PR after
sync/async interface verification).

**Do not merge Wave B before Wave A ADG rebuild confirms clean.**
**Do not open Wave C items until HITL decisions are recorded for R-C1, R-C2, R-C3, R-C4.**
**Do not touch Wave D items in Phase 4.**

---

## Appendix: Fixes That Reduce Real Risk Without Moving ADG Counts

| Repair | Risk reduced | ADG count impact |
|---|---|---|
| R-B1 (GeminiJudge reroute) | HIGH — eliminates uncontrolled Gemini API key access | None — ADG blind |
| R-B2 (GeminiJudgeProvider reroute) | HIGH — eliminates duplicate provider bypass | None — ADG blind |
| R-B3 (semantic_enricher OpenAI) | MEDIUM — eliminates lazy OpenAI self-provisioning | None — ADG blind |
| R-C1 (dependencygraph_validator) | LOW-MEDIUM — fixes misguarded L5 provider dep | None — ADG blind |

All four Wave B items are ADG-invisible but materially reduce provider-bypass risk.
The ADG score improvement from these comes entirely through the file-scan ratchet, not through
view counts.

## Appendix: Fixes That Only Improve Structural Hygiene

| Repair | Description |
|---|---|
| R-A1 | Dead duplicate deregistration — zero runtime impact |
| R-A2 | Dormant adapter deregistration — zero runtime impact |
| R-D1 | OTel bypass in apps_tracing_mixin — graceful degradation already in place |
| R-D2 | retrieval_layers.py mixed usage — accepted ceiling, no regression |

## Appendix: Fixes Blocked by ADG Visibility Limitations

| Finding | View | Why blocked | Mitigation |
|---|---|---|---|
| F-P1-001/002 | v_p0_provider_bypass | Lazy method-body imports not in ADG edges | File scanner |
| F-P1-007 | v_p1_raw_http_outside_seam | External PyPI packages not in ADG nodes | File scanner |
| F-P1-003 | v_p0_provider_bypass | try/except module import not in ADG edges | File scanner |

## Appendix: Fixes That Must NOT Be Touched in Wave A

| Item | Reason |
|---|---|
| `apps_tracing_mixin.py` | Accepted ceiling; not a Wave A item |
| `retrieval_layers.py` | Accepted ceiling; chromadb mixed usage is sanctioned |
| `optimized_vllm_client.py` | Architecture decision pending (R-C2) |
| `dependencygraph_validator.py` | HITL required (R-C1) |
| `neo4j_store.py` | Architecture decision pending (R-C4) |
| Any CI ratchet | No CI changes until Wave B repairs committed and ADG rebuild clean |
