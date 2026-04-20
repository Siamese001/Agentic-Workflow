---
trigger: model_decision
description: Use this rule before any refactoring, anti-pattern burndown, or wave planning to enforce mandatory ADG hotspot analysis — violations + structural centrality must drive target selection.
---
# ADG Hotspot Enforcement — Mandatory Pre-Refactoring Gate

> Reference doctrine: `docs/reference/ADG/ADG SQLite Hotspot Cheat Sheet.md`

## HARD GATE — No Refactoring Without a Hotspot Report

Before drafting ANY refactoring plan or wave queue at T2/T3:

1. A ranked hotspot report MUST be produced from the live ADG snapshot.
2. Target selection and wave ordering MUST be derived from that report.
3. FORBIDDEN: choosing files based on naming convention, alphabetical order, or "feels important" intuition without ADG backing.

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
HOTSPOT SCORE ≈ violation_severity × structural_centrality × blast_radius × layer_criticality

- violation_severity: silent_swallow > broad_catch > logged_catch
- centrality:         fan-in (import concentration)
- blast_radius:       fan-out + flows_to + controls_flow
- layer_criticality:  L0/L5 > L3/L4 > L1/L2 > L6
```

High fan-in + swallow → guardian only with very strong reason (many callers get wrong signal).
High fan-out + broad catch → narrow the catch (orchestrator hiding chain failures).
L4/L5 silent swallow → highest skepticism; near-certain refactor target.

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
