---
trigger: model_decision
description: Use this rule before any refactoring, anti-pattern burndown, or wave planning to enforce mandatory ADG hotspot analysis — violations + structural centrality must drive target selection.
---
# ADG Hotspot Enforcement — Mandatory Pre-Refactoring Gate

> Reference doctrine: `docs/reference/ADG/ADG SQLite Hotspot Cheat Sheet.md`

## Architecture — Graph Layer over Relational SQLite

The ADG snapshot is **SQLite (a relational database) with a graph-layer overlay**
that provides graph-database semantics without a separate native graph store
(no Neo4j, no ArangoDB, no RDF triplestore).

The graph layer is emulated over relational tables:

| Graph Primitive | Relational Implementation |
|-----------------|---------------------------|
| Nodes | `nodes` table (id, entity_type, layer, file_path, adg_name) |
| Edges | `edges` table (src_id, tgt_id, relation_type) |
| Traversals (fan-in, fan-out, blast radius) | Recursive CTEs + materialized views (`mv_*`) |
| Centrality / chokepoints / critical paths | Pre-computed materialized views |
| Behavioral graph queries | Semantic edges: `flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite` |
| Architectural concern taxonomies | Pre-built P-views (`v_p0_*`..`v_p3_*`) |

**Why this matters for refactoring**: hotspot analysis is a **graph query**, not
a text search or a simple flat-table aggregation. Use the graph-layer primitives
(MVs, semantic edges, P-views) as PRIMARY; use raw `SELECT ... FROM edges` /
`FROM violations` only when no MV exists for the question.

## HARD GATE — No Refactoring Without a Hotspot Report

Before drafting ANY refactoring plan or wave queue at T2/T3:

1. A ranked hotspot report MUST be produced from the live ADG snapshot.
2. Target selection and wave ordering MUST be derived from that report.
3. FORBIDDEN: choosing files based on naming convention, alphabetical order, or "feels important" intuition without ADG backing.

> **PRIMARY source shortcut (post-P7):** `adg_refactor_accelerator_<ts>.json` under
> `artifacts/adg/` already contains the ranked `candidates[]` array with layer,
> blast_radius, centrality, 90-day churn, and impacted_tests. When present, it IS
> the hotspot report — do not recompute by hand. See `adg-p7-analyst-artifacts.md`
> for the full routing table. Live MCP queries below remain valid fallbacks when
> the artifact is stale, missing, or the question isn't covered.

---

## Required Protocol (execute in order)

### Step 1 — Violations Snapshot

```
adg_violations(limit=100)
```

Extract:
- P0 count (CRITICAL severity, open) — MUST be zero before P1 work begins
- P1 count (HIGH severity, open) by category: broad_exception_catch, silent_exception_swallow, log_and_swallow, return_none_swallow
- Top files by raw violation count

### Step 2 — Wave Plan (P0 first)

```
adg_p0_wave_plan(limit=100)
```

Use the wave-based ordering to establish P0 remediation queue. P0 blockers MUST be resolved before any P1 wave begins. The wave plan encodes structural dependency ordering — respect it.

### Step 3 — Fan-In Rank (P1 hotspot scoring)

**PRIMARY source (preferred):** query the materialized views that pre-compute
this ranking directly from the ADG snapshot — do not recompute by hand:

| Materialized View | Use |
|-------------------|-----|
| `mv_graph_reverse_dependency_hotspots` | Fan-in hotspots ranked by reverse_dependency_score |
| `mv_debt_concentration_hotspots` | Files where violation density overlaps high centrality |
| `mv_hotspot_centrality` | Per-module centrality score |
| `mv_dependency_cone_risk` | Per-module blast-cone risk |

The MV columns already encode the hotspot score; use their ordering directly.

**Fallback (only if MVs are unavailable / stale):** compute manually using
`adg_edge_fanin` for the top 20–30 P1 violation files from Step 1:

```
adg_edge_fanin(tgt_id=<file_node_id>, relation_type="imports")
impact = violation_count × (1 + log10(1 + fan_in))
```

Where:
- `violation_count` = open P1 violations in the file (not exempted/guardian/waived)
- `fan_in` = number of distinct source files that import this file

Sort descending by impact. This ranked list IS the refactoring queue.

**Plans that recompute ranking by hand when the MVs are available MUST cite
why the MVs were insufficient.** Otherwise the MV result is the canonical source.

### Step 4 — Layer Criticality Adjustment

For top-ranked files, check their layer via `adg_nodes_by_file`. Apply layer multipliers:

| Layer | Multiplier | Why |
|-------|-----------|-----|
| L0 routing | ×2.0 | Poisoned routing = all downstream lies |
| L3 orchestration | ×1.75 | Chain failure hiding |
| L4 state / cache | ×1.75 | Silent inconsistency |
| L5 safety / guardrail | ×2.0 | Swallowed controls = no safety |
| L1/L2 | ×1.0 | Standard weight |
| L6 observability | ×0.75 | Still bad, but less structural risk |

Rerank after multiplier. Final adjusted rank = refactoring priority order.

### Step 5 — Produce Hotspot Report

The hotspot report MUST contain (formatted as a table in the plan):

```
| rank | file | layer | violations | fan_in | impact | archetype |
```

Where archetype is one of:
- **CENTRAL_DEPENDENCY** — high fan-in, bad swallow poisons many callers
- **ORCHESTRATOR** — high fan-out/flows, swallow hides chain failures
- **STATE_NODE** — state/cache path, swallow = silent inconsistency
- **SAFETY_GATEKEEPER** — controls/safety path, swallow suppresses guardrails

---

## Blocking Conditions

| Condition | Action |
|-----------|--------|
| P0 violations > 0 | P0 MUST be addressed first. P1 wave is BLOCKED. |
| ADG snapshot older than last code change | Regenerate: `python tools/generate_full_adg.py` |
| `adg_violations` returns error | Run `/mcp-failure-rca` — BLOCKED until MCP is healthy |
| Hotspot report missing from plan | Plan is INVALID — regenerate before any edits |

---

## Required Output Evidence

The `.windsurf/plans/<name>.md` for any refactoring wave MUST include a section:

```markdown
## ADG_HOTSPOT_REPORT
Snapshot: adg_indexed_<timestamp>.sqlite
P0 open: <N>
P1 open: <N>
Top hotspots (impact-ranked):
| rank | file | layer | violations | fan_in | impact | archetype |
|------|------|-------|-----------|--------|--------|-----------|
| 1    | ...  | ...   | ...       | ...    | ...    | ...       |
...
Wave queue derived from rank order above.
```

A plan without `## ADG_HOTSPOT_REPORT` is incomplete and MUST NOT be executed.

---

## Hotspot Score Mental Model

```
HOTSPOT SCORE ≈ violation_severity × structural_centrality × blast_radius × layer_criticality × surface_intersection

- violation_severity:   silent_swallow > broad_catch > logged_catch > return_none
- centrality:           fan-in (import concentration)
- blast_radius:         fan-out + flows_to + controls_flow
- layer_criticality:    L0/L5 > L3/L4 > L1/L2 > L6
- surface_intersection: +1 multiplier per ADG Surface the catch flow crosses
```

High fan-in + swallow → guardian only with very strong reason (many callers get wrong signal).
High fan-out + broad catch → narrow the catch (orchestrator hiding chain failures).
L4/L5 silent swallow → highest skepticism; near-certain refactor target.

---

## The 5 ADG Surfaces (risk boundaries — MUST be cross-referenced per hotspot)

Surfaces are semantic boundaries where untrusted inputs flow. Swallowing errors
at a surface causes **system lies** — the system reports success while producing
corrupt/missing output. A hotspot that intersects any surface is higher-priority
than the same hotspot in an isolated module.

| # | Surface | What It Guards | Query hint |
|:-:|---------|----------------|-----------|
| 1 | **Execution Surface** | Tool invocations, agent dispatches, subprocess, LLM calls | nodes on `mv_graph_critical_path_blast_radius` touching `L_TOOLS` / `L2_execution` |
| 2 | **Write Surface** | State mutations via UWG / SovereignBaseAgent / canonical store | `v_p0_write_bypass_uwg` + `writes_to` fan-in |
| 3 | **Security Surface** | Guardrails / safety plane / policy enforcement / HITL gates | `L5_safety` nodes + `v_p0_provider_bypass` |
| 4 | **State Surface** | Memory / cache / checkpoint / canonical store | `L4_state` nodes + `reads_from` / `writes_to` high-density |
| 5 | **Observability Surface** | OTEL spans / audit trail / evidence ledger | `L6_observability` nodes + `emits_side_effect` edges |

**Required in `## ADG_HOTSPOT_REPORT`**: each hotspot row MUST list the surfaces it intersects (or "none").

---

## The 4 Deadly Catch-Site Antipatterns

These four are **structurally dangerous** and are the canonical hotspot triggers:

| Antipattern | Code Shape | Failure Mode |
|-------------|-----------|--------------|
| `broad_exception_catch` | `except Exception:` | Collapses specific failures into one bucket |
| `silent_exception_swallow` | `except X: pass` | Total invisibility |
| `log_and_swallow` | `except X: log(e); continue` | Keeps running in bad state |
| `return_none_swallow` | `except X: return None` | Failure → ambiguity → later crash |

Any of these on a surface + high fan-in = **HOTSPOT**. Guardian exemption requires HITL approval per `anti-pattern-hitl-gate.md`.

---

## Hotspot Archetypes (required classification)

Every row in `## ADG_HOTSPOT_REPORT` MUST be tagged with exactly one archetype:

| Archetype | Signature | Danger |
|-----------|-----------|--------|
| **CENTRAL_DEPENDENCY** | High fan-in, low fan-out | Bad swallow poisons many callers |
| **ORCHESTRATOR** | High fan-out, dense `flows_to` | Swallow hides chain failures |
| **STATE_NODE** | On Write / State surface; `writes_to`/`reads_from` density | Silent inconsistency across sessions |
| **SAFETY_GATEKEEPER** | On Security surface; `L5_safety`; guardrail/policy code | Swallow suppresses guardrails — no safety |

---

## Zero-Loss Propagation Pipeline (required trace per hotspot)

Every hotspot claim MUST be traceable through this chain. A hotspot that skips
any step is **unproven** and cannot be scheduled for refactoring:

```
[ catch site at file:line ]
       │
       ▼
[ antipattern edge ]       (one of the 4 deadly kinds)
       │
       ▼
[ ownership bridge ]       (Symbol → owning Module → Layer)
       │
   ├─► violation_severity  (which of the 4?)
   ├─► layer               (L0/L5 > L3/L4 > L1/L2 > L6)
   ├─► fan-in              (reverse walk — who breaks)
   ├─► fan-out             (forward walk — what gets hidden)
   ├─► surfaces crossed    (any of 5 ADG Surfaces?)
   └─► archetype           (which of the 4?)
       │
       ▼
  [ HOTSPOT — ranked ]
```

---

## Quick MCP Tool Mapping

| Need | Tool | Relation Type |
|------|------|--------------|
| All violations ranked | `adg_violations` | — |
| P0 wave ordering | `adg_p0_wave_plan` | — |
| Fan-in for a file node | `adg_edge_fanin` | `imports` |
| Layer of a file | `adg_nodes_by_file` | — |
| Node structural details | `adg_node` | — |
| Fan-out blast radius | `adg_edge_fanout` | `imports` / `flows_to` |

---

## References

- Cheat sheet: `docs/reference/ADG/ADG SQLite Hotspot Cheat Sheet.md`
- Hotspot scripts: `tools/debug/_adg_p1_hotspots.py`, `tools/debug/_adg_p1_hotspots_top.py`
- Repair loop: `adg-repair-discipline.md`
- Wave plan tool: `adg_p0_wave_plan` (adg_sqlite MCP)
