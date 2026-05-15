---
name: adg-sqlite
description: AST Dependency Graph analysis — node lookup by ID/file/layer, edge fan-in/fan-out, layer violations, P0 wave plans, snapshot health — via the in-house adg_sqlite MCP server. Invoke for ANY dependency, import, consumer, reference, blast-radius, or who-uses-X / what-depends-on-Y query. Distinguishes ADG MCP (structural code analysis) from grep_search (FORBIDDEN for deps) and from runtime ADG (otel_mcp). Wraps the canonical SQLite snapshot at artifacts/adg/adg_indexed_<ts>.sqlite. See sibling skill graph-analysis for the broader retrieval-tool decision tree.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
---

# ADG SQLite Skill

In-house MCP — no upstream vendor. The canonical static dependency graph for this repo.

**Sibling skill:** `graph-analysis` (decision tree for picking ADG MCP vs grep vs SQLite-direct vs semantic)
**Doctrine:** `.cursor/rules/adg-canonical-invariants.md`, `.cursor/rules/adg-graph-layer-enforcement.md`

## When To Use This MCP

| User intent | Use adg_sqlite? |
|---|---|
| Dependency / import analysis | ✅ Yes — REQUIRED |
| Blast radius of a change | ✅ Yes — REQUIRED |
| Layer / file / consumer queries | ✅ Yes — REQUIRED |
| Hotspot ranking (fan-in × violations) | ✅ Yes — REQUIRED |
| P0/P1/P2/P3 violation triage | ✅ Yes — REQUIRED |
| Wave plan generation | ✅ Yes — REQUIRED |
| Refactoring scope discovery | ✅ Yes — REQUIRED |

## Tool Routing

| Goal | Tool |
|---|---|
| Health check (always first) | `adg_health` |
| Find node by name | `adg_find_node` |
| Get node by ID | `adg_node` |
| Nodes in a file | `adg_nodes_by_file` |
| Nodes in a layer (L0..L6) | `adg_nodes_by_layer` |
| Outgoing edges by relation | `adg_edge_fanout` |
| Incoming edges by relation | `adg_edge_fanin` |
| All current violations | `adg_violations` |
| P0 wave plan | `adg_p0_wave_plan` |
| Snapshot status | `adg_status` |
| Process info (verify restart) | `adg_runtime_info` |
| Reload latest snapshot | `adg_reload` |
| Close connections (lock release) | `adg_close_connections` |
| Reopen connections | `adg_reopen_connections` |
| **Top-N structurally central nodes (centrality MV)** | **`adg_mv_hotspot_centrality`** |
| **Blast radius (downstream impact, hops out)** | **`adg_blast_radius`** |
| **Semantic-edge fanout (`flows_to`/`writes_to`/...)** | **`adg_semantic_fanout`** |
| **Pre-classified architectural concerns (P0..P3 views)** | **`adg_p_view_query`** |

## Hard Rules

1. **`grep_search` for dependency analysis is FORBIDDEN.** Always use ADG. (Constitutional §22, §28.)
2. **MCP serialization (§25):** one MCP call per response. Plan reads accordingly.
3. **SQLite-direct fallback supersedes grep.** When MCP is blocked, query `artifacts/adg/adg_indexed_<ts>.sqlite` directly via the `sqlite3` module — NOT grep. (See `graph-analysis/SKILL.md`.)
4. **Provenance stamping required** for ADG-backed answers in plans/reports: `ADG Provenance: backend=<redis_cache|sqlite|degraded_grep>, snapshot=adg_indexed_<ts>.sqlite`.
5. **Lock protocol before MCP restart:** `adg_close_connections` → restart → `adg_reopen_connections` → `adg_health` to verify.
6. **T2/T3 work is BLOCKED** if `adg_health` is red and Redis hot cache is cold. Run `/mcp-failure-rca`.

## Common Workflows

**Hotspot-first refactoring (mandatory before drafting any T2/T3 plan):**
1. `adg_health` → green
2. `adg_violations` → P0/P1 counts by file/category
3. `adg_p0_wave_plan` → P0-first wave order
4. `adg_edge_fanin(relation_type='imports')` for top files → impact = violations × (1 + log10(1 + fan_in))
5. Drive scope from rank, not arbitrary file choice

**Branch resolution when ADG evidence is inconclusive:**

When ADG MCP returns ambiguous results (e.g., multiple hotspot candidates with similar centrality), use the enriched choice builder for the branch decision:

```python
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

# ADG returned multiple candidates — ask which to prioritize
payload = build_enriched_choice_question(
    question="ADG shows multiple hotspot candidates. Which should I refactor first?",
    options=[
        {
            "id": "A",
            "label": f"{candidate_a['name']} — higher fan-in ({candidate_a['fan_in']})",
            "description": f"Centrality: {candidate_a['centrality']:.2f}, Violations: {candidate_a['violations']}",
            "tradeoff": "Higher impact but more complex blast radius",
        },
        {
            "id": "B",
            "label": f"{candidate_b['name']} — lower centrality but safer",
            "description": f"Centrality: {candidate_b['centrality']:.2f}, Violations: {candidate_b['violations']}",
            "tradeoff": "Lower risk but less structural impact",
        },
    ],
    recommended_id="A" if candidate_a['centrality'] > candidate_b['centrality'] else None,
    telemetry_context={"adg_analysis": "hotspot_selection", "candidates": [candidate_a['id'], candidate_b['id']]},
)

# Emit telemetry (REQUIRED for enriched choices)
print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))

# Present to user
ask_user_question(
    question=payload["question"],
    options=payload["options"],
    allowMultiple=False,
)
```

**Classification:** ENRICHED_CHOICE (ADG-driven branch resolution, not governance).

**Blast radius (precomputed, fast):**
1. `adg_find_node(name='X')` → ID
2. `adg_blast_radius(node_id=ID, hops=2)` — returns `blast_radius_direct`, `blast_radius_2hop`, `reachability_rows`. Backed by the graph projection MV; warm-cache p99 <50ms.
3. Use `adg_edge_fanin` only when you need the literal edge rows.

**Refactor target ranking (graph-layer primary):**
1. `adg_mv_hotspot_centrality(limit=20)` → top-N by `degree_centrality` then `fan_in`
2. For each candidate, `adg_blast_radius(node_id=…, hops=2)` to size the impact window
3. `adg_p_view_query(view_name='v_p0_…')` to cross-reference pre-classified architectural concerns

**Semantic-edge analysis (beyond `imports`):**
- `adg_semantic_fanout(src_id=…, relation_type=…)` accepts only canonical semantic relations: `flows_to`, `writes_to`, `reads_from`, `emits_side_effect`, `controls_flow`, `resolves_callsite`. For pure `imports` use `adg_edge_fanout` instead.

## L2 Runtime-Agent Consumption Contract

Per **ADR-079**, L2 runtime agents (orchestrators, executors, healers) that consume the graph layer in production paths MUST:

1. Use either the MCP tools above OR the in-process `tools.adg.core.service.ADGService` — never raw `sqlite3.connect()`.
2. Declare `__adg_consumer_mode__ ∈ {proof, risk, inventory}` per the three-bucket authority model.
3. Honor the latency contract (warm-cache p99 <50ms; cold p99 <500ms).
4. Wrap reads in a feature-flag fallback to legacy behavior on MCP red, snapshot stale, or budget breach.
5. Cache once-per-decision (request/trace/D2-cache window), not once-per-token.

Reverse direction (L6 graph → L2 mutation) is forbidden. See ADR-079 for the canonical reference impl pattern.

## Static vs Runtime ADG

This MCP serves the **static** ADG (AST scan of source code). For runtime telemetry, healing chains, anomaly spans — use `otel_mcp`. **Do not conflate the two.**
