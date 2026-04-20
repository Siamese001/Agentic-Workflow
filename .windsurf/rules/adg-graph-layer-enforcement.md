---
trigger: model_decision
description: Use this rule before any T2/T3 refactoring plan, wave queue, or prioritization decision to enforce mandatory use of the ADG graph-layer primitives (materialized views, semantic edges, pre-built P-views) as PRIMARY drivers — not just the flat SQLite tables.
---
# ADG Graph-Layer Enforcement — MVs + Semantic Edges + P-Views Are Primary

> Reference doctrine: `docs/reference/ADG/ADG SQLite Hotspot Cheat Sheet.md`, this rule file, and `adg-hotspot-enforcement.md` (which this extends).

## HARD GATE — Graph Layer Must Drive Refactoring

The ADG is **SQLite (relational) with a graph-layer overlay** — `nodes`/`edges`
tables + materialized views + P-views + semantic edges — providing graph-DB
semantics (traversals, centrality, blast radius) without a separate Neo4j-style
backend. The graph layer is NOT optional flavor on top of flat tables; it IS the
primary analysis surface. It provides:

1. **Materialized views (`mv_*`)** — 45+ pre-computed analyses (hotspots, blast radius, chokepoints, critical paths, dependency cones)
2. **Semantic edges** — `flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite` (all populated; not just `imports`)
3. **Pre-built P-views** — `v_p0_*`, `v_p1_*`, `v_p2_*`, `v_p3_*` (6 + 4 + 3 + 1 pre-classified concern views)
4. **Precision tables** — `precision_variable_attributes`, `precision_side_effects`, `precision_call_resolution` (when populated)

Any T2/T3 refactoring plan MUST use these as **primary drivers**. Using only `edges` + `violations` tables is **insufficient** and counts as partial analysis.

---

## Required Protocol (extends `adg-hotspot-enforcement.md`)

### Step A — Materialized View Consultation (MANDATORY before target selection)

At minimum, query these MVs and include findings in the plan:

| MV | Use For | Plan Must Record |
|----|---------|------------------|
| `mv_graph_reverse_dependency_hotspots` | Fan-in hotspots (who depends on me) | Top-N files + reverse_dependency_score |
| `mv_graph_chokepoint_bridges` | Articulation points where changes cascade | Bridge modules in affected scope |
| `mv_graph_critical_path_blast_radius` | Critical-path modules | Critical paths intersecting targets |
| `mv_hotspot_centrality` | Graph centrality score per module | Centrality of top-N refactor targets |
| `mv_dependency_cone_risk` | Per-module blast cone risk | Cone size for top-N targets |
| `mv_path_criticality_rollup` | Path-level criticality | Critical paths with open violations |
| `mv_exemptions_near_critical_paths` | Risky exemptions on critical paths | Exemptions being inherited |
| `mv_debt_concentration_hotspots` | Where debt clusters | Concentration vs fan-in overlap |

FORBIDDEN: plans that cite only raw `edges` / `violations` counts without at least 3 of the above MVs.

### Step B — Semantic Edge Traversal (required for cross-file analysis)

When the plan touches multiple files, query the appropriate semantic relations:

| Question | Required Relation | Tool |
|----------|------------------|------|
| "What depends on X's output?" | `flows_to` | `adg_edge_fanout(relation_type="flows_to")` |
| "Who calls this?" | `resolves_callsite` | `adg_edge_fanin(relation_type="resolves_callsite")` |
| "What side effects does this trigger?" | `emits_side_effect` | `adg_edge_fanout(relation_type="emits_side_effect")` |
| "What control flow reaches this?" | `controls_flow` | `adg_edge_fanin(relation_type="controls_flow")` |
| "What writes this data?" | `writes_to` | `adg_edge_fanin(relation_type="writes_to")` |
| "What reads this data?" | `reads_from` | `adg_edge_fanin(relation_type="reads_from")` |

Using only `imports` edges when the question is behavioral (who calls, who mutates, what side-effects) is **insufficient**.

### Step C — Pre-Built P-View Consultation (for concern prioritization)

Before declaring a refactoring concern, consult the pre-built views. Each encodes a specific architectural concern:

| View | Concern |
|------|---------|
| `v_p0_apps_direct_infra` | Apps bypassing app boundary to hit infra |
| `v_p0_l0_raw_execution` | L0 doing raw execution (routing layer violation) |
| `v_p0_l1_direct_infra` | L1 cognition layer hitting infra directly |
| `v_p0_l6_mutation` | Observability layer performing mutations |
| `v_p0_provider_bypass` | Provider calls bypassing gateway |
| `v_p0_write_bypass_uwg` | Writes bypassing UWG (Unified Write Gateway) |
| `v_p1_ad_hoc_imports` | Ad-hoc imports (should go through seams) |
| `v_p1_mis_layered_infra` | Infra code in wrong layer |
| `v_p1_not_on_spine` | Off-spine modules |
| `v_p1_raw_http_outside_seam` | Raw HTTP outside the network seam |
| `v_p1_zero_caller_infra` | Infra with zero callers (dead) |
| `v_p2_dormant_ambiguous` | Dormant/ambiguous modules |
| `v_p2_duplicated_adapters` | Duplicated adapter implementations |
| `v_p2_mixed_usage` | Mixed legitimate/illegitimate use |
| `v_p3_isolated_experimental` | Isolated experimental code |

Refactoring targets MUST be cross-referenced against these views. Example: before refactoring a file flagged as a P1 hotspot, check if it also appears in `v_p1_mis_layered_infra` (indicating the fix may require layer move, not just exception narrowing).

---

## Plan Output Requirements

Every T2/T3 refactoring plan at `.windsurf/plans/<name>-<6hex>.md` MUST contain a section:

```markdown
## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views Consulted
- mv_graph_reverse_dependency_hotspots: <top-N with scores>
- mv_graph_chokepoint_bridges: <bridges intersecting target scope>
- mv_hotspot_centrality: <centrality of top-N targets>
- <+ at least one more relevant MV>

### Semantic Edges Used
- relation_type: <flows_to | resolves_callsite | emits_side_effect | ...>
  Query: <what was queried>
  Finding: <what it revealed>

### Pre-Built P-Views Cross-Referenced
- v_p0_* or v_p1_* or v_p2_*: <concerns found affecting targets>

### Graph-Layer-Derived Priority
Files ranked using MVs above, NOT just violation counts.
```

A plan missing `## ADG_GRAPH_LAYER_EVIDENCE` is **incomplete and MUST NOT be executed**.

---

## Blocking Conditions

| Condition | Action |
|-----------|--------|
| Plan cites only raw `edges`/`violations` with no MVs | BLOCKED — regenerate with graph layer |
| Plan uses only `imports` edges when the question is behavioral | BLOCKED — use correct semantic relation |
| Plan ignores a P-view concern that applies to its targets | BLOCKED — cross-reference required |
| MV query returns stale results (snapshot > 7 days) | Regenerate ADG: `python tools/generate_full_adg.py` |

---

## Why This Matters

The SQLite `edges` table has 550k+ rows. Iterating it directly for refactoring analysis is:

1. **Slow** — MVs pre-aggregate the analyses that matter
2. **Error-prone** — computing centrality / blast-radius / critical-paths ad-hoc loses fidelity vs the canonical MV definitions
3. **Incomplete** — `imports` edges alone answer dependency questions but not behavior questions (what writes / reads / flows / triggers side effects)

The graph layer is the **canonical** analysis primitive. The flat `edges`/`violations` tables are the **storage** primitive. Do not conflate the two.

---

## Quick Tool Mapping

| Need | Primary Source | Fallback |
|------|----------------|----------|
| Fan-in hotspot ranking | `mv_graph_reverse_dependency_hotspots` | `adg_edge_fanin(relation_type="imports")` |
| Blast radius / impact | `mv_graph_critical_path_blast_radius` | `adg_edge_fanout` transitive walk |
| Bridge/chokepoint files | `mv_graph_chokepoint_bridges` | — (no good fallback) |
| Centrality score | `mv_hotspot_centrality` | — (pre-computed, use it) |
| Architectural concern match | `v_p0_*`, `v_p1_*`, `v_p2_*`, `v_p3_*` | — (pre-built, use them) |
| Dataflow lineage | `flows_to` edges + `precision_variable_attributes` | `reads_from` + `writes_to` join |
| Side-effect reachability | `emits_side_effect` edges + `precision_side_effects` | — (use semantic edges) |
| Call-graph resolution | `resolves_callsite` + `precision_call_resolution` | `imports` (degraded) |

---

## Enforcement

| Layer | Mechanism |
|-------|-----------|
| Tier 2 (prompt) | This rule file (`model_decision` trigger, auto-loaded for refactor tasks) |
| Tier 3 (plan check) | `ops_scripts/ci/check_graph_layer_evidence.py` scans `.windsurf/plans/**/*.md` for required section + MV citations |
| Tier 4 (CI) | `run_contract_gates.py` invokes the check gate |
| Tier 5 (telemetry) | Plans lacking the evidence section logged to `artifacts/windsurf/graph_layer_violations.jsonl` |

---

## References

- Extension of: `adg-hotspot-enforcement.md`
- Cheat sheet: `docs/reference/ADG/ADG SQLite Hotspot Cheat Sheet.md`
- ADG schema (views + MVs): query via `SELECT name FROM sqlite_master WHERE type IN ('view','table') AND name LIKE 'mv_%' OR name LIKE 'v_p%'`
- Enforcement script: `ops_scripts/ci/check_graph_layer_evidence.py`
