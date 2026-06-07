
<!-- Converted from `.claude/rules/adg-analysis-procedures.md`. Original Cursor trigger: `model_decision`. -->

# ADG Analysis Procedures

> **Tier map (W2 dedupe):** Invariants → `adg-canonical-invariants.md`, `adg-graph-layer-enforcement.md`. On-demand procedures → **this rule** + `adg-p-band-burn-down-discipline.md` (globs). Tool routing → `adg-sqlite` + `graph-analysis` skills. Workflow aliases → `/adg-repair-loop`, `/adg-test-triage-gate` (no duplicate bodies). Legacy mirror → `.windsurf/rules/` (read-only).

> Procedural companion to `adg-canonical-invariants.md`.  
> **ADG SQLite = canonical truth; Redis = hot projection; artifacts = pre-computed analyses.**

---

## 1. Pre-Analysis: Graph Layer Foundation

### Architecture Overview

The ADG is **SQLite (relational) with a graph-layer overlay** providing graph-DB semantics:

| Graph Primitive | Relational Implementation |
|-----------------|---------------------------|
| Nodes | `nodes` table (id, entity_type, layer, file_path, adg_name) |
| Edges | `edges` table (src_id, tgt_id, relation_type) |
| Traversals | Recursive CTEs + materialized views (`mv_*`) |
| Centrality/blast radius | Pre-computed materialized views |
| Behavioral queries | Semantic edges: `flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite` |
| Concern taxonomies | Pre-built P-views (`v_p0_*`..`v_p3_*`) |

**FORBIDDEN**: Using only raw `edges`/`violations` tables without graph-layer primitives.

---

## 2. Hotspot Analysis Protocol

### Step 1 — Violations Snapshot

```
adg_violations(limit=100)
```

Extract:
- P0 count (CRITICAL) — MUST be zero before P1 work
- P1 count (HIGH) by category: `broad_exception_catch`, `silent_exception_swallow`, `log_and_swallow`, `return_none_swallow`
- Top files by raw violation count

### Step 2 — P0 Wave Plan

```
adg_p0_wave_plan(limit=100)
```

Use wave-based ordering. P0 blockers MUST resolve before P1 waves.

**Wave execution tone** (minimal narration while burning down P0 → P1 → P2): `adg-p-band-burn-down-discipline.md`.

### Step 3 — Fan-In Ranking (P1 Hotspots)

**PRIMARY**: Query materialized views directly:

| Materialized View | Use |
|-------------------|-----|
| `mv_graph_reverse_dependency_hotspots` | Fan-in hotspots by reverse_dependency_score |
| `mv_debt_concentration_hotspots` | Violation density + high centrality overlap |
| `mv_hotspot_centrality` | Per-module centrality score |
| `mv_dependency_cone_risk` | Per-module blast-cone risk |

**Fallback** (MVs unavailable): Manual computation
```
impact = violation_count × (1 + log10(1 + fan_in))
```

### Step 4 — Layer Criticality Multipliers

| Layer | Multiplier | Why |
|-------|-----------|-----|
| L0 routing | ×2.0 | Poisoned routing = downstream lies |
| L3 orchestration | ×1.75 | Chain failure hiding |
| L4 state/cache | ×1.75 | Silent inconsistency |
| L5 safety/guardrail | ×2.0 | Swallowed controls = no safety |
| L1/L2 | ×1.0 | Standard weight |
| L6 observability | ×0.75 | Lower structural risk |

### Step 5 — Produce Hotspot Report

```markdown
## ADG_HOTSPOT_REPORT
Snapshot: adg_indexed_<timestamp>.sqlite
P0 open: <N>
P1 open: <N>
Top hotspots (impact-ranked):
| rank | file | layer | violations | fan_in | impact | archetype |
|------|------|-------|-----------|--------|--------|-----------|
```

**Archetypes** (required):
- **CENTRAL_DEPENDENCY** — high fan-in, bad swallow poisons callers
- **ORCHESTRATOR** — high fan-out, swallow hides chain failures  
- **STATE_NODE** — state/cache path, swallow = inconsistency
- **SAFETY_GATEKEEPER** — controls/safety path, swallow = no safety

---

## 3. Graph-Layer Evidence (T2/T3 Required)

### Materialized Views to Consult

| MV | Use For |
|----|---------|
| `mv_graph_reverse_dependency_hotspots` | Fan-in hotspots |
| `mv_graph_chokepoint_bridges` | Articulation points |
| `mv_graph_critical_path_blast_radius` | Critical-path modules |
| `mv_hotspot_centrality` | Centrality scores |
| `mv_dependency_cone_risk` | Blast cone risk |
| `mv_path_criticality_rollup` | Path-level criticality |
| `mv_exemptions_near_critical_paths` | Risky exemptions |
| `mv_debt_concentration_hotspots` | Debt clustering |

### Semantic Edge Traversal

| Question | Relation | Tool |
|----------|----------|------|
| "What depends on X's output?" | `flows_to` | `adg_edge_fanout` |
| "Who calls this?" | `resolves_callsite` | `adg_edge_fanin` |
| "What side effects trigger?" | `emits_side_effect` | `adg_edge_fanout` |
| "What control flow reaches this?" | `controls_flow` | `adg_edge_fanin` |
| "What writes this data?" | `writes_to` | `adg_edge_fanin` |
| "What reads this data?" | `reads_from` | `adg_edge_fanin` |

### Pre-Built P-Views (Concern Prioritization)

| View | Concern |
|------|---------|
| `v_p0_*` (6 views) | Critical: apps_direct_infra, l0_raw_execution, l1_direct_infra, l6_mutation, provider_bypass, write_bypass_uwg |
| `v_p1_*` (4 views) | High: ad_hoc_imports, mis_layered_infra, not_on_spine, raw_http_outside_seam, zero_caller_infra |
| `v_p2_*` (3 views) | Medium: dormant_ambiguous, duplicated_adapters, mixed_usage |
| `v_p3_*` (1 view) | Low: isolated_experimental |

### Required Plan Output

```markdown
## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views Consulted
- mv_graph_reverse_dependency_hotspots: <top-N>
- mv_graph_chokepoint_bridges: <bridges in scope>
- <+ at least one more>

### Semantic Edges Used
- relation_type: <flows_to|resolves_callsite|...>
  Query: <what was queried>
  Finding: <what it revealed>

### Pre-Built P-Views Cross-Referenced
- v_p0_* or v_p1_*: <concerns affecting targets>

### Graph-Layer-Derived Priority
Files ranked using MVs above, NOT just violation counts.
```

---

## 4. P7 Analyst Artifacts (PRIMARY Source)

### The 7 Per-Run Artifacts

Under `artifacts/adg/` in `adg_run_<ts>.zip`:

| # | Artifact | Primary Use |
|---|----------|-------------|
| 1 | `adg_graphdb_projection_<ts>.json` | NetworkX node-link (76k nodes / 255k edges) |
| 2 | `adg_graphdb_metadata_<ts>.json` | Commit SHA, counts, timestamp |
| 3 | `adg_graphdb_index_<ts>.json` | Snapshot registry |
| 4 | `adg_graphdb_queries_<ts>.json` | 9 StructuralQueries + BlastRadius + layer subgraphs |
| 5 | `adg_structural_outputs_<ts>.json` | Burndown + top-20 blast-radius + seams + centrality |
| 6 | `adg_refactor_accelerator_<ts>.json` | Top-20 refactor candidates (ADG + churn + blast + tests) |
| 7 | `adg_runtime_spine_<ts>.json` | 6 handoff views + 13 cross-cutting families |

### Question → Artifact Routing

| Question | PRIMARY Artifact | SECONDARY |
|----------|------------------|-----------|
| "Which files to refactor first?" | `adg_refactor_accelerator_<ts>.json` → `candidates[]` | `adg_violations` |
| "Top-N blast radius?" | `adg_structural_outputs_<ts>.json` → `blast_radius` | `adg_edge_fanout` |
| "Top-N centrality?" | `adg_structural_outputs_<ts>.json` → `centrality` | `mv_hotspot_centrality` |
| "Chokepoint seams?" | `adg_structural_outputs_<ts>.json` → `seams` | `mv_graph_chokepoint_bridges` |
| "Burndown totals?" | `adg_structural_outputs_<ts>.json` → `burndown` | `adg_violations` |
| "Tests covering target?" | `adg_refactor_accelerator_<ts>.json` → `impacted_tests` | `adg_test_selector.py` |
| "90-day churn?" | `adg_refactor_accelerator_<ts>.json` → `churn_90d` | `git log` |
| "Layer purity violations?" | `adg_graphdb_queries_<ts>.json` → `l0_l1_l6_role_purity` | Live MV |
| "Gravity violations?" | `adg_graphdb_queries_<ts>.json` → `gravity_import_violations` | `v_p0_*`, `v_p1_*` |

### Required Protocol

1. **Locate latest artifacts** — match `adg_indexed_<ts>.sqlite` timestamp
2. **Load refactor accelerator FIRST** — `candidates[]` IS the ranked queue
3. **Cross-reference structural_outputs** — centrality, blast, seams
4. **Cross-reference graphdb_queries** — strategy signals (layer move vs exception narrowing)
5. **Cross-reference runtime_spine** — close witness gaps if `semantic_failures` present

---

## 5. Repair Discipline (ADG-Controlled)

### HARD GATES — NEVER BYPASS

**§ADG-1.1 No Edit Without ADG Provenance**
Before ANY code edit, answer all four:
1. Which ADG cluster? (from `artifacts/adg_failure_clusters.json`)
2. What is the root module? (canonical definition node)
3. Which scoped tests? (from `artifacts/adg_test_surface_map.json`)
4. Why is this file in the blast radius? (edge path from semantic graph)

**§ADG-1.2 No Full-Suite Run Before Convergence**
`pytest tests/unit` is FORBIDDEN during scoped repair loops.
Allowed: `pytest <cluster_scoped_test_files> -q`, `pytest <single_test_id> -xvs`

**§ADG-1.3 Fix Root Modules, Not Call Sites**
When symbol undefined in N files: fix the single root definition node, NOT each call site.

**§ADG-1.4 No Text-Search Debugging**
FORBIDDEN: `grep_search` for dependencies, imports, call-sites.  
REQUIRED: ADG MCP tools exclusively (`adg_edge_fanout`, `adg_edge_fanin`, `adg_node`, etc.)

### Repair Loop Protocol

```
STEP 1: Read artifacts/adg_failure_clusters.json → Identify highest-priority cluster
STEP 2: Read artifacts/adg_semantic_graph.json → Trace: test → import_edges → root_module
STEP 3: Read artifacts/adg_test_surface_map.json → Extract scoped test IDs
STEP 4: Run SCOPED tests: pytest <scoped_test_ids> -q → Observe failures
STEP 5: Fix ROOT MODULE only (definition node)
STEP 6: Rerun SCOPED tests → Verify cluster green
STEP 7: Mark cluster complete → Load next cluster → Repeat
```

### Mandatory Pre-Condition

Before ANY edit, write `## ADG_REPAIR_LITMUS`:
```markdown
## ADG_REPAIR_LITMUS
Cluster: <cluster_id>
Root module: <path/to/definition/file.py>
Scoped tests: <test_id_1>, <test_id_2>, ...
Blast radius: <edge_path: test → import → module>
```

**IF you cannot answer all 4 questions → STOP. The edit is FORBIDDEN.**

---

## 6. Test Accelerator Protocol

### Mandatory Commands

| Scenario | Command |
|----------|---------|
| Changed files | `python tools/adg/adg_test_accelerator.py scope --changed <files> --format pytest` |
| Pre-refactor (T2/T3) | `python tools/adg/adg_test_accelerator.py gap --top 30` |
| Import modifications | `python tools/adg/adg_test_accelerator.py collection-safety --json` |
| Parallel execution | `python tools/adg/adg_test_accelerator.py groups --workers 4 --format json` |
| Phase completion | `python tools/adg/adg_test_accelerator.py report --out <path>` |

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Proceed |
| 1 | No tests / Error | Run full suite, record SCOPE_LOSSINESS |
| Non-zero | ADG scan failure | Check `adg_stale_guard.py`, regenerate ADG |

### Tier-Based Enforcement

| Tier | Requirement |
|------|-------------|
| T0/T1 | Optional |
| T2 | **Required:** `scope` for changed files; `collection-safety` if imports modified |
| T3 | **Required:** `gap` before refactor, `scope` for selection, `collection-safety` after, `groups` for parallel |

---

## 7. The 5 ADG Surfaces

Cross-reference every hotspot against surfaces:

| # | Surface | Guards | Query Hint |
|:-:|---------|--------|------------|
| 1 | **Execution** | Tool invocations, agent dispatches, LLM calls | `mv_graph_critical_path_blast_radius` touching `L_TOOLS` / `L2_execution` |
| 2 | **Write** | State mutations via UWG / SovereignBaseAgent | `v_p0_write_bypass_uwg` + `writes_to` fan-in |
| 3 | **Security** | Guardrails, safety plane, Author-Gate | `L5_safety` nodes + `v_p0_provider_bypass` |
| 4 | **State** | Memory, cache, checkpoint store | `L4_state` nodes + `reads_from`/`writes_to` density |
| 5 | **Observability** | OTEL spans, audit trail, evidence | `L6_observability` nodes + `emits_side_effect` |

**Required**: Each `ADG_HOTSPOT_REPORT` row MUST list surfaces intersected (or "none").

---

## 8. Quick MCP Tool Mapping

| Need | Primary Tool | Fallback |
|------|--------------|----------|
| All violations | `adg_violations` | — |
| P0 wave ordering | `adg_p0_wave_plan` | — |
| Fan-in | `adg_edge_fanin` | — |
| Layer of file | `adg_nodes_by_file` | — |
| Node details | `adg_node` | — |
| Fan-out | `adg_edge_fanout` | — |
| Hotspot ranking (MV) | `mv_hotspot_centrality` | Manual compute |
| Blast radius | `mv_graph_critical_path_blast_radius` | `adg_edge_fanout` walk |

---

## References

- Invariants: `adg-canonical-invariants.md`
- Cheat sheet: `docs/reference/ADG/ADG SQLite Hotspot Cheat Sheet.md`
- P7 artifacts: `artifacts/adg/adg_run_<ts>.zip`
- Repair artifacts: `artifacts/adg_failure_clusters.json`, `artifacts/adg_semantic_graph.json`, `artifacts/adg_test_surface_map.json`
- Test accelerator: `tools/adg/adg_test_accelerator.py`
