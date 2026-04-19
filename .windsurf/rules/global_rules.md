---
trigger: always_on
---

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
| Degraded fallback | grep allowed ONLY after health red — emit `DEGRADED_FALLBACK: reason=<...>` |

`grep_search` for dependency analysis is FORBIDDEN. Use it only to confirm literals.
Silent degraded fallback (grep without health check + reason code) = `severity: critical` violation.

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

## Subprocess Timeout Discipline

ALL subprocess calls MUST include `timeout=`. No exceptions.

PowerShell (`powershell`, `pwsh`) is FORBIDDEN. Use `subprocess.run(argv, shell=False)`.
Tier 1 enforcement: `pre_run_gate.py` blocks PowerShell commands.

---

## Exception Handling: Column 5 Precise Exceptions

Exception handling MUST follow the Column 5 Precise Exceptions pattern.
Catch specific types with specific recovery - never `except Exception: pass`.
Reference: `docs/reference/Python/Error & Exception Handling.md`
Guardian exemptions require explicit HITL approval. See Constitutional Section 8.

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
- Programmatic HTTP → `enhanced_http` only. Use `read_url_content` ONLY when user approval of the URL is required.
- Git state / PRs / issues → `GitKraken` only.

## Continuous Execution

Execute continuously without stopping UNLESS a genuine HITL decision point is reached.

FORBIDDEN: stopping after tool calls to check in; asking permission for deterministic actions; presenting options when there is one correct path; breaking work into artificial phase-breaks; narrating work-in-progress without advancing it.

REQUIRED: chain all deterministic tool calls; stop only when scoring reveals genuine decision ambiguity; validate before declaring done.