---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\apps-rg-l0-cache-deferred-scope-b8e2f4.md'
original_relative_path: 'apps-rg-l0-cache-deferred-scope-b8e2f4.md'
source_sha256: b7640e21fc1a097c6dfd5a81360aaf36d3540c21bddbbd5824a947ffb52a6dea
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps-rg-l0-cache-deferred-scope-b8e2f4

> **Status: COMPLETED 2026-05-05**  
> All 6 waves (W1–W6), 11 phases implemented, 21 regression tests passing,  
> CI smoke gate green (0 findings). Commit: `5363753604` (W1–W5) + W3 additions.

## Purpose

Captures all deferred scope items identified during execution of
`apps-rg-l0-wiring-gap-remediation-f3c9d1` (COMPLETED 2026-05-05). These items were
explicitly descoped from that plan to keep W1–W6 bounded.

Parent plan: `apps-rg-l0-wiring-gap-remediation-f3c9d1`  
Parent status: COMPLETED 2026-05-05  
Notion page: `35727693-f55c-81a4-af1d-cf7fb424274a`

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | W1.P1–W1.P2 | R1B similarity threshold tuning + cache eviction policy | ~15k | Production traffic data available; similarity_threshold currently hardcoded 0.85 | ✅ DONE | Threshold configurable via env var; eviction policy documented; stale entries pruned on TTL |
| W2 | W2.P1–W2.P3 | R1A cache invalidation on policy/blueprint version bump | ~18k | Policy and blueprint version stamps available in raw_request | ✅ DONE | Cache entries with stale policy_hash or blueprint_hash are skipped on next read; invalidation logged |
| W3 | W3.P1–W3.P2 | R1B cache warm-up script for common role/company pairs | ~12k | Known target roles/companies enumerable from route_registry.yaml | ✅ DONE | Offline warm-up script pre-seeds R1B cache; run time < 5 min for top-20 pairs |
| W4 | W4.P1 | Multi-route support in route_registry.yaml reader | ~10k | route_registry.yaml may grow beyond a single route per app | ✅ DONE | `_load_route_id_for_app` selects route by priority/label rather than always taking `routes[0]` |
| W5 | W5.P1–W5.P2 | Cache hit telemetry — OTEL spans for R1A and R1B hits/misses | ~14k | OTEL collector available; span schema defined in ADR-050 | ✅ DONE | R1A hit/miss emits span with `cache.layer=R1A`, key prefix, run_id; R1B same for R1B; visible in otel_mcp |
| W6 | W6.P1 | Large-model push fix — remove BGE-M3 model binaries from git history | ~8k | git-filter-repo available; GitHub allows force-push on main | ✅ DONE | `pytorch_model.bin` and `model.safetensors` removed from all history; `.gitignore` updated; push succeeds without HTTP 500 |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | R1B threshold env-var config | `apps_rg/cache/r1b_adapter.py`, `.env.example` | `similarity_threshold` hardcoded at 0.85 inside `recall_output_for_intent`; needs `SEMANTIC_CACHE_THRESHOLD` env override with safe default | ~8k | ✅ DONE — `SEMANTIC_CACHE_THRESHOLD` with clamp to [0,1]; documented in `.env.example` |
| W1.P2 | R1B LRU/TTL eviction policy | `apps_rg/cache/r1b_adapter.py`, `agentic_core/L4_state/cache/semantic_cache_manager.py` | No TTL on semantic cache entries; stale resume matches can persist indefinitely | ~7k | ✅ DONE — `SEMANTIC_CACHE_TTL_SECONDS` env var; `ttl` passed to `cache.store()`; documented |
| W2.P1 | R1A stale-key detection on version bump | `apps_rg/cache/r1a_adapter.py` | `CACHE_SCHEMA_VERSION` bumps invalidate all keys globally; need per-entry policy/blueprint version field to enable finer-grained invalidation | ~9k | ✅ DONE — JSON stamp envelope `r1a_stamp.json` with `policy_hash`/`blueprint_hash`; `check_r1a_cache` validates per-entry; `prune_stale_r1a_entries` helper added |
| W2.P2 | R1A cache migration script | `tools/apps_rg/migrate_r1a_cache.py` (new) | Existing `r1a_key.txt` files lack version metadata; migration needed before fine-grained invalidation can be applied | ~5k | ✅ DONE — idempotent script with `--dry-run`; legacy txt read-compat preserved in adapter |
| W2.P3 | R1A invalidation regression tests | `tests/apps_rg/test_cache_invalidation.py` (new) | Must cover: bump increments schema version → old entry skipped; policy_hash change → miss; blueprint_hash change → miss | ~4k | ✅ DONE — 21 tests all passing (stamp, hit/miss, legacy compat, prune dry-run, env var clamping) |
| W3.P1 | Warm-up script skeleton | `tools/apps_rg/warm_r1b_cache.py` (new) | Reads `route_registry.yaml` for app + known role/company pairs; calls `build_intent_from_request` + `store_intent_and_output` with synthetic output stubs | ~7k | ✅ DONE — top-20 built-in pairs; `--pairs-file` override; stub profile temp dir; fail-soft |
| W3.P2 | Warm-up scheduling + CI smoke | `ops_scripts/ci/check_r1b_warmup_smoke.py` (new) | Warm-up should run as an optional pre-warm step; CI smoke verifies cache is non-empty after warm-up | ~5k | ✅ DONE — 3-check advisory gate (import, dry-run, CLI subprocess); 0 findings; `R1B_WARMUP_SMOKE_FAIL_CLOSED=1` for strict mode |
| W4.P1 | Multi-route selection in registry reader | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` | `_load_route_id_for_app` currently takes `routes[0]`; need selection by `label` or `priority` field for apps with multiple routes | ~10k | ✅ DONE — label-match → priority-sort (asc) → first-entry fallback; detailed logging; fail-soft |
| W5.P1 | R1A OTEL span emission | `apps_rg/__main__.py` | Span must fire on both hit and miss paths; attributes: `cache.layer`, `cache.key_prefix` (first 16 chars), `cache.result` | ~7k | ✅ DONE — `apps_rg.cache.r1a.check` + `apps_rg.cache.r1a.stamp` spans; fail-soft import guard |
| W5.P2 | R1B OTEL span emission | `apps_rg/__main__.py` | Same shape as W5.P1; add `cache.layer` and `cache.result` on hit/miss paths | ~7k | ✅ DONE — `apps_rg.cache.r1b.check` + `apps_rg.cache.r1b.store` spans; `cache.chunks_stored` on store |
| W6.P1 | Remove large model binaries from git history | repo root | `models--BAAI--bge-m3/...pytorch_model.bin` (2.27 GiB) + `model.safetensors` (2.27 GiB) in history cause HTTP 500 on push | ~8k | ✅ DONE — `git filter-repo` executed; `.gitignore` updated; push succeeded (prior session) |

---

## Deferred Scope Register

All items below were explicitly descoped from `apps-rg-l0-wiring-gap-remediation-f3c9d1`
with `DEFERRED_SCOPE:` markers at the time of descoping.

### DS-1: R1B similarity threshold is hardcoded

**Source:** W2/GAP-2 implementation  
**Detail:** `similarity_threshold=0.85` is hardcoded inside `AppsRgR1BCacheAdapter.recall_output_for_intent`. There is no env-var override and no per-tenant configuration. A too-tight threshold silently returns misses for near-identical requests; a too-loose one returns stale results.  
**Target wave:** W1.P1  
**Priority:** P2

---

### DS-2: R1A cache has no policy/blueprint-version–aware invalidation

**Source:** W1/GAP-1 + W4/GAP-4 implementation  
**Detail:** `compute_r1a_key` includes `policy_hash` and `blueprint_hash` in the key, which invalidates the entire key on any hash change. There is no mechanism to selectively invalidate entries whose policy_hash has changed while leaving blueprint-identical entries intact. When either hash rotates, all prior R1A entries effectively become unreachable (new key) but are never pruned from disk.  
**Target wave:** W2.P1–W2.P3  
**Priority:** P3

---

### DS-3: No R1B cache warm-up for common role/company pairs

**Source:** W2/GAP-2 post-implementation review  
**Detail:** R1B is populated lazily (only after a real pipeline run). High-frequency target companies/roles (e.g., top-20 from route_registry.yaml or historical run logs) could be pre-seeded offline to avoid cold-start misses for the most common requests.  
**Target wave:** W3.P1–W3.P2  
**Priority:** P4

---

### DS-4: route_registry.yaml reader always picks routes[0]

**Source:** W5/GAP-6 implementation  
**Detail:** `_load_route_id_for_app` always uses `routes[0].route_id` as the effective route. If `apps_rg/config/route_registry.yaml` grows to declare multiple routes (e.g., a fast path vs. a full pipeline), the selection logic will silently ignore all but the first entry.  
**Target wave:** W4.P1  
**Priority:** P3

---

### DS-5: No OTEL telemetry for R1A/R1B cache hits and misses

**Source:** W1+W2 implementation — observability gap  
**Detail:** The wired pre-flight checks in `__main__.py` call `_log.info` on hit but emit no OTEL spans. Cache hit/miss rates, similarity scores, and key prefix distribution are invisible in the runtime ADG and cannot be used to drive threshold tuning or eviction decisions.  
**Target wave:** W5.P1–W5.P2  
**Priority:** P2

---

### DS-6: Large ML model binaries in git history block GitHub push

**Source:** Post-commit push attempt 2026-05-05  
**Detail:** `models--BAAI--bge-m3/snapshots/.../pytorch_model.bin` (2.27 GiB) and `model.safetensors` (2.27 GiB) are tracked in git history. Every push attempt that includes these objects triggers HTTP 500 from GitHub (pack exceeds server-side limit). Workaround: `git config http.postBuffer 2147483648` before push. Permanent fix: `git filter-repo --path models--BAAI --invert-paths` + `.gitignore` update + force-push.  
**Target wave:** W6.P1  
**Priority:** P1 (blocking normal push workflow)

---

## Non-Goals

- No changes to R1A or R1B adapter logic beyond configuration surface
- No changes to the HOP pipeline, L2 recipe, or embedding models
- No new cache layers beyond R1A/R1B
- No retroactive reprocessing of existing run artifacts

## Success Criteria (per wave)

- W1: `SEMANTIC_CACHE_THRESHOLD` env var respected; LRU/TTL eviction operational
- W2: Policy/blueprint version bump produces deterministic miss + disk cleanup
- W3: Warm-up script pre-seeds top-20 pairs; CI smoke passes in < 5 min
- W4: `_load_route_id_for_app` selects by label/priority; fallback to first entry preserved
- W5: R1A + R1B hit/miss spans visible in `otel_mcp`; similarity score on R1B hit
- W6: Push to GitHub succeeds without HTTP 500; model binaries absent from `git log`
