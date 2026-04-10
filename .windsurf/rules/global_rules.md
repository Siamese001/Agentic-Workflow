---
trigger: always_on
---

# Global Rules - Always-On Policy (Tier 2 SSOT)

These are compact, always-on policy statements covering cross-cutting concerns.
Enforcement is at Tier 1 (hooks), Tier 4 (pre-commit), or Tier 5 (CI).
This file is the single source of truth for these policy topics.

---

## MCP Green Light

Before starting ANY T2/T3 work, check ADG health in this order:
1. **Preferred**: Check Redis hot cache — `python tools/adg/adg_redis_ingest.py --check` (exit 0 = hot, fast in-memory path)
2. **Fallback**: If Redis is down or cache is cold, call `mcp1_adg_health`
3. If `mcp1_adg_health` is unhealthy: run `/mcp-failure-rca` and wait for recovery.

NEVER begin multi-file work with both Redis cold AND ADG MCP unhealthy.
Tier 1 enforcement: `pre_prompt_classifier.py` checks Redis sentinel first, falls back to ADG MCP probe.

---

## ADG-First Analysis

Dependency analysis MUST use ADG MCP tools - NOT grep or text search.

| Query Need | Required Tool |
|------------|---------------|
| Find by layer | `mcp1_adg_nodes_by_layer` |
| Find by file | `mcp1_adg_nodes_by_file` |
| Outgoing deps | `mcp1_adg_edge_fanout` |
| Incoming deps | `mcp1_adg_edge_fanin` |
| Node details | `mcp1_adg_node` |

`grep_search` for dependency analysis is FORBIDDEN. Use it only to confirm literals.

**Why this matters**: `grep_search` is a native Cascade tool with NO pre-execution hook.
Windsurf cannot programmatically block it. Enforcement relies on:
1. This rule (always_on — loaded into system prompt)
2. SR_MANDATE step 0 (injected by `pre_prompt_classifier.py` for T2/T3)
3. Retroactive detection (`post_cascade_adg_audit.py` via `post_cascade_response` hook)
Violations logged to: `artifacts/windsurf/adg_first_violations.jsonl`

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
1. Call `mcp1_adg_close_connections`
2. Restart MCP server
3. Call `mcp1_adg_reopen_connections`
4. Verify with `mcp1_adg_health`

Tier 1 enforcement: `pre_mcp_gate.py` blocks ADG calls when SQLite write lock detected.

---

## MCP Authority: One SSOT Per Capability

Each capability has exactly ONE authoritative MCP. Overlaps documented in `docs/reference/MCP_Registry.md`.
Before adding a new MCP, verify no existing MCP covers the capability.

Known authority assignments:
- File reads: `filesystem` (local), `github` (remote)
- HTTP requests: `read_url_content` (simple GETs, native Cascade tool), `enhanced_http` (POST, auth, batch, advanced)
- Project context: `adg_sqlite` (structural), `memory` (episodic)