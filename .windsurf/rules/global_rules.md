---
trigger: always_on
---

# Global Rules - Always-On Policy (Tier 2 SSOT)

## Tool Prefix Stability

Server IDs in `.windsurf/mcp_config.json` are stable. Live tool prefixes (`mcp0_`, `mcp1_`, …) shift when servers are added/removed/reordered. Prefer stable server IDs + bare tool names in documentation; resolve the live prefix from the current tool list.

## MCP Green Light

Before ANY T2/T3 work, check ADG health: (1) **preferred** Redis hot cache via `python tools/adg/adg_redis_ingest.py --check`; (2) **fallback** `adg_health`; (3) if unhealthy, run `/mcp-failure-rca`. NEVER begin multi-file work with both Redis cold AND ADG MCP unhealthy. Tier 1 enforcement: `pre_prompt_classifier.py`.

## ADG-First Analysis

Dependency analysis MUST use ADG MCP tools — NOT grep/text search. Fallback hierarchy: (1) `adg_sqlite` MCP → (2) direct SQLite of `artifacts/adg/adg_indexed_<ts>.sqlite` → (3) grep ONLY if both unreachable AND `DEGRADED_FALLBACK: reason=<mcp_err>+<sqlite_err>` emitted.

Key tools: `adg_nodes_by_layer`, `adg_nodes_by_file`, `adg_edge_fanout`/`adg_edge_fanin`, `adg_node`, `adg_health`. `grep_search` for dependency analysis FORBIDDEN — only confirm literals. Silent fallback = `severity: critical` in `adg_first_violations.jsonl`. `adg_sqlite` is local — call freely per response (§25 applies to remote MCPs only).

## Hotspot-First Refactoring Gate

Before drafting ANY T2/T3 refactoring plan, AFTER MCP green light, BEFORE edits: (1) `adg_violations` for P0/P1 counts; (2) `adg_p0_wave_plan` for P0-first ordering; (3) `adg_edge_fanin(relation_type="imports")` for top files → impact = violations × (1 + log10(1 + fan_in)); (4) drive scope from hotspot rank, not arbitrary file choice. FORBIDDEN: drafting a refactoring plan or wave queue without a ranked hotspot report. Extended protocol: `adg-hotspot-enforcement.md`.

## Graph-Layer Primary Driver (Refactoring)

T2/T3 refactoring plans MUST use graph-layer primitives as PRIMARY drivers: materialized views (`mv_graph_reverse_dependency_hotspots`, `mv_hotspot_centrality`, `mv_dependency_cone_risk`, etc.), semantic edges (`flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite`), and P-views (`v_p0_*`..`v_p3_*`). FORBIDDEN: plans citing only raw `edges`/`violations`. Every T2/T3 plan MUST include `## ADG_GRAPH_LAYER_EVIDENCE` (≥3 MVs + semantic edges + P-view matches). Gate: `check_graph_layer_evidence.py`. Detail: `adg-graph-layer-enforcement.md`.

## Subprocess Timeout Discipline

ALL subprocess calls MUST include `timeout=`. PowerShell (`powershell`, `pwsh`) is FORBIDDEN — use `subprocess.run(argv, shell=False)`. Tier 1: `pre_run_gate.py`.

## Exception Handling: Column 5 Precise Exceptions

Catch specific types with specific recovery — never `except Exception: pass`. Reference: `docs/reference/_primers/Python/Error & Exception Handling.md`. Guardian exemptions require explicit Author-Gate approval per constitutional §8.

## Plans: Wave + Phase Summary Required

ALL T2/T3 plans MUST include (1) Wave Structure table (waves, phases, focus, status); (2) Phase-Level Summary table (phase ID, title, scope, pain points, tokens, status). A plan missing either is invalid. SSOT: `.windsurf/plans/<slug>-<6hex>.md`.

## ADG SQLite Lock Protocol

Before restarting any MCP server: (1) `adg_close_connections`; (2) restart; (3) `adg_reopen_connections`; (4) verify with `adg_health`. Tier 1: `pre_mcp_gate.py` blocks ADG calls when SQLite write lock detected.

## MCP Authority: One SSOT Per Capability

Each capability has exactly ONE authoritative MCP. Full table: `AGENTS.md` Quick Reference. Before adding a new MCP, verify no existing MCP covers the capability.

**Key routing invariants:**
- Structural dependencies → `adg_sqlite` only. `grep_search` FORBIDDEN.
- Persistent memory → `memory` MCP only. NOT Windsurf built-in `create_memory`.
- Semantic search → `vector_db` only. NOT for structural deps, NOT for episodic recall.
- HTTP routing: external content → `tavily`; external library docs → `context7`; GitHub repo Q&A → `deepwiki`; JS-rendered pages → `playwright`; local/internal HTTP → direct `httpx`; one-off URL fetch → `read_url_content`.
- Git state / PRs / issues → `GitKraken` only.

## Continuous Execution

Execute continuously without stopping UNLESS a genuine Author-Gate decision point is reached. FORBIDDEN: stopping after tool calls, asking permission for deterministic actions, presenting options when there is one correct path. See `author-gate-enforcement.md` for bypass conditions.
