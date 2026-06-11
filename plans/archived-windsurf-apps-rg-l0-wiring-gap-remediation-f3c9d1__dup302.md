---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-l0-wiring-gap-remediation-f3c9d1__dup302.md'
original_relative_path: 'apps-rg-l0-wiring-gap-remediation-f3c9d1__dup302.md'
source_sha256: 01aa2ba7c98eabbf42bef0e12ff34a9fd838803175bdff7dd9e4dd4c67f5b861
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps-rg-l0-wiring-gap-remediation-f3c9d1

## Purpose

Six prior `apps_rg` plans (2026-05-02 through 2026-05-04) each built L0 cache components in isolation.
None of them wired the components into the live call path. This plan defines every wiring gap precisely
and schedules remediation waves. **No code is implemented in this document.**

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | W1.P1–W1.P2 | R1A exact-cache wiring (pre-pipeline short-circuit) | ~18k | `r1a_adapter.py` correct; `artifact_dir` available pre-run | Not Started | `check_r1a_cache` called before R4; hit returns cached result; `stamp_r1a_cache` called post-run |
| W2 | W2.P1–W2.P2 | R1B semantic-cache wiring (intent-vector lookup) | ~22k | `r1b_adapter.py` correct; `SemanticCacheManager` available | Not Started | `SEMANTIC_CACHE_D2_ENABLED=1` read; `AppsRgR1BCacheAdapter.recall_output_for_intent` called before L2; hit short-circuits |
| W3 | W3.P1 | Env-flag activation + `.env.example` documentation | ~6k | No other consumer changes the flags | Not Started | Both env flags documented in `.env.example`; default stays `"0"`; integration test confirms path selection |
| W4 | W4.P1 | R1A post-run stamping + R1B post-run store | ~12k | Successful L2 run produces `generated_resume.json` | Not Started | `stamp_r1a_cache` called after clean Exit X3; `store_intent_and_output` called after clean Exit X3 |
| W5 | W5.P1 | `route_registry.yaml` reader wired into R4 bootstrap | ~10k | `route_registry.yaml` schema stable | Not Started | R4 pipeline reads `apps_rg/config/route_registry.yaml` at startup; `route_id` from registry used in receipts |
| W6 | W6.P1 | Regression tests for all five wiring points | ~20k | Waves W1–W5 complete | Not Started | ≥25 new tests covering R1A hit/miss/stamp, R1B hit/miss/store, env-flag off path, registry read |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | R1A pre-flight check in `__main__.py` | `apps_rg/__main__.py`, `apps_rg/cache/r1a_adapter.py` | Must run before R4 is invoked; needs `runs_dir` path consistent with `artifact_dir` | ~9k | Not Started |
| W1.P2 | R1A short-circuit return shape | `apps_rg/__main__.py` | Return type must match `R4IntegratedRunResult`; need synthetic result on cache hit | ~9k | Not Started |
| W2.P1 | Intent construction from `raw_request` | `apps_rg/__main__.py`, `apps_rg/types/intent_payload.py`, `apps_rg/utils/intent_builder.py` | `build_intent_from_request` signature needs `candidate_profile_path` as `Path`; must happen before R4 call | ~11k | Not Started |
| W2.P2 | R1B recall gate in `__main__.py` | `apps_rg/__main__.py`, `apps_rg/cache/r1b_adapter.py` | Env flag `SEMANTIC_CACHE_D2_ENABLED` must be `"1"`; hit must short-circuit R4 entirely | ~11k | Not Started |
| W3.P1 | Env-flag documentation + integration smoke | `.env.example`, `apps_rg/__main__.py` | Both flags default `"0"` — must stay fail-closed; only active when explicitly set | ~6k | Not Started |
| W4.P1 | Post-run cache write-back | `apps_rg/__main__.py`, `apps_rg/cache/r1a_adapter.py`, `apps_rg/cache/r1b_adapter.py`, `apps_rg/chunking/resume_chunker.py` | Must run only on clean `X3=ALLOW`; `output_chunks` must be sourced from `generated_resume.json` | ~12k | Not Started |
| W5.P1 | Route registry bootstrap reader | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py`, `apps_rg/config/route_registry.yaml` | Registry reader must be fail-soft; `route_id` from YAML should override hardcoded `R4_SINGLE_ACTION` constant | ~10k | Not Started |
| W6.P1 | Full wiring regression suite | `tests/apps_rg/` or `tests/_apps_contract/` | Must cover all five wiring points with mocked caches; no live LLM calls | ~20k | Not Started |

---

## Gap Register (DIRECTLY OBSERVED — verified in code 2026-05-05)

### GAP-1: R1A pre-flight check never called

**What exists:**
- `apps_rg/cache/r1a_adapter.py` — `compute_r1a_key()`, `check_r1a_cache()`, `stamp_r1a_cache()` all implemented correctly.

**What is missing:**
- `apps_rg/__main__.py` never imports or calls any function from `r1a_adapter.py`.
- `_build_raw_request()` computes `jd_hash`, `brief_hash`, `resume_hash`, `policy_hash`, `blueprint_hash` — all R1A key ingredients — but they are passed into `raw_request` and then ignored for cache purposes.
- `main()` calls `run_integrated_r4_deterministic_pipeline()` directly without first computing an R1A key and checking `artifacts/apps_rg/runs/`.

**Expected call site (missing):**
```python
# In main(), BEFORE run_integrated_r4_deterministic_pipeline():
from apps_rg.cache.r1a_adapter import compute_r1a_key, check_r1a_cache
r1a_key = compute_r1a_key(
    source_resume_hash=raw_request["resume_hash"],
    target_company=raw_request["target_company"],
    target_role=raw_request["target_role"],
    jd_hash=raw_request["jd_hash"],
    briefing_hash=raw_request["brief_hash"],
    policy_hash=raw_request["policy_hash"],
    blueprint_hash=raw_request["blueprint_hash"],
)
cached_run = check_r1a_cache(r1a_key)
if cached_run:
    # short-circuit with synthetic R4IntegratedRunResult
    ...
```

**Proof:** `grep -r "r1a_adapter\|check_r1a_cache\|compute_r1a_key" apps_rg/__main__.py` → 0 results.

---

### GAP-2: R1B semantic recall never called

**What exists:**
- `apps_rg/cache/r1b_adapter.py` — `AppsRgR1BCacheAdapter`, `check_r1b_for_apps_rg()` fully implemented.
- `apps_rg/types/intent_payload.py` — `ResumeGenerationIntent` with `to_embedding_text()`, `to_cache_key_dict()`.
- `apps_rg/utils/intent_builder.py` — `build_intent_from_request()` (exists per r1b_adapter import chain).

**What is missing:**
- `apps_rg/__main__.py` never imports or calls `check_r1b_for_apps_rg()` or `AppsRgR1BCacheAdapter`.
- No `ResumeGenerationIntent` is ever constructed from CLI args.
- `SEMANTIC_CACHE_D2_ENABLED` env flag is never set to `"1"` anywhere in the codebase — not in `.env.example`, not in any config YAML, not in CI.

**Expected call site (missing):**
```python
# In main(), after R1A miss, BEFORE run_integrated_r4_deterministic_pipeline():
if os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") == "1":
    from apps_rg.cache.r1b_adapter import check_r1b_for_apps_rg
    r1b_hit = check_r1b_for_apps_rg(
        candidate_profile_path=str(candidate_path),
        target_company=args.target_company,
        target_role=args.target_role,
        policy_hash=raw_request["policy_hash"],
        blueprint_hash=raw_request["blueprint_hash"],
    )
    if r1b_hit:
        # short-circuit with synthetic R4IntegratedRunResult
        ...
```

**Proof:** `grep -r "r1b_adapter\|check_r1b\|AppsRgR1BCacheAdapter\|SEMANTIC_CACHE_D2_ENABLED" apps_rg/__main__.py` → 0 results.

---

### GAP-3: `EXACT_CACHE_D1_ENABLED` env flag never activated

**What exists:**
- `agentic_core/L0_routing/reasoning/route_gates.py` — `check_d1_exact_cache()` reads `os.environ.get("EXACT_CACHE_D1_ENABLED", "0")`. Returns `None` immediately when `"0"`.
- `check_route_gates()` composes D1 then D2. Called by `integrated_r4_deterministic_pipeline_run.py` at line 355.

**What is missing:**
- `EXACT_CACHE_D1_ENABLED` does not appear anywhere in the codebase outside `route_gates.py` itself.
- `.env.example` does not document it.
- No integration test sets it to `"1"` and verifies the D1 arm fires.

**Impact:** `check_route_gates()` is called on every R4 run but always returns `None` — the D1 arm in the generic L0 gate is permanently dead even though the app-level R1A adapter (`apps_rg/cache/r1a_adapter.py`) is a filesystem-based alternative that doesn't require the flag.

**Note:** GAP-1 and GAP-3 are parallel paths to the same capability. GAP-1 (app-level R1A) is simpler to activate. GAP-3 (generic L0 D1 via `route_gates.py`) requires wiring `L1ExactCache` which is an L4 dependency. Remediation in W3 should document both paths and decide which is canonical for `apps_rg`.

---

### GAP-4: Post-run R1A stamp never written

**What exists:**
- `apps_rg/cache/r1a_adapter.py` — `stamp_r1a_cache(key, run_dir_path)` writes `r1a_key.txt` to the run directory.

**What is missing:**
- `apps_rg/__main__.py` never calls `stamp_r1a_cache()` after a successful pipeline run.
- `artifact_dir` is computed in `main()` and is the correct target, but no post-run write-back happens.
- Without the stamp, every subsequent run with identical inputs is a cache miss forever — R1A can never hit even if the check were wired (GAP-1).

**Expected call site (missing):**
```python
# In main(), AFTER run_integrated_r4_deterministic_pipeline() on clean X3:
if not result.fault and not result.terminal_r5:
    from apps_rg.cache.r1a_adapter import stamp_r1a_cache
    stamp_r1a_cache(r1a_key, str(artifact_dir))
```

---

### GAP-5: Post-run R1B store never called

**What exists:**
- `apps_rg/cache/r1b_adapter.py` — `AppsRgR1BCacheAdapter.store_intent_and_output()` fully implemented; expects `output_chunks: list[dict]`.
- `apps_rg/chunking/resume_chunker.py` — `ResumeChunker` produces chunked output with lineage.

**What is missing:**
- `apps_rg/__main__.py` never calls `store_intent_and_output()` after a successful run.
- `output_chunks` would need to be sourced from the pipeline result (via `generated_resume.json` in `artifact_dir`).
- Without this, the semantic cache can never accumulate entries for future R1B hits.
- R1B recall (GAP-2) would always miss even if wired, because the store side is also unimplemented.

---

### GAP-6: `route_registry.yaml` never read at runtime

**What exists:**
- `apps_rg/config/route_registry.yaml` — declares `route_id: apps_rg.resume_generation_v1`, `execution_form: DETERMINISTIC_PIPELINE`, `l3_required: false`.

**What is missing:**
- Nothing in `apps_rg/__main__.py` or `integrated_r4_deterministic_pipeline_run.py` reads this file.
- The R4 pipeline hardcodes `ROUTE_ID = "R4_SINGLE_ACTION"` — it is never overridden by the registry-declared `route_id`.
- All receipts, Exit packets, and audit artifacts carry `R4_SINGLE_ACTION` instead of `apps_rg.resume_generation_v1`.
- The registry was built for auditable topology but has zero runtime consumers.

---

## Summary Gap Table

| Gap | Component Built | Call Site Missing | Severity |
|-----|----------------|-------------------|----------|
| GAP-1 | `r1a_adapter.py` | `__main__.py` pre-flight check | HIGH — R1A cache permanently dead |
| GAP-2 | `r1b_adapter.py` + `intent_payload.py` | `__main__.py` pre-flight check | HIGH — R1B cache permanently dead |
| GAP-3 | `route_gates.py` D1/D2 env gates | `EXACT_CACHE_D1_ENABLED` never set `"1"` | MEDIUM — generic L0 gate dead; app-level R1A is parallel path |
| GAP-4 | `r1a_adapter.stamp_r1a_cache` | `__main__.py` post-run write-back | HIGH — R1A can never accumulate hits even if GAP-1 fixed |
| GAP-5 | `r1b_adapter.store_intent_and_output` | `__main__.py` post-run write-back | HIGH — R1B can never accumulate hits even if GAP-2 fixed |
| GAP-6 | `route_registry.yaml` | No runtime reader | LOW — audit/observability gap; no functional impact |

---

## Non-Goals

- No changes to `route_gates.py`, `r1a_adapter.py`, `r1b_adapter.py`, or `intent_payload.py` — those are correct.
- No changes to `L4_state` caches, `SemanticCacheManager`, or `L1ExactCache`.
- No L3 orchestration changes.
- No HOP pipeline changes.
- No new embedding models or similarity thresholds.

---

## Parent Plans (context only — do not re-execute)

- `apps-rg-r1b-semantic-cache-hardening-c8d4a2` — built R1B adapter + intent payload
- `apps-rg-research-consolidation-*` — built research facade + company_research_loader
- `apps-rg-canonical-wireup-c8a4f2` — built GovernedAppRunner, R3 path
- `apps-rg-deferred-scope-followon-d4e1b9` — built static DAG registry, route_registry.yaml
- `apps-rg-l2-recipe-adapter-final-core-bound-d9f4a2` — wired L2 recipe resolution (the one wiring that DID land)
