---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-cache-followon-deferred-c7d3a1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-cache-followon-deferred-c7d3a1.md'
source_sha256: bf13c5f416e11eeb40e2d5c1b28cf8117a38895c3e56f03180f86b626c9fe77f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps-rg-cache-followon-deferred-c7d3a1

> **Status: COMPLETED 2026-05-05**  
> All 3 waves, 3 phases implemented. 21 regression tests still passing. CI smoke gate green.

## Purpose

Captures deferred scope items identified during execution of
`apps-rg-l0-cache-deferred-scope-b8e2f4` (COMPLETED 2026-05-05). These items were
explicitly descoped to keep the plan bounded. **This plan is a holding document only.**

Parent plan: `apps-rg-l0-cache-deferred-scope-b8e2f4`  
Parent status: COMPLETED 2026-05-05

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | W1.P1 | Wire `check_r1b_warmup_smoke` into CI runner | ~4k | `run_contract_gates.py` pattern understood | ✅ DONE | Gate `RG-W3` appears in `run_contract_gates.py` assurance group; `python ops_scripts/ci/run_contract_gates.py` executes it |
| W2 | W2.P1 | Pair discovery from `route_registry.yaml` | ~8k | `route_registry.yaml` contains or can reference known company/role pairs | ✅ DONE | `warm_r1b_cache.py --from-registry` reads pairs from app route registry rather than hardcoded TOP_PAIRS |
| W3 | W3.P1 | `cache.similarity_score` on R1B hit span | ~5k | R1B recall returns similarity score alongside payload | ✅ DONE | `apps_rg.cache.r1b.check` span carries `cache.similarity_score` float attribute on hit path; miss path omits attribute |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Register RG-W3 gate in CI runner | `ops_scripts/ci/run_contract_gates.py` | `check_r1b_warmup_smoke.py` exists but is not wired into the contract gate runner; will not fire on CI unless registered | ~4k | ✅ DONE — added to assurance group after NP3; advisory; `R1B_WARMUP_SMOKE_FAIL_CLOSED=1` for strict mode |
| W2.P1 | Route-registry pair discovery | `tools/apps_rg/warm_r1b_cache.py`, `apps_rg/config/warmup_pairs.yaml` (new) | W3.P1 spec stated "reads route_registry.yaml for known pairs"; current impl uses hardcoded TOP_PAIRS; registry-driven pairs would auto-update as routes evolve | ~8k | ✅ DONE — `warmup_pairs.yaml` + `_load_from_registry()` helper + `--from-registry` CLI flag; TOP_PAIRS fallback retained |
| W3.P1 | Similarity score on R1B hit span | `apps_rg/__main__.py`, `apps_rg/cache/r1b_adapter.py` | `check_r1b_for_apps_rg` currently returns the payload dict or None; the raw similarity score from `SemanticCacheManager.recall` is not propagated back to the caller so `__main__.py` cannot set `cache.similarity_score` on the span | ~5k | ✅ DONE — score embedded as `_cache_similarity_score` in returned payload; `__main__.py` sets `cache.similarity_score` attribute on R1B hit span |

---

## Deferred Scope Register

### DS-1: `check_r1b_warmup_smoke` not wired into CI runner

**Source:** W3.P2 completion — gate written but not registered  
**Detail:** `ops_scripts/ci/check_r1b_warmup_smoke.py` exists and passes locally (0 findings) but is not referenced in `ops_scripts/ci/run_contract_gates.py`. The gate will never fire automatically on CI pushes until wired in.  
**Target wave:** W1.P1  
**Priority:** P2

---

### DS-2: Warm-up script uses hardcoded TOP_PAIRS instead of route_registry.yaml

**Source:** W3.P1 spec stated "reads route_registry.yaml for app + known role/company pairs"  
**Detail:** The delivered script embeds a static `TOP_PAIRS` list of 20 pairs. The original intent was to derive pairs from the app's `route_registry.yaml` (or a companion `warmup_pairs.yaml`) so the list evolves with the app config rather than requiring code changes.  
**Target wave:** W3.P1  
**Priority:** P4

---

### DS-3: R1B hit OTEL span missing `cache.similarity_score` attribute

**Source:** W5.P2 spec — "add `cache.similarity_score` attribute on hit path"  
**Detail:** `apps_rg.cache.r1b.check` span is emitted with `cache.layer` and `cache.result` but does not carry the raw similarity score. `check_r1b_for_apps_rg` returns payload-or-None; the similarity value from `SemanticCacheManager.recall` is consumed inside the adapter and not surfaced. Fix requires: (1) return `(payload, similarity)` tuple from `recall_output_for_intent`; (2) propagate through `check_r1b_for_apps_rg`; (3) set `cache.similarity_score` on the span in `__main__.py`.  
**Target wave:** W3.P1  
**Priority:** P3

---

## Non-Goals

- No changes to R1A adapter, stamp format, or migration script
- No changes to HOP pipeline, L2 recipe, or embedding models
- No retroactive reprocessing of existing run artifacts
- No new cache layers beyond R1A/R1B

## Success Criteria (per wave)

- W1: `python ops_scripts/ci/run_contract_gates.py` executes `RG-W3` gate
- W2: `--from-registry` flag reads pairs from app config; TOP_PAIRS retained as fallback
- W3: `cache.similarity_score` visible on R1B hit spans in `otel_mcp`; miss spans unaffected
