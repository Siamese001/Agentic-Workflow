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
**Doctrine:** `.windsurf/rules/adg-canonical-invariants.md`, `.windsurf/rules/adg-graph-layer-enforcement.md`

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

**Blast radius:**
1. `adg_find_node(name='X')` → ID
2. `adg_edge_fanin(src_id=ID, relation_type='imports')` → who depends on X
3. Recursive trace via repeated fan-in queries

## Static vs Runtime ADG

This MCP serves the **static** ADG (AST scan of source code). For runtime telemetry, healing chains, anomaly spans — use `otel_mcp`. **Do not conflate the two.**
