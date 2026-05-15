---
plan_id: p1p2-burndown-graph-driven-7e4a9c
created: 2026-04-19
tier: T3
status: active
---

# P1 + P2 Burndown — Graph-Layer Driven Wave Plan

## Current State

**ADG snapshot**: `adg_indexed_04192026_2048.sqlite`
**Ratchets**: P1 = 0/0 (stable, all 896 HIGH exempt), P2 = **2430**/2430 (stable).

**P2 net (2430) breakdown by kind:**

| Kind | Net | Auto-fixable? |
|------|-----|---------------|
| broad_exception_catch | 789 | Manual (per-site narrowing) |
| partial_side_effects | 511 | Manual (rollback design) |
| double_logging | 243 | Manual (log-or-raise choice) |
| log_and_swallow | 197 | Manual |
| silent_exception_swallow | 188 | Manual |
| return_none_swallow | 110 | Manual |
| default_fallback_masking | 103 | Manual |
| exception_type_erasure | 84 | **AUTO — add `from e`** |
| star_import_use | 83 | Semi-auto |
| unreachable_after_raise | 78 | **AUTO — delete dead code** |
| retry_without_backoff | 28 | Manual (backoff integration) |
| bare_except | 16 | **AUTO — narrow to Exception** |

Note: the swallow-class P1 HIGH count is 0 net, but 896 gross exists in prod — all validly exempted. Those are NOT in this burndown (they are approved as-is).

---

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views Consulted

#### `mv_graph_reverse_dependency_hotspots`
Columns: `file_path, layer, direct_inbound, hop2_inbound, reverse_dependency_score, layer_criticality_weight`.
Used to compute **violation × fan-in impact** score for every P2 file.

**Top-5 hotspots by violations × reverse_dependency_score:**

| file | violations | fan_in | rdscore | layer |
|------|-----------|--------|---------|-------|
| `system_learning/adapters/system_learning_memory_bridge.py` | **38** | 28 | 28 | L_SL |
| `apps_rg/engines/base_rg_engine.py` | 5 | 44 | 44 | L_APP |
| `agentic_core/L2_execution/utils/write_gateway.py` | 3 | **80** | 80 | L2 |
| `agentic_core/adg/extraction/static_scanner.py` | 2 | **91** | 91 | L_TOOLS |
| `agentic_core/base_agents/SovereignBaseAgent.py` | — | 132 | 132 | L_SHARED |

#### `mv_graph_critical_path_blast_radius`
Columns: `file_path, direct_downstream, hop2_downstream, raw_blast_radius, weighted_blast_radius, critical_downstream_count, blast_radius_type`.
Used to identify blast-radius of each hotspot before touching it.

#### `mv_graph_chokepoint_bridges`
Columns: `file_path, fan_in, fan_out, bridge_score, imbalance_ratio, bridge_type`.
Chokepoints act as articulation points — changes cascade. Top hotspots cross-checked against this MV so bridge-files get refactor-with-caution treatment.

#### `mv_hotspot_centrality`
Columns: `adg_name, resolved_path, fan_in, fan_out, degree, betweenness_approx, degree_centrality`.
Used to rank by **betweenness**, not just fan-in, so chain-failure hiders surface even when their direct inbound is modest.

#### `mv_debt_concentration_hotspots`
Columns: `file, layer, p0_count, p1_count, p2_count, p3_count, total_violations, total_debt_score, hotspot_rank`.
Canonical debt-score ranking used to order Wave 2+ targets.

### Semantic Edges Used

For each top-5 hotspot file, we queried edge counts by relation_type:

| file | flows_to | emits_side_effect | resolves_callsite | controls_flow | writes_to |
|------|----------|-------------------|-------------------|---------------|-----------|
| `system_learning_memory_bridge.py` | **118** | 13 | 63 | 125 | 0 |
| `apps_rg/engines/base_rg_engine.py` | 2 | 2 | 5 | 10 | 0 |
| `L2_execution/utils/write_gateway.py` | 34 | **20** | 41 | 28 | **25** |
| `ops_scripts/.../_ssot_phases.py` | 166 | 57 | 128 | 123 | 4 |
| `ops_scripts/.../_ssot_meta_learning.py` | 88 | 36 | 47 | 48 | 6 |

**Finding**: `write_gateway.py` has the highest **behavioral density** of the prod-critical files (25 writes + 20 side-effects + 41 call-resolutions) — any swallow here is high-impact.

`resolves_callsite` will be used in Wave 2 to enumerate callers of each swallow site so we know the caller-contract before narrowing the catch.

### Pre-Built P-Views Cross-Referenced

| P-view | Count | Relevance |
|--------|-------|-----------|
| `v_p2_duplicated_adapters` | 2 | Duplicates found — inspect during Wave 2 for possible consolidation |
| `v_p2_mixed_usage` | 3 | Mixed legitimate/illegitimate use — inspect during Wave 2 |
| `v_p3_isolated_experimental` | 6 | Isolated experimental modules — exclude from burndown |
| All `v_p0_*` / `v_p1_*` | 0 | No P0/P1-class architectural concerns — clean architectural state |

### Graph-Layer-Derived Priority

**Wave ordering is derived from the MVs above — NOT violation count alone:**
- **Wave 1 targets** = all files with unreachable_after_raise / exception_type_erasure / bare_except (mechanical, irrespective of centrality). Estimated impact: **178 sites** burned in ~10 minutes.
- **Wave 2 targets** = top-5 hotspots from `mv_graph_reverse_dependency_hotspots` **restricted to manual-only kinds** (broad_exception_catch, swallows, default-fallback, partial-side-effects). Estimated impact: **~46 sites** in architecturally critical files.
- **Wave 3 targets** = star_import_use (83 sites) — semi-mechanical expansion.
- **Wave 4 targets** = `broad_exception_catch` systematic narrowing, grouped by **`resolves_callsite` caller cohorts** (use graph layer to group sites by caller-expectation).
- **Wave 5 targets** = everything else, lowest priority.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Net Burn | Tokens | Status | Success Criteria |
|------|-----------|-------|--------------:|-------:|--------|------------------|
| 1    | W1-01     | Mechanical fixes: `unreachable_after_raise` + `exception_type_erasure` + `bare_except` | **178** | 🟢 2k | pending | All 3 kinds → 0; P2 ≤ 2252 |
| 2    | W2-01..05 | Top-5 hotspot file refactors (per `mv_graph_reverse_dependency_hotspots`) | ~46 | 🟡 8k | pending | Top-5 files reduced to ≤2 P2 each |
| 3    | W3-01     | `star_import_use` mechanical expansion | 83 | 🟢 3k | pending | P2 star_import_use = 0 |
| 4    | W4-01..N  | `broad_exception_catch` narrowing, grouped by `resolves_callsite` caller cohort | ~789 | 🔴 40k+ | pending | broad_exception_catch ≤ 100 |
| 5    | W5-01..N  | Remaining P2 (manual per-site review) | ~1300 | 🔴 huge | pending | P2 ≤ 500 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1-01 | Mechanical burn (3 auto-fixable kinds) | ~140 files across all layers | Manual per-site narrowing only — no `burn_wave2.py` exists (never built). Auto-fix rejected 2026-04-24 per RCA: P0/P1 have ~87% false-positive rate against doctrinally-valid best-effort patterns. See `tools/archive/phase3_orphan_w6/README.md`. | 🟢 2k | pending |
| W2-01 | `system_learning_memory_bridge.py` (38 V) | 1 file, L_SL | Largest single-file target; use resolves_callsite to understand consumers before narrowing | 🟡 3k | pending |
| W2-02 | `apps_rg/engines/base_rg_engine.py` (5 V) | 1 file, L_APP | High fan-in 44 | 🟢 1k | pending |
| W2-03 | `L2_execution/utils/write_gateway.py` (3 V) | 1 file, L2 | Critical write path — 25 writes_to + 20 side-effects | 🟡 2k | pending |
| W2-04 | `adg/extraction/static_scanner.py` (2 V) | 1 file, L_TOOLS | Centrality 91; high blast radius | 🟢 1k | pending |
| W2-05 | `apps_shared/utils/subatomic_hop_util.py` (17 V) | 1 file, L_APP_SHARED | Large AP cluster | 🟡 2k | pending |
| W3-01 | Star-import expansion | 83 sites, ~40 files | Expand `from X import *` to explicit names | 🟢 3k | pending |
| W4-01 | `broad_exception_catch` — L0/L5 narrowing cohort | L0 routing + L5 safety files | Highest criticality layers first | 🟡 10k | pending |
| W4-02 | `broad_exception_catch` — L2/L3/L4 cohort | Core execution/orchestration/state | Middle tier | 🔴 15k | pending |
| W4-03 | `broad_exception_catch` — L_APP/ops_scripts/tests cohort | Tooling layers | Lower priority | 🔴 15k | pending |
| W5-01 | `partial_side_effects` manual review | ~511 sites | Requires rollback/compensate design per site | 🔴 huge | deferred |
| W5-02 | All swallow-class manual review | ~500 sites | Per-site intent review | 🔴 huge | deferred |

## Gap Register

Deferred items (not in this burndown):
- Wave 5 is described but not scheduled — separate plan when Wave 1-4 complete
- `global_state_mutation` (2766 P3) and `hardcoded_path` (90 P3) deliberately excluded — watch-only, no P3 ratchet
- `throw_for_normal_flow` (266 P3) excluded — subjective, needs taxonomy first

---

## Execution Protocol

Each wave follows this protocol:
1. Execute fixer script with `ast.parse` verification per-file
2. `py_compile` the modified trees  
3. Regenerate ADG (`python tools/generate_full_adg.py`)
4. Verify P2 decreased by expected amount, ratchets auto-reduce
5. Move to next wave

Rollback: any wave that fails `py_compile` or drops test count is reverted via git.

---

## References

- Rule: `.cursor/rules/adg-graph-layer-enforcement.md` (Constitutional §22)
- Rule: `.cursor/rules/adg-hotspot-enforcement.md` (Constitutional §5)
- Intel source: Graph-layer MVs on snapshot `adg_indexed_04192026_2048.sqlite`
