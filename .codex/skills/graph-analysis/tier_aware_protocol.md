# Tier-Aware Protocol

## Tier Table

| Tier | Scope | ADG Requirement | Evidence Required |
|---|---|---|---|
| **T0 — Question** | No code changes | Use ADG hot cache if available | None |
| **T1 — Trivial** | ≤1 file, ≤20 lines | ADG cache query optional | No `DEPENDENCY_GRAPH` section |
| **T2 — Scoped** | 2–5 files, single layer | Query ADG cache for blast radius | Brief scope note with graph justification |
| **T3 — Architectural** | >5 files, cross-layer | Full ADG protocol | `## DEPENDENCY_GRAPH` section mandatory |

## T2 Protocol

1. Check Redis hot cache: `python tools/adg/adg_redis_ingest.py --check`
2. If hot: query `mcp__adg_sqlite__adg_edge_fanout` for each changed file
3. Confirm blast radius is contained to single layer
4. Emit brief scope note in evidence

## T3 Protocol

1. Verify ADG MCP health: `mcp__adg_sqlite__adg_health`
2. Build full dependency graph for all affected nodes
3. Run fan-out and fan-in for each root node
4. Identify cross-layer edges, cycles, and boundary violations
5. Emit `## DEPENDENCY_GRAPH` section (see `impact_analysis_template.md`)
6. Verify scope against `scope_validation_checklist.md`

## ADG MCP Quick Reference

| Query Need | Tool |
|---|---|
| Find by layer | `mcp__adg_sqlite__adg_nodes_by_layer` |
| Find by file | `mcp__adg_sqlite__adg_nodes_by_file` |
| Outgoing deps | `mcp__adg_sqlite__adg_edge_fanout` |
| Incoming deps | `mcp__adg_sqlite__adg_edge_fanin` |
| Node details | `mcp__adg_sqlite__adg_node` |
