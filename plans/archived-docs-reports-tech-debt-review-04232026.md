---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\tech-debt-review-04232026.md'
original_relative_path: 'tech-debt-review-04232026.md'
source_sha256: 157c3d29c2997978e79e0ce577c67fb357478759ec6573acfafc247c6a74afbc
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Technical Debt Review — Repo-Wide (ADG-Driven)

**Date:** 2026-04-23
**ADG snapshot:** `adg_indexed_04232026_0925.sqlite` (SQLite canonical) + `adg_graph_04232026_0925.sqlite` (graph projection)
**Graph stats:** 74,826 nodes · 552,727 edges · schema v1.0
**Backend used:** SQLite (canonical truth) + graph projection
**ADG Provenance:** backend=sqlite, snapshot=adg_indexed_04232026_0925.sqlite
**Raw evidence:** `artifacts/adg/tech_debt_review_04232026.txt`

> All findings are traceable through the Zero-Loss Propagation Pipeline
> (catch site → antipattern edge → ownership bridge → 5 ADG Surfaces → ranked hotspot).
> Every hotspot row intersects at least one of the 5 Surfaces (Execution / Write / Security / State / Observability).

---

## 1. Executive Snapshot

| Metric | Count | Notes |
|---|---:|---|
| Total violations | **4,467** | 9 CRITICAL, 17 HIGH, 4,441 LOW |
| P0 `write_bypass_uwg` rows | 3 | mutations outside Unified Write Gateway |
| `mv_new_write_bypass_paths` (critical severity) | **1,900** | mkdir / copy / state mutations bypassing UWG |
| `mv_authority_boundary_breaches` | 150 | L6 → L0/L1 gravity-leak imports |
| `mv_gateway_bypass_paths` | 23 | raw `aiohttp`, `boto3`, `urllib` outside provider seam |
| `mv_exemptions_near_critical_paths` | 1,827 | guardian exemptions sitting on high-criticality code |
| `mv_provider_surface_sprawl` | 17 | ad-hoc provider imports scattered across layers |
| `unused_import` edges | 7,751 | latent bloat |
| Duplicated adapters (`v_p2_duplicated_adapters`) | 3 | remediable duplication |

**Headline risks (ranked by structural impact):**
1. `agentic_core/runtime/contracts/lifecycle_trace_contract.py` — fan-in **114,121**, 2,095 direct downstreams. Any bug = system-wide blast.
2. L5 safety-plane healers (`hierarchy_healer.py`, `FileClassificationAgent.py`, `LocationHealerAgent.py`) — dense violation clusters on ×2.0 layer multiplier.
3. Write-path sovereignty eroding — 1,900 critical-severity writes bypass UWG, mostly in `L4_state/utils/memory/` and `L3_orchestration/exit_control/`.
4. L6 → L0 reverse-gravity imports — observability writes poisoning routing config (150 edges, concentrated in `L6_observability/__init__.py`).
5. Provider seam leaks — direct `aiohttp` / `boto3` / `urllib` in L3 / L4 / L_APP instead of through `L2_execution/utils/providers.py`.

---

## 2. Violations — Distribution

| Severity | Class | Category | Count |
|---|---|---|---:|
| CRITICAL | hygiene | `violates` | 9 |
| HIGH | hygiene | `antipattern` | 17 |
| LOW | hygiene | `antipattern` | 4,441 |

**Reading:** The CRITICAL+HIGH band (26 total) is tractable and should be the week-one target. The 4,441 LOW band is chronic antipattern drift (broad `except`, `log_and_swallow`, `silent_swallow`, `return_none_swallow`) and drives the guardian-exemptions-near-critical-paths problem.

**Anti-pattern category (from `mv_exemptions_near_critical_paths`):**
- `broad_exception_catch` — dominant in `tools/eval/retrieval_benchmark.py`
- `silent_exception_swallow` — same file (lines 1082, 1363, 1395)
- `log_and_swallow` — `_ssot_meta_learning.py` has 8 consecutive instances (lines 285–447)

---

## 3. Top 15 Debt-Concentration Files

| CRIT | HIGH | LOW | TOT | File |
|---:|---:|---:|---:|---|
| 1 | 0 | 46 | 47 | `tools/eval/retrieval_benchmark.py` |
| 0 | 0 | 41 | 41 | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_reporting.py` |
| 0 | 0 | 35 | 35 | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_meta_learning.py` |
| 0 | 0 | 24 | 24 | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` |
| 0 | 0 | 20 | 20 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` |
| 0 | 0 | 19 | 19 | `tools/generate/reporting/reports.py` |
| 0 | 0 | 17 | 17 | `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` |
| 0 | 0 | 16 | 16 | `ops_scripts/ci/run_contract_gates.py` |
| 0 | 0 | 16 | 16 | `tools/generate/validation/gates.py` |
| 0 | 0 | 13 | 13 | `agentic_core/L4_state/enforcement/neo4j_store.py` |
| 0 | 0 | 13 | 13 | `agentic_core/L3_orchestration/reasoning/breadth_first_classifier.py` |
| 0 | 0 | 13 | 13 | `agentic_core/adg/applications/guardian_prioritizer.py` |

(Test files omitted — they are `L_TEST` tier and do not carry layer multipliers.)

---

## 4. Fan-In Hotspots (Blast Radius) — Top 10

Files every bug propagates through:

| Fan-in | File | Archetype |
|---:|---|---|
| **114,121** | `agentic_core/runtime/contracts/lifecycle_trace_contract.py` | CENTRAL_DEPENDENCY (asymmetric_connector) |
| 1,006 | `agentic_core/L0_routing/config/path_constants.py` | CENTRAL_DEPENDENCY (L0 ×2.0) |
| 449 | `agentic_core/__init__.py` | CENTRAL_DEPENDENCY |
| 260 | `agentic_core/L0_routing/config/__init__.py` | CENTRAL_DEPENDENCY (L0 ×2.0) |
| 255 | `tools/generate/validation/gates.py` | ORCHESTRATOR |
| 227 | `agentic_core/adg/contracts/schema_util.py` | CENTRAL_DEPENDENCY |
| 151 | `agentic_core/adg/extraction/static_scanner.py` | ORCHESTRATOR (fan-out 158) |
| 136 | `agentic_core/base_agents/SovereignBaseAgent.py` | CENTRAL_DEPENDENCY |
| 118 | `agentic_core/L2_execution/_agentic_core_smoke.py` | CENTRAL_DEPENDENCY |
| 109 | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | CENTRAL_DEPENDENCY (L5 ×2.0) |

**Immediate concern:** `lifecycle_trace_contract.py` is a single-point-of-failure at an almost unprecedented scale (fan-in > 100k). Every trace/span contract change cascades through 2,095 direct downstream modules and an estimated 2,694 at hop-2. Treat as frozen/Author-Gate-only.

---

## 5. Fan-Out Hotspots (Orchestrators) — Top 10

Files that hide downstream failures if they swallow exceptions:

| Fan-out | File | Layer |
|---:|---|---|
| 288 | `tests/unit/tools/generate/test_generate_full_adg_failfast.py` | L_TEST |
| 158 | `agentic_core/adg/extraction/static_scanner.py` | L_TOOLS |
| 157 | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | **L5** |
| 145 | `agentic_core/L6_observability/__init__.py` | **L6** |
| 139 | `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | **L5** |
| 134 | `tools/eval/retrieval_benchmark.py` | L_TOOLS |
| 132 | `agentic_core/adg/client/cli.py` | L_TOOLS |
| 127 | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | **L5** |
| 126 | `agentic_core/L3_orchestration/reasoning/engines/orchestrator_engine.py` | **L3** |
| 126 | `agentic_core/L1_cognition/utils/execution_util.py` | L1 |

**L5 safety-plane files with fan-out > 100 AND violation clusters are the highest-risk archetype in the system (SAFETY_GATEKEEPER on ×2.0 multiplier).**

---

## 6. Impact-Ranked Hotspots (Wave 1 Target List)

`impact = violations × (1 + log10(1+fan_in)) × layer_multiplier`

| LYR | VIO | FI | IMPACT | File | Wave |
|---|---:|---:|---:|---|:---:|
| L5 | 24 | 22 | **113.4** | `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | W1 |
| L5 | 20 | 24 | **95.9** | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | W1 |
| L5 | 17 | 10 | **69.4** | `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | W1 |
| L_TOOLS | 16 | 255 | 54.5 | `tools/generate/validation/gates.py` | W2 |
| L_TOOLS | 47 | 0 | 47.0 | `tools/eval/retrieval_benchmark.py` | W2 |
| L3 | 13 | 6 | 42.0 | `agentic_core/L3_orchestration/reasoning/breadth_first_classifier.py` | W1 |
| L_OPS | 41 | 0 | 41.0 | `ops_scripts/dev_tools/L0_routing_scripts/_ssot_reporting.py` | W3 |
| L5 | 12 | 3 | 38.5 | `agentic_core/L5_safety/reasoning/root_hygiene_healer.py` | W1 |
| L5 | 6 | 109 | 36.5 | `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | W1 |
| L5 | 8 | 9 | 32.0 | `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | W1 |
| L_TOOLS | 10 | 151 | 31.8 | `agentic_core/adg/extraction/static_scanner.py` | W2 |
| L0 | 5 | 103 | 30.2 | `agentic_core/L0_routing/types/guardian_contract_types.py` | W1 |
| L0 | 7 | 13 | 30.0 | `agentic_core/L0_routing/enforcement/execution_gateway.py` | W1 |
| L4 | 13 | 1 | 29.6 | `agentic_core/L4_state/enforcement/neo4j_store.py` | W2 |

**Wave proposal:** W1 = L0/L5 hotspots (×2.0), W2 = L3/L4 + high-fan-in L_TOOLS, W3 = L_OPS cleanup, W4 = test/file hygiene.

---

## 7. Architectural Structural Debt (beyond anti-patterns)

### 7.1 Write-path sovereignty erosion (1,900 CRITICAL rows — biggest structural risk)

`mv_new_write_bypass_paths` shows **1,900 critical-severity write operations bypassing the Unified Write Gateway (UWG)**, including:

- `agentic_core/L4_state/utils/memory/*` — `parent.mkdir`, `blob_storage_provider.py` S3 writes
- `agentic_core/L3_orchestration/exit_control/ledger_*` — `self._path.parent.mkdir`
- `agentic_core/L4_state/reasoning/retrieval_layers.py` — `persist_dir.mkdir`
- `apps_shared/integrations/runtime_hitl_integration.py` — runtime HITL ledger writes

**Impact:** Partial writes become corrupt system-of-record. `v_p0_write_bypass_uwg` surfaces 3 P0 rows but the severity=critical inventory is 1,900 — these should convert to P0 once UWG enforcement tightens.

### 7.2 Gateway bypass (provider seam leaks — 23 paths)

| Layer | Symbol | File |
|---|---|---|
| L3 | `aiohttp.ClientSession`, `aiohttp.ClientTimeout`, `aiohttp.TCPConnector` | `L3_orchestration/inference/qwen_vllm/*` |
| L3 | `urllib.parse.urlparse` | `L3_orchestration/reasoning/engines/source_*` |
| L4 | `urllib.parse.urlparse` | `L4_state/reasoning/CachedStateLedger.py` |
| L4 | `boto3.client` | `L4_state/utils/memory/blob_storage_provider.py`, `canonical_store.py` |
| L_APP | `urllib.request.Request` | `apps_lic/reasoning/enterprise_campaign_orchestrator.py` |
| L_APP | `urllib.parse.urlparse` | `apps_research/services/source_discovery_service.py` |

**Mitigation:** Route all of these through `agentic_core/L2_execution/utils/providers.py` (fan-out 226, already the provider seam) with a small adapter for aiohttp/boto3.

### 7.3 Authority boundary breaches (150 rows — gravity inversion)

**Pattern:** `L6_observability/__init__.py` and related L6 modules import from `L0_routing/config/path_constants.py` and `L0_routing/types/determinism_types.py`. This inverts layer gravity (higher → lower).

**Reading:** observability is depending on routing types — which means any L0 type change ripples into L6 and breaks trace/metric surfaces. Fix by publishing a minimal dependency-injection surface or mirroring required types into `L6_observability/types/`.

### 7.4 Manager sprawl (106 flagged) and provider sprawl (17)

Manager sprawl is low-signal here (all `sprawl_flag=0`) but the file list is useful as an orchestrator inventory. Provider sprawl is 17 files with ad-hoc providers — convert to shared adapter.

### 7.5 Duplicated adapters (`v_p2_duplicated_adapters`) — 3 rows and `v_p2_mixed_usage` — 3 rows

Small, tractable. Candidate for Wave 2 cleanup.

### 7.6 Experimental / isolated code (`v_p3_isolated_experimental`) — 6 rows

Zero-caller experimental modules. Either promote to real surface or archive under `archives/`.

### 7.7 Unused imports — 7,751 edges

Latent bloat. Auto-fixable with `ruff --fix --select F401` — worth one pass before any refactor wave for signal-to-noise.

---

## 8. Guardian Exemptions Near Critical Paths (1,827 rows)

Two files dominate and are the most leveraged fixes in the entire backlog:

| File | Pattern | Count (sample) | Criticality |
|---|---|---:|---:|
| `tools/eval/retrieval_benchmark.py` | `broad_exception_catch` + `silent_exception_swallow` | 7 shown (many more in file) | 275 |
| `ops_scripts/dev_tools/L0_routing_scripts/_ssot_meta_learning.py` | `log_and_swallow` (8 consecutive: lines 285, 343, 364, 374, 385, 403, 439, 447) | 8 | 220 |

**Action:** narrow these two files' exception handling first — single-file PRs will each move multiple MV rows.

---

## 9. Graph-Projection Cross-References

Attached graph projection (`adg_graph_04232026_0925.sqlite`) confirms:

- **`proj_centrality`** — concurs with `mv_hotspot_centrality` ranking: lifecycle_trace_contract tops, L0 config next.
- **`proj_scc`** — use to identify cyclic-import clusters (not summarized here; top rows suggest small cycles only).
- **`proj_reachability`** — `lifecycle_trace_contract` reaches 2,694 nodes at hop-2 → confirms "freeze" recommendation.
- **`proj_diff`** — use for next run to confirm P1 ratchet movement.

---

## 10. Recommended Execution Plan

> **This section lists work candidates only. Each wave below, if approved, requires a full plan at `.windsurf/plans/<slug>-<6hex>.md` with the mandatory `## ADG_HOTSPOT_REPORT` and `## ADG_GRAPH_LAYER_EVIDENCE` sections before any edits.**

### Wave 1 — L0/L5 core (×2.0 layer multiplier, highest impact-per-file)
- **W1.1** narrow exceptions in `hierarchy_healer.py`, `FileClassificationAgent.py`, `LocationHealerAgent.py`, `root_hygiene_healer.py`, `ArchitectureGovernorAgent.py` (5 files, ~79 LOW violations, ~317 impact points removed)
- **W1.2** harden `L0_routing/enforcement/execution_gateway.py` and `guardian_contract_types.py`
- **W1.3** freeze `lifecycle_trace_contract.py` behind an Author-Gate (no edits without scored decision)

### Wave 2 — write-path sovereignty (biggest structural risk)
- **W2.1** inventory the 1,900 `mv_new_write_bypass_paths` rows; route L4 memory writers through UWG
- **W2.2** add aiohttp/boto3 adapters in `L2_execution/utils/providers.py`; migrate the 23 `mv_gateway_bypass_paths` call sites
- **W2.3** fix L6 → L0 gravity inversion (150 `mv_authority_boundary_breaches`)

### Wave 3 — tooling & ops cleanup
- **W3.1** narrow exceptions in `tools/eval/retrieval_benchmark.py` (47 violations, 7 exemptions on critical paths)
- **W3.2** narrow 8 consecutive `log_and_swallow` in `_ssot_meta_learning.py`
- **W3.3** `tools/generate/validation/gates.py`, `tools/generate/reporting/reports.py`

### Wave 4 — hygiene pass
- **W4.1** `ruff --fix F401` for 7,751 unused imports
- **W4.2** promote or archive the 6 `v_p3_isolated_experimental` modules
- **W4.3** collapse the 3 `v_p2_duplicated_adapters` + 3 `v_p2_mixed_usage`

### Rollout discipline (non-negotiables)
- No wave without hotspot report + graph-layer evidence section.
- ADG regeneration + Redis reload after each wave.
- P1 ratchet must tighten (no regression) before the next wave.
- L_TEST-tier files deferred unless they block production refactors.

---

## 11. Evidence & Tooling

- Review script: `tools/debug/_tech_debt_review.py`
- Raw output: `artifacts/adg/tech_debt_review_04232026.txt`
- ADG snapshots: `artifacts/adg/adg_indexed_04232026_0925.sqlite`, `artifacts/adg/adg_graph_04232026_0925.sqlite`
- Related rules: `.windsurf/rules/adg-canonical-invariants.md`, `.windsurf/rules/adg-hotspot-enforcement.md`, `.windsurf/rules/adg-graph-layer-enforcement.md`
