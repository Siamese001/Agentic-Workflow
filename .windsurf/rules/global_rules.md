---
trigger: always_on
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Global Rules - Always-On Policy (Tier 2 SSOT)

These are compact, always-on policy statements covering cross-cutting concerns.
Enforcement is at Tier 1 (hooks), Tier 4 (pre-commit), or Tier 5 (CI).
This file is the single source of truth for these policy topics.

## Tool Prefix Stability

Server IDs in `.windsurf/mcp_config.json` are stable. Live tool prefixes such as `mcp0_`, `mcp1_`, and `mcp2_` can shift whenever servers are added, removed, or reordered. Prefer stable server IDs plus bare tool names in documentation, and resolve the live prefix from the current tool list.

---

## MCP Green Light

Before starting ANY T2/T3 work, check ADG health in this order:
1. **Preferred**: Check Redis hot cache — `python tools/adg/adg_redis_ingest.py --check` (exit 0 = hot, fast in-memory path)
2. **Fallback**: If Redis is down or cache is cold, call `adg_health`
3. If `adg_health` is unhealthy: run `/mcp-failure-rca` and wait for recovery.

NEVER begin multi-file work with both Redis cold AND ADG MCP unhealthy.
Tier 1 enforcement: `pre_prompt_classifier.py` checks Redis sentinel first, falls back to ADG MCP probe.

---

## ADG-First Analysis

Dependency analysis MUST use ADG MCP tools - NOT grep or text search.

| Query Need | Required Tool |
|------------|---------------|
| Find by layer | `adg_nodes_by_layer` |
| Find by file | `adg_nodes_by_file` |
| Outgoing deps | `adg_edge_fanout` |
| Incoming deps | `adg_edge_fanin` |
| Node details | `adg_node` |
| Health check (before fallback) | `adg_health` |
| **MCP-down fallback (REQUIRED first)** | **Direct SQLite read of `artifacts/adg/adg_indexed_<ts>.sqlite`** — `nodes`/`edges`/`mv_*`/`v_p*` tables expose the same surface as MCP. NEVER skip this tier. |
| Degraded fallback (last resort) | grep allowed ONLY after BOTH MCP and SQLite are unreachable AND `DEGRADED_FALLBACK: reason=<mcp_err>+<sqlite_err>` is emitted |

`grep_search` for dependency analysis is FORBIDDEN. Use it only to confirm literals.
Silent degraded fallback (grep without health check + reason code) = `severity: critical` violation.

**MCP serialization (§25) is NEVER an excuse for grep.** When you cannot make a second `adg_sqlite` MCP call due to the one-MCP-per-response rule, the canonical path is direct SQLite, not grep. The fallback hierarchy is:

```
1. adg_sqlite MCP       ← preferred when MCP healthy AND no other MCP call in flight
2. sqlite3 (direct)     ← REQUIRED when (1) blocked for ANY reason
3. grep_search          ← FORBIDDEN for dep analysis regardless of (1) and (2) state
```

See `mcp-serialization.md` §"Hard Rule — SQLite-Direct Fallback Supersedes Grep" for the full snippet.

**Why this matters**: `grep_search` is a native Cascade tool with NO pre-execution hook.
Windsurf cannot programmatically block it. Enforcement relies on:
1. This rule (always_on — loaded into system prompt)
2. SR_MANDATE step 0 (injected by `pre_prompt_classifier.py` for T2/T3)
3. Retroactive detection (`post_cascade_adg_audit.py` via `post_cascade_response` hook)
Violations logged to: `artifacts/windsurf/adg_first_violations.jsonl`

---

## Hotspot-First Refactoring Gate

Before drafting ANY T2/T3 refactoring plan, AFTER the MCP green light, BEFORE any edits:

1. **Violations snapshot** — call `adg_violations` → open P0/P1 counts by file and category
2. **Wave plan** — call `adg_p0_wave_plan` → P0-first remediation ordering (address P0 before P1)
3. **Fan-in rank** — for top violation files, call `adg_edge_fanin(relation_type="imports")` → compute impact = violations × (1 + log10(1 + fan_in))
4. **Drive scope** — refactoring target selection and wave ordering MUST be derived from hotspot rank, not arbitrary file choice

FORBIDDEN: drafting a refactoring plan or wave queue without a ranked hotspot report.
Extended protocol: `adg-hotspot-enforcement.md`

---

## Graph-Layer Primary Driver (Refactoring)

The ADG is **SQLite (relational) with a graph-layer overlay** — not a native
graph database (no Neo4j/ArangoDB). The overlay — `nodes`/`edges` tables,
materialized views, P-views, semantic edges — provides graph-DB semantics
(traversals, centrality, blast radius) over a relational store. The following
graph-layer primitives MUST be PRIMARY drivers of T2/T3 refactoring plans
(in addition to raw `edges`/`violations`):

| Primitive | Purpose | Example tables/views |
|-----------|---------|----------------------|
| **Materialized views** | Pre-computed hotspot / blast-radius / chokepoint analyses | `mv_graph_reverse_dependency_hotspots`, `mv_graph_chokepoint_bridges`, `mv_graph_critical_path_blast_radius`, `mv_hotspot_centrality`, `mv_dependency_cone_risk`, `mv_path_criticality_rollup`, `mv_exemptions_near_critical_paths`, `mv_debt_concentration_hotspots` |
| **Semantic edges** | Behavior queries beyond simple imports | `flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite` |
| **Pre-built P-views** | Pre-classified architectural concerns | `v_p0_apps_direct_infra`, `v_p0_write_bypass_uwg`, `v_p1_mis_layered_infra`, `v_p1_zero_caller_infra`, `v_p2_duplicated_adapters`, `v_p3_isolated_experimental`, ... |
| **Precision tables** (when populated) | Dataflow / side-effects / call resolution | `precision_variable_attributes`, `precision_side_effects`, `precision_call_resolution` |

FORBIDDEN: a T2/T3 refactoring plan that cites only raw `edges`/`violations` counts with no materialized views, no semantic edges beyond `imports`, and no cross-reference against the P-views.

Every T2/T3 plan at `.windsurf/plans/<name>-<6hex>.md` MUST include an `## ADG_GRAPH_LAYER_EVIDENCE` section citing at least 3 materialized views, the semantic relations used, and any P-view matches. Constitutional rule §22 enforces this. Gate: `check_graph_layer_evidence.py`. Full protocol: `adg-graph-layer-enforcement.md`.

---

## Subprocess Timeout Discipline

ALL subprocess calls MUST include `timeout=`. No exceptions.

PowerShell (`powershell`, `pwsh`) is FORBIDDEN. Use `subprocess.run(argv, shell=False)`.
Tier 1 enforcement: `pre_run_gate.py` blocks PowerShell commands.

---

## Exception Handling: Column 5 Precise Exceptions

Exception handling MUST follow the Column 5 Precise Exceptions pattern.
Catch specific types with specific recovery - never `except Exception: pass`.
Reference: `docs/reference/_primers/Python/Error & Exception Handling.md`
Guardian exemptions require explicit Author-Gate approval. See Constitutional Section 8.

---

## Plans: Wave + Phase Summary Required

ALL T2/T3 plans MUST include:
1. Wave Structure table (waves, phases, focus, status)
2. Phase-Level Summary table (phase ID, title, scope, pain points, tokens, status)

A plan missing the phase-level summary table is invalid and must not be saved.
Location SSOT: `.windsurf/plans/<name>-<6hex>.md`

---

## ADG SQLite Lock Protocol

Before restarting any MCP server:
1. Call `adg_close_connections`
2. Restart MCP server
3. Call `adg_reopen_connections`
4. Verify with `adg_health`

Tier 1 enforcement: `pre_mcp_gate.py` blocks ADG calls when SQLite write lock detected.

---

## MCP Authority: One SSOT Per Capability

Each capability has exactly ONE authoritative MCP. **Full MCP routing table is in `AGENTS.md` Quick Reference section** (auto-generated, always loaded, CI-enforced). Overlap details live in `docs/guides/MCP_Registry.md`.

Before adding a new MCP, verify no existing MCP covers the capability.

**Key routing invariants**:
- Structural dependencies → `adg_sqlite` only. `grep_search` FORBIDDEN for dependency analysis.
- Persistent memory → `memory` MCP only. NOT Windsurf built-in `create_memory`.
- Semantic search → `vector_db` only. NOT for structural deps, NOT for episodic recall.
- HTTP routing follows the decision tree (no single authoritative MCP — `enhanced_http` retired 2026-04-27): external content → `tavily`; external library docs → `context7`; GitHub repo Q&A → `deepwiki`; JS-rendered pages → `playwright`; local/internal/agentic_core outbound HTTP → direct `httpx` in code; one-off URL fetch with user approval → Cascade native `read_url_content`.
- Git state / PRs / issues → `GitKraken` only.

## Continuous Execution

Execute continuously without stopping UNLESS a genuine Author-Gate decision point is reached.

FORBIDDEN: stopping after tool calls to check in; asking permission for deterministic actions; presenting options when there is one correct path; breaking work into artificial phase-breaks; narrating work-in-progress without advancing it.

REQUIRED: chain all deterministic tool calls; stop only when scoring reveals genuine decision ambiguity; validate before declaring done.