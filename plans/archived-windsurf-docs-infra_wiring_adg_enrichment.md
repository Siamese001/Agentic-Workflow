---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\infra_wiring_adg_enrichment.md'
original_relative_path: 'infra_wiring_adg_enrichment.md'
source_sha256: f0ba34ae8d3ef79c485482e9a24f6ab0a0e2a889c323e2de904337437b4c7e89
recovered_status: LOST_RECOVERED
last_commit: '3126c63b013'
last_commit_date: '2026-04-11 19:05:02 -0400'
created_date: '2026-04-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Infrastructure Wiring ADG Enrichment — Phase 2
**Generated:** 2026-04-11
**Based on:** Phase 1 ownership matrix (`infra_ownership_matrix.md`, 2026-04-11)
**Scope:** Detection-layer changes only. No runtime callers patched. No CI ratchets added.

---

## A. Executive Summary

Phase 2 closes the detection gaps identified in Phase 1. Three unregistered surfaces
(Neo4j, Prometheus, vLLM/aiohttp) are now visible to the scanner and ADG views. Four
sanctioned-vs-approved coverage gaps are closed. One new ADG view
(`v_p1_raw_http_outside_seam`) makes raw HTTP clients outside the approved seam visible.
Provider bypass detection (google imports) is added to the file scanner.

**After `generate_full_adg.py` runs** the following new signals will surface:
- `v_p1_zero_caller_infra` — 1 new entry: `neo4j_store.py` (zero ADG callers confirmed)
- `v_p1_raw_http_outside_seam` — 1 new entry: `optimized_vllm_client.py` (raw aiohttp in L3)
- `v_p0_provider_bypass` — potentially 2 new entries if ADG captures lazy google imports in
  `llm_judge.py` / `provider_registry.py` (depends on ADG lazy-import edge coverage)

No P0 violations introduced. All new detections are P1 (hardening).

---

## B. Detection Gaps Fixed

| Gap (Phase 1 §E) | Fix Applied | File Changed |
|---|---|---|
| Neo4j unregistered in FORBIDDEN_IMPORTS | Added `"import neo4j"`, `"from neo4j"` | `infra_wiring_scan.py` |
| Neo4j unregistered in _RAW_INFRA_PACKAGES | Added `"neo4j"` | `infra_wiring_views.py` |
| Neo4j not in _APPROVED_ADAPTER_PATHS (no P1 visibility) | Added `neo4j_store.py` — tracked; zero-caller P1 will fire | `infra_wiring_views.py` |
| Neo4j not in SANCTIONED_ADAPTER_FILES | Added `neo4j_store.py` with EXPERIMENTAL_ISOLATED comment | `infra_wiring_scan.py` |
| Prometheus unregistered in FORBIDDEN_IMPORTS | Added `"import prometheus_client"`, `"from prometheus_client"` | `infra_wiring_scan.py` |
| Prometheus unregistered in _RAW_INFRA_PACKAGES | Added `"prometheus_client"` | `infra_wiring_views.py` |
| Prometheus not in _APPROVED_ADAPTER_PATHS | Added `prometheus_metrics.py` (de-facto L6 adapter) | `infra_wiring_views.py` |
| Prometheus not in SANCTIONED_ADAPTER_FILES | Added `prometheus_metrics.py`, `metrics_server.py` | `infra_wiring_scan.py` |
| vLLM/aiohttp unregistered in FORBIDDEN_IMPORTS | Added `"import aiohttp"`, `"from aiohttp"` | `infra_wiring_scan.py` |
| vLLM/aiohttp unregistered in _RAW_INFRA_PACKAGES | Added `"aiohttp"` | `infra_wiring_views.py` |
| vLLM/aiohttp not in SANCTIONED_ADAPTER_FILES | Added `optimized_vllm_client.py` (UNDER_REVIEW) | `infra_wiring_scan.py` |
| No ADG view for raw HTTP outside seam | New view `v_p1_raw_http_outside_seam` (P1-15) | `infra_wiring_views.py` |
| OTel canonical adapter path wrong | Added `open_telemetry_tracing_adapter_util.py` to _APPROVED_ADAPTER_PATHS | `infra_wiring_views.py` |
| `blob_storage_provider.py` in SANCTIONED but not APPROVED | Added to _APPROVED_ADAPTER_PATHS | `infra_wiring_views.py` |
| `cache/core/redis_cache_client.py` in SANCTIONED but not APPROVED | Added to _APPROVED_ADAPTER_PATHS | `infra_wiring_views.py` |
| Provider bypass detection missing google imports | Added `"import google"`, `"from google"` | `infra_wiring_scan.py` |
| `v_p1_mis_layered_infra` missing prometheus + neo4j checks | Added layer checks for both | `infra_wiring_views.py` |
| `total_infra_surfaces` hardcoded as 10 | Updated to 13 in scorecard generator and artifact | `infra_wiring_scan.py`, `infra_wiring_scorecard.json` |

---

## C. Files Changed

| File | Change Type | Lines Affected |
|---|---|---|
| `tools/generate/infra_wiring_views.py` | Added 3 packages to `_RAW_INFRA_PACKAGES` | Lines 15–29 |
| `tools/generate/infra_wiring_views.py` | Added 5 entries to `_APPROVED_ADAPTER_PATHS` | Lines 57–63 |
| `tools/generate/infra_wiring_views.py` | Added 2 checks to `_VIEW_P1_MIS_LAYERED_INFRA` | Lines 392–395 |
| `tools/generate/infra_wiring_views.py` | New `_VIEW_P1_RAW_HTTP_OUTSIDE_SEAM` view (P1-15) | Lines 466–491 |
| `tools/generate/infra_wiring_views.py` | HTTP subset computation in `materialize_infra_views()` | Lines 540–543 |
| `tools/generate/infra_wiring_views.py` | New view added to drop/create/count sequences | Lines 569, 625, 659 |
| `tools/generate/infra_wiring_views.py` | `p1_views` list updated in `enrich_and_report()` | Line 695 |
| `tools/generate/infra_wiring_views.py` | Count string updated ("14 checks" → "15 checks") | Line 679 |
| `ops_scripts/ci/infra_wiring_scan.py` | Added 8 new patterns to `FORBIDDEN_IMPORTS` | Lines 36–45 |
| `ops_scripts/ci/infra_wiring_scan.py` | Added 4 files to `SANCTIONED_ADAPTER_FILES` | Lines 90–94 |
| `ops_scripts/ci/infra_wiring_scan.py` | `total_infra_surfaces` 10 → 13 | Line 330 |
| `ops_scripts/ci/infra_wiring_scan.py` | `approved_active` formula updated to base-13 | Line 331 |
| `ops_scripts/ci/infra_wiring_scan.py` | Added `v_p1_raw_http_outside_seam` to fallback view_names | Line 242 |
| `artifacts/infra_wiring_scorecard.json` | Phase 2 baseline: 13 surfaces, new ratchet, PENDING_REBUILD state | All |

**Files NOT changed (runtime callers — deferred to Phase 3):**
- `agentic_core/L4_state/reasoning/retrieval_layers.py`
- `agentic_core/knowledge/enrichment/semantic_enricher.py`
- `agentic_core/evaluation/judges/llm_judge.py`
- `agentic_core/evaluation/judges/provider_registry.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py`

---

## D. New Relations / Views Added

### `v_p1_raw_http_outside_seam` (NEW — P1-15)

Detects raw aiohttp/httpx/requests imports outside the approved HTTP seam (tools/mcp/enhanced_http_server.py
and agentic_core/gateway/). The vLLM client (`optimized_vllm_client.py`) is intentionally visible here —
it is UNDER_REVIEW, not approved.

```sql
-- Key predicate (simplified):
WHERE e.relation_type = 'imports'
  AND n_dst.adg_name IN ({http_adg_names})  -- aiohttp, httpx, requests ADG nodes
  AND n_src.resolved_path NOT LIKE 'tools/%'
  AND n_src.resolved_path NOT LIKE 'infrastructure/%'
  AND n_src.resolved_path NOT LIKE 'apps_shared/%'
  AND n_src.resolved_path NOT LIKE 'tests/%'
  AND n_src.resolved_path NOT LIKE '%api_gateway_integration%'
```

### `v_p1_mis_layered_infra` (UPDATED — added 2 checks)

```sql
-- Phase 2 additions:
OR (n.resolved_path = 'agentic_core/L6_observability/utils/metrics/prometheus_metrics.py' AND n.layer != 'L6')
OR (n.resolved_path = 'agentic_core/L4_state/enforcement/neo4j_store.py' AND n.layer != 'L4')
```

### `v_p0_provider_bypass` (UNCHANGED — already covers agentic_core/evaluation/)

The view already excludes only `infrastructure/sdks_mcps/`, `tools/`, `system_learning/`,
`agentic_core/embeddings/`. `agentic_core/evaluation/` is NOT excluded. Whether it fires
depends on whether the ADG captures lazy method-body imports as `imports` edges. The file
scanner now catches `from google` / `import google` at any indentation level (via `.strip()`).

---

## E. Before/After Count Deltas

| Metric | Before (Phase 1) | After (Phase 2 — pre-ADG-rebuild) | After (Phase 2 — post-ADG-rebuild, expected) |
|---|---|---|---|
| `_RAW_INFRA_PACKAGES` count | 8 | 11 | 11 |
| `FORBIDDEN_IMPORTS` patterns | 16 | 24 | 24 |
| `_APPROVED_ADAPTER_PATHS` count | 9 | 14 | 14 |
| `SANCTIONED_ADAPTER_FILES` count | 19 | 23 | 23 |
| ADG views total | 14 | 15 | 15 |
| `total_infra_surfaces` in scorecard | 10 | 13 | 13 |
| `v_p1_zero_caller_infra` | 0 | 0 (PENDING_REBUILD) | **≥1** (`neo4j_store.py`) |
| `v_p1_raw_http_outside_seam` | N/A | N/A (PENDING_REBUILD) | **≥1** (`optimized_vllm_client.py`) |
| `v_p0_provider_bypass` | 0 | 0 (PENDING_REBUILD) | **≥0** (depends on ADG lazy-import edges) |
| `v_p1_mis_layered_infra` | 0 | 0 (PENDING_REBUILD) | 0 (prometheus and neo4j ARE in correct layers) |
| P2 mixed usage ceiling | 3 | 3 (ACCEPTED, unchanged) | May increase if neo4j/prometheus create new mixed paths |

---

## F. Validation Queries

Run these against the ADG SQLite after `python tools/generate_full_adg.py`:

```sql
-- 1. All infra surfaces now tracked (raw packages in ADG)
SELECT DISTINCT adg_name, identity_kind
FROM nodes
WHERE adg_name IN (
  'ADG::Symbol::neo4j', 'ADG::Symbol::prometheus_client', 'ADG::Symbol::aiohttp',
  'ADG::Symbol::redis', 'ADG::Symbol::chromadb', 'ADG::Symbol::openai'
)
ORDER BY adg_name;

-- 2. Raw HTTP clients outside approved seam
SELECT consumer_file, consumer_layer, import_symbol, import_line
FROM v_p1_raw_http_outside_seam
ORDER BY consumer_layer, consumer_file;

-- 3. Adapters with zero callers (should show neo4j_store.py)
SELECT adapter_file, caller_count
FROM v_p1_zero_caller_infra
ORDER BY caller_count;

-- 4. Provider bypass in non-exempt agentic_core paths
SELECT consumer_file, consumer_layer, import_symbol, import_line
FROM v_p0_provider_bypass
WHERE consumer_file LIKE 'agentic_core/%'
ORDER BY consumer_file;

-- 5. All infra importers that are NOT in approved adapter paths (raw consumers)
SELECT DISTINCT n_src.resolved_path, n_src.layer, n_dst.adg_name
FROM edges e
JOIN nodes n_src ON e.src_id = n_src.id
JOIN nodes n_dst ON e.dst_id = n_dst.id
WHERE e.relation_type = 'imports'
  AND n_dst.adg_name IN (
    'ADG::Symbol::neo4j', 'ADG::Symbol::prometheus_client', 'ADG::Symbol::aiohttp'
  )
ORDER BY n_dst.adg_name, n_src.resolved_path;

-- 6. Sanctioned-vs-approved gap check (should return 0 rows after Phase 2)
-- Lists approved adapter paths whose ADG module node exists but has zero callers
-- AND is NOT in process-boundary list
SELECT adapter_file, caller_count
FROM v_p1_zero_caller_infra
WHERE adapter_file NOT IN (
  'infrastructure/sdks_mcps/__init__.py',
  'tools/mcp/enhanced_http_server.py',
  'agentic_core/L4_state/utils/memory/canonical_store.py',
  'agentic_core/L3_orchestration/reasoning/engines/sovereign_redis_orchestrator.py',
  'apps_shared/data_adapters/repo_signal_adapter.py'
);

-- 7. Mis-layered adapter check (prometheus must be L6, neo4j must be L4)
SELECT adapter_file, actual_layer FROM v_p1_mis_layered_infra;
```

---

## G. Remaining Ambiguities (Still Require Architecture Decision)

These are unchanged from Phase 1 §F — Phase 2 made them **visible** but did not resolve them:

1. **Neo4j (§F1)** — zero callers confirmed; broken guard pattern documented. Decision required:
   deprecate (add to FORBIDDEN as hard-block) or formalize with real optional-dependency guard.
   **Next step**: after ADG rebuild, `v_p1_zero_caller_infra` will confirm the zero-caller state.

2. **vLLM/aiohttp in L3 (§F2)** — `optimized_vllm_client.py` now appears in `v_p1_raw_http_outside_seam`.
   Decision required: add to `_APPROVED_ADAPTER_PATHS` (formal approval) or remove raw aiohttp
   and route via `enhanced_http_server.py`. The UNDER_REVIEW comment in SANCTIONED_ADAPTER_FILES
   is a bridge state — not approval.

3. **`agentic_core/evaluation/` provider exemption (§F3)** — file scanner now detects `from google`
   in `llm_judge.py` and `provider_registry.py` (lazy imports caught via `.strip()`). Whether to
   add `agentic_core/evaluation/` to `_PROVIDER_EXEMPT_PREFIXES` or require routing via
   `create_vertex_client()` remains an open architecture decision. Currently: fail-closed (detected).

4. **`infrastructure/sdks_mcps` migration completion (§F4)** — stub classes still empty `pass`.
   No Phase 2 change possible without knowing migration completion timeline.

5. **Feature flag convergence (§F5)** — two stores; no external infra dependency; no Phase 2
   action possible without knowing intended relationship.

6. **Prometheus `apps_tracing_mixin.py` OTel bypass (§F7)** — `apps_shared/mixins/apps_tracing_mixin.py`
   still directly imports `from opentelemetry import trace`. Now that `open_telemetry_tracing_adapter_util.py`
   is in `_APPROVED_ADAPTER_PATHS`, the v_p2_mixed_usage view may surface this as a new mixed-usage
   instance after ADG rebuild.

---

*Stop condition reached — Phase 2 ADG detection enrichment complete. ADG rebuild required to
surface new P1 signals. Runtime caller repairs and CI ratchets deferred to Phase 3.*
