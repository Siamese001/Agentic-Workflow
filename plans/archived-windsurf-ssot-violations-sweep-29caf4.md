---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\ssot-violations-sweep-29caf4.md'
original_relative_path: 'ssot-violations-sweep-29caf4.md'
source_sha256: 74d6e48db33e92e741f961e221e9ffe303252ec75e7c9e9d2f19e02d6bf4c365
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-20'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# SSOT Violations Sweep — W1+W2+W3

**Plan ID:** `ssot-violations-sweep-29caf4`
**Date:** 2026-04-20
**Tier:** T2 (3 files, single-layer-dominant at L5, fan-in=0 per ADG)
**Scope:** Close 7 NEW hardcoded-exclusion violations + 1 P0 layer violation. Defer 34 grandfathered entries to a separate plan.
**Status:** APPROVED (Author-Gate `refactor_scope` — W1+W2+W3 only)

## ADG Provenance

- Backend: `sqlite` + `redis_cache` (both healthy, cache_hit_capable)
- Snapshot: `adg_indexed_04202026_0923.sqlite` (76,374 nodes / 552,654 edges)
- Graph projection: `adg_graph_04202026_0923.sqlite` (fresh, not stale)

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|:----:|:---------:|-------|:-----------:|-------------|:------:|------------------|
| W1 | W1-P1 | L5 validator — replace 2 scan-walk exclusion literals with SSOT import | ~4K 🟢 | `GLOBAL_EXCLUDED_DIRS` semantically equivalent to both `ignore_dirs` and `ignored_dirs` | todo | `HygieneGuardianAgent.py` has zero hardcoded exclusion sets |
| W2 | W2-P1, W2-P2 | L5 reasoning + L_RUNTIME — mixed fix (extract tooling subset + allowlist legitimate domain literals) | ~7K 🟢 | Cleanup/delete sets are distinct domain from walk-exclusion sets | todo | `check_hardcoded_exclusions` baseline stays at 34 (no NEW above baseline) |
| W3 | W3-P1 | P0 layer violation in `tools/eval/retrieval_benchmark.py:2818` | ~5K 🟡 | Line has guardian comment; gate needs to honor it OR line needs restructure | todo | `adg_p0_wave_plan` reports 0 P0 items |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|:-----------:|:------:|
| W1-P1 | Replace hand-rolled `ignore_dirs` sets in `HygieneGuardianAgent.py` | 1 file | Two methods with overlapping-but-slightly-different ad-hoc sets | ~4K | todo |
| W2-P1 | Extract tooling subset + replace `_tooling_dirs` in `root_hygiene_healer.py:544` | 1 file (+ path_constants expose) | `_tooling_dirs` is a subset of `GLOBAL_EXCLUDED_DIRS`; need a named subset constant | ~4K | todo |
| W2-P2 | Add `root_hygiene_healer.py` + `sovereign_index_util.py` to `ALLOWLIST_PATHS` with justification | 1 file (check_hardcoded_exclusions.py) | Cleanup/delete sets are a distinct semantic domain; `sovereign_index_util` already imports SSOT as primary | ~3K | todo |
| W3-P1 | Reconcile `retrieval_benchmark.py:2818` L_TOOLS→L6 P0 layer violation | 1–2 files | Already has `# guardian: allow-layer-violation` comment but P0 wave plan flags it | ~5K | todo |

## ADG_HOTSPOT_REPORT

Graph-layer ranking driven by `adg_p0_wave_plan`, `adg_nodes_by_file`, `adg_edge_fanin`, and MV indicators.

| # | File:Line | Layer | Violation Kind | Fan-in (imports) | Priority Score | Archetype | Surface | Surface Rationale |
|:-:|-----------|:-----:|----------------|:----------------:|:--------------:|-----------|---------|-------------------|
| 1 | `agentic_core/L5_safety/validators/HygieneGuardianAgent.py:455` | L5 | hardcoded_exclusion_set (9 tokens) | 0 (module) | 45 (9×5) | **SAFETY_GATEKEEPER** | **Security Surface** | L5 validator enforces hygiene policy; drift in exclusion set = gate permits prohibited paths |
| 2 | `agentic_core/L5_safety/validators/HygieneGuardianAgent.py:684` | L5 | hardcoded_exclusion_set (5 tokens) | 0 (module) | 25 (5×5) | **SAFETY_GATEKEEPER** | **Security Surface** | Naming-hygiene scan; same drift risk as above |
| 3 | `agentic_core/L5_safety/reasoning/root_hygiene_healer.py:544` | L5 | hardcoded_tooling_subset (5 tokens) | 0 (module) | 25 (5×5) | **SAFETY_GATEKEEPER** | **Security Surface** | Tooling-dirs subset needs extraction to path_constants |
| 4 | `agentic_core/L5_safety/reasoning/root_hygiene_healer.py:387, 617, 713` | L5 | cleanup_domain_set (3+5+3 tokens) | 0 (module) | 15+15+15=45 | **CENTRAL_DEPENDENCY** (leaf) | **Write Surface** | Cleanup/delete action targets — these MUTATE disk state; distinct semantic from walk-exclusions |
| 5 | `agentic_core/runtime/utils/sovereign_index_util.py:193` | L_RUNTIME | fallback_literal (11 tokens) | 0 (module) | 19 (log(11)×8 layer-bonus) | **CENTRAL_DEPENDENCY** (leaf) | **State Surface** | Sovereign index; already imports SSOT as primary, literal is failsafe fallback |
| 6 | `tools/eval/retrieval_benchmark.py:2818` | L_TOOLS | layer_violation (L_TOOLS→L6) | 22 (node-level per wave plan) | 272 | **ORCHESTRATOR** | **Execution Surface** + **Observability Surface** | Benchmark imports L6 observability internals; crosses two surfaces |

**Layer-criticality multipliers applied:** L5 ×2.0 (safety plane), L_RUNTIME ×1.0, L_TOOLS ×1.0.

**Impact formula:** `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier × (1 + surface_intersections)`.

## ADG_GRAPH_LAYER_EVIDENCE

Graph-layer primitives consulted (per Constitutional §22):

**Materialized views referenced (≥3 required):**
- `mv_graph_reverse_dependency_hotspots` — confirmed all 4 target files have rank=N/A (leaf modules; not in hotspot list)
- `mv_hotspot_centrality` — per-module centrality score = low for all targets (consistent with fan-in=0 imports relation)
- `mv_debt_concentration_hotspots` — target files not in top-N debt-density rank (consistent with ratchet-not-breach status)
- `mv_dependency_cone_risk` — blast-cone risk = low (fan-out via `imports` is module-internal only for L5 agents)

**Semantic edges consulted:**
- `imports` — used for module-level fan-in queries (all targets returned 0)
- `flows_to` / `writes_to` — relevant for `root_hygiene_healer.py` Write Surface classification (delete actions mutate disk)
- `emits_side_effect` — relevant for `retrieval_benchmark.py` Observability Surface (L6 eval packet ingestion)

**P-views consulted:**
- `v_p2_duplicated_adapters` — target files NOT present → these are not classical duplicate-adapter drift
- `v_p0_apps_direct_infra` — target files NOT present → no apps→infra direct bypass here

**Why the raw `edges`/`violations` tables alone are insufficient:**
- `violations` table flags 50+ antipattern rows but doesn't rank by structural centrality or surface intersection → MV layer is required to prioritize
- `edges` alone can't classify the archetype (ORCHESTRATOR vs CENTRAL_DEPENDENCY) without joining against layer and surface metadata

## Zero-Loss Propagation Pipeline (per hotspot)

Traced for all 6 rows in the Hotspot Report:

```
HygieneGuardianAgent.py:455, :684
  catch site → hardcoded_exclusion_set (9/5 tokens)
  → ownership: HygieneGuardianAgent (symbol 18176) → L5_safety.validators (module 1086) → L5 layer
  → severity: MEDIUM (hygiene drift; gate-permits-bad-path risk)
  → fan-in: 0 (leaf, low blast radius)
  → surface: Security (L5 safety plane, validator archetype)
  → archetype: SAFETY_GATEKEEPER
  → HOTSPOT — RANK 1, 2
```

(Similar traces for rows 3–6 elided for brevity; same pipeline applied.)

## Wave Execution Order

### W1: Fix HygieneGuardianAgent.py (2 sites, proper SSOT import)

**Strategy:** Replace both hand-rolled `ignore_dirs` / `ignored_dirs` sets with `from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS`. The purpose of both sets is scan-walk exclusion — identical semantic to the SSOT.

**Risk:** 🟢 Low. Fan-in=0; semantic match is exact; no test fixture references these sets by name.

**Verification:** `python ops_scripts/ci/check_hardcoded_exclusions.py` reports violations drop from 7 to 5 (only root_hygiene_healer + sovereign_index_util remain).

### W2-P1: Extract tooling subset for root_hygiene_healer.py:544

**Strategy:** Add `TOOLING_EXCLUDED_DIRS` constant to `agentic_core/L0_routing/config/path_constants.py` containing the version-control / IDE / CI subset (`.git`, `.github`, `.vscode`, `.idea`, `.windsurf`). Import it in `root_hygiene_healer.py:544` replacing the inline `_tooling_dirs` set.

**Risk:** 🟢 Low. New SSOT constant, no existing consumers.

### W2-P2: ALLOWLIST exemption for legitimate domain literals

**Strategy:** Add entries to `ALLOWLIST_PATHS` in `ops_scripts/ci/check_hardcoded_exclusions.py`:
1. `agentic_core/L5_safety/reasoning/root_hygiene_healer.py` — cleanup/delete action targets (ALWAYS_DELETE, DELETE_IF_OLD, temp-folder sets); **Write Surface domain**, not walk-exclusion drift
2. `agentic_core/runtime/utils/sovereign_index_util.py` — fallback literal (line 190-193 ALREADY imports `GLOBAL_EXCLUDED_DIRS` as primary; literal is deliberate failsafe for import-error case)

Include inline comment on each allowlist entry citing the justification.

**Risk:** 🟢 Low. Allowlist is the gate's documented mechanism for legitimate domain overlap; explicit comments preserve intent.

**Verification:** `check_hardcoded_exclusions` returns exit 0 with baseline=34 unchanged.

### W3-P1: Reconcile tools/eval/retrieval_benchmark.py:2818 P0 layer violation

**Strategy (investigation-first):** The line already has `# guardian: allow-layer-violation` comment. Adjacent lines (2811, 2815, 2822) have similar comments but are NOT flagged. Root cause unknown.

**Investigation steps:**
1. Query ADG for all 4 lazy imports in the function (`adg_edge_fanout` on module 6394 with `relation_type=imports`)
2. Determine why only line 2818 (L_TOOLS→L6) triggers P0 vs the others (L_TOOLS→apps_exec, L3, L2)
3. Either: (a) patch the layer-violation rule generator to honor guardian-imports consistently, or (b) move the import to satisfy layer boundaries

**Fallback:** If (a) is a deep generator change, add line 2818 to the layer-violation baseline and document as grandfathered in a follow-up plan.

**Risk:** 🟡 Medium. Node-level fan-in=22 suggests this benchmark touches many nodes via the imported `async_eval_packet` API.

## Mode Separation

- **analyze** — complete (ADG queries, gate sweep, site inspection)
- **plan** — complete (this file)
- **edit** — begins at W1-P1 after this plan commit
- **verify** — each wave ends with `check_hardcoded_exclusions` + `adg_p0_wave_plan` re-run

## Rollback Checkpoints

- After W1 → commit → verify → tag if any revert needed
- After W2 → commit → verify
- After W3 → commit → verify

## Gap Register

| Gap | Impact | Disposition |
|-----|--------|-------------|
| 34 grandfathered hardcoded-exclusion sites | Long-tail SSOT drift across many files/layers | Deferred to separate plan (out of scope per user Author-Gate) |
| `_validate_baseline_integrity` test coverage | New code path in `check_graph_layer_evidence.py` not yet unit-tested | Deferred; gate manually validated against current baseline |
| Guardian-on-imports consistency in ADG generator | Root cause of W3 singular flag; may affect other files | Surfaced during W3 execution |
