---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\infra_wiring_wave_a_validation.md'
original_relative_path: 'infra_wiring_wave_a_validation.md'
source_sha256: cf8ec1ae03078c404c81246962201bfb822617acd612910956de8fcb9e6d2201
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave A Validation Report — Infrastructure Wiring Phase 5

**Executed:** 2026-04-11T20:41:58Z
**ADG snapshot (post-rebuild):** `adg_indexed_04112026_1631.sqlite`
**Scorecard written:** `artifacts/infra_wiring_scorecard.json`
**Status: WAVE A COMPLETE ✅**

---

## Files Changed

| File | Change |
|---|---|
| `tools/generate/infra_wiring_views.py` | Removed 2 entries from `_APPROVED_ADAPTER_PATHS` |

**No production runtime files changed. No files deleted from disk.**

## Exact Entries Removed

From `_APPROVED_ADAPTER_PATHS` in `tools/generate/infra_wiring_views.py`:

```python
# REMOVED (R-A2):
"agentic_core/L4_state/utils/memory/blob_storage_provider.py"

# REMOVED (R-A1):
"agentic_core/cache/core/redis_cache_client.py"
```

Replaced with tombstone comments (file, line ~59-60):
```python
# REMOVED 2026-04-11 R-A2: blob_storage_provider.py deregistered — zero callers, dormant (F-P1-004). File retained on disk.
# REMOVED 2026-04-11 R-A1: cache/core/redis_cache_client.py deregistered — dead duplicate of cache/redis_cache_client.py (F-P1-005). File retained on disk.
```

`ops_scripts/ci/infra_wiring_scan.py` — **unchanged** (basename exemptions were correct as-is; the ADG view counts are driven entirely by `_APPROVED_ADAPTER_PATHS`, not by the scan-level `SANCTIONED_ADAPTER_FILES`).

---

## Before / After Metrics

| Metric | Before (Phase 3) | After (Wave A) | Delta | Target met? |
|---|---|---|---|---|
| `v_p1_zero_caller_infra` | 2 | **0** | −2 | ✅ |
| `v_p1_not_on_spine` | 2 | **0** | −2 | ✅ |
| `v_p2_duplicated_adapters` | 2 | 2 | 0 | ⚠️ see note |
| `violations.p0` | 0 | 0 | 0 | ✅ |
| `violations.p1` | 4 | **0** | −4 | ✅ |
| `violations.p2` | 5 | 5 | 0 | ✅ (ceiling accepted) |
| `violations.p3` | 6 | 6 | 0 | ✅ (quarantined) |
| `compliance_score` | 96% | **100%** | +4 | ✅ |
| `ratchet: zero-caller infra` | BLOCK | **COMPLIANT** | — | ✅ |
| `ratchet: not on L0-L6 spine` | BLOCK | **COMPLIANT** | — | ✅ |

### Note on `v_p2_duplicated_adapters`

The plan predicted 2 → 1. Actual result: **2 → 2** (no change).

**Root cause:** `v_p2_duplicated_adapters` counts infra surfaces where more than one adapter in
`_APPROVED_ADAPTER_PATHS` imports the same raw infra package. After removing the two deregistered
entries, the view recomputed from the ADG — `agentic_core/cache/redis_cache_client.py` (canonical)
still shows duplicate-adapter count of 2 because the ADG edges for the dead-duplicate file
(`cache/core/redis_cache_client.py`) were indexed into the prior SQLite snapshot and are present
in the fresh `adg_indexed_04112026_1631.sqlite` (the ADG rebuild indexes files from disk — the file
still exists). The view counts edges, not registry entries.

**Impact:** Zero. The ratchet ceiling for `duplicated_adapters` is 2, status is ACCEPTED. No
regression, no BLOCK. The count will reach 1 only after `agentic_core/cache/core/redis_cache_client.py`
is deleted from disk (a follow-up step gated on R-C3 confirmation).

**The primary Wave A goals (P1 counts to 0, compliance 100%, BLOCK ratchets cleared) are all met.**

---

## Ratchet Status After Wave A

| Ratchet | Before | After |
|---|---|---|
| apps_* direct infra access | BLOCK (3 file-scan) | BLOCK (3) — Wave B target |
| UWG write bypass | COMPLIANT | COMPLIANT |
| zero-caller infra | **BLOCK** | **COMPLIANT** ✅ |
| not on L0-L6 spine | **BLOCK** | **COMPLIANT** ✅ |
| mixed wrapped/raw usage | ACCEPTED | ACCEPTED |
| duplicated adapters | ACCEPTED | ACCEPTED |

The `apps_* direct infra access` ratchet (3 google-import file-scan violations in
`llm_judge.py`, `provider_registry.py`, `dependencygraph_validator.py`) remains BLOCK —
this is the Wave B target (R-B1, R-B2) and R-C1 (HITL-gated).

---

## Wave A Clean Completion Confirmation

- [x] R-A1 executed: `agentic_core/cache/core/redis_cache_client.py` removed from `_APPROVED_ADAPTER_PATHS`
- [x] R-A2 executed: `agentic_core/L4_state/utils/memory/blob_storage_provider.py` removed from `_APPROVED_ADAPTER_PATHS`
- [x] ADG rebuilt: `adg_indexed_04112026_1631.sqlite`
- [x] Views rematerialised: `materialize_infra_views()` executed against fresh SQLite
- [x] Scorecard updated: `artifacts/infra_wiring_scorecard.json` timestamp `2026-04-11T20:41:58Z`
- [x] `v_p1_zero_caller_infra = 0` ✅
- [x] `v_p1_not_on_spine = 0` ✅
- [x] `violations.p1 = 0` ✅
- [x] `compliance_score = 100%` ✅
- [x] No production runtime files modified
- [x] No files deleted from disk
- [x] No CI ratchet ceilings changed
- [x] No Wave B/C/D items touched

**Wave A is cleanly complete.**

---

## Next Prompt Target: Wave B Only

Wave B repairs (from `docs/reports/plans/infra_wiring_repair_plan.md`):

- **R-B1** — `agentic_core/evaluation/judges/llm_judge.py`: Replace lazy `import google.generativeai` in `GeminiJudge._get_client()` with `create_vertex_client()` call via `infrastructure/sdks_mcps`
- **R-B2** — `agentic_core/evaluation/judges/provider_registry.py`: Same reroute for `GeminiJudgeProvider._get_client()` + pre-built client injection in `create_default_registry()`
- **R-B3** — `agentic_core/knowledge/enrichment/semantic_enricher.py`: Replace lazy `from openai import OpenAI` in `_init_default_client()` with `create_openai_client()` via sanctioned seam (prerequisite: verify sync vs async interface before applying)

Wave B prerequisite: confirm `SemanticEnricher` sync/async interface before R-B3. R-B1 and R-B2 have no open prerequisites.

**Do not implement R-C1 (HITL required), R-C2, R-C3, R-C4, or any Wave D item in Wave B.**
