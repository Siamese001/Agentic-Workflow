---
trigger: always_on
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic detection and audit capture belong in `.windsurf/scripts/post_cascade_mcp_serialization_audit.py` and its violation log.

# MCP Serialization — One MCP Call Per Response

> ⛔ **MCP tool calls (any `mcp*_` prefix) MUST be issued one per response, with no sibling tool calls of any kind in the same `<function_calls>` block.**

## The Invariant

For every Cascade response:

1. If the response contains an `mcp*_` tool call, it MUST contain **exactly one tool call total**.
2. Non-MCP tools (`read_file`, `edit`, `run_command`, `grep_search`, `search_web`, ...) may be batched freely with each other — but **never** with an MCP call.
3. Multiple MCP calls in the same response are **also** a violation (even two MCP calls of the same server).

## Why (root cause, upstream)

The Windsurf/Anthropic MCP client transport has a documented race when two or more tool calls are dispatched concurrently and at least one of them is an MCP invocation. Symptoms: the MCP call appears to hang from Cascade's vantage; the user sees a stuck turn; the MCP server itself is unaffected and healthy.

Upstream tracking:

- `anthropics/claude-agent-sdk-typescript#41` — *"SDK MCP server: 'Stream closed' errors during concurrent tool calls"* (authoritative; documents the race).
- `anthropics/claude-code#38437` — MCP proxy silently drops tool results.
- `anthropics/claude-code#22451` — Desktop MCP tools hang ~5 min then fail.
- `anthropics/claude-code#44032` — Silent 4-minute timeout.

The failure is in the **client SDK**, not in the server process or its stdio handler. Behavior shaping in Cascade's prompt is the only lever that addresses the actual mechanism until upstream ships the fix.

## Mitigation Pattern (use first, escalate to MCP second)

Prefer direct on-disk reads over MCP round-trips when the equivalent data is available locally:

| Need | Forbidden | Preferred |
|---|---|---|
| Inspect ADG node by id | `mcp1_adg_node` | `sqlite3.connect("artifacts/adg/adg_indexed_<ts>.sqlite")` then `SELECT * FROM nodes WHERE id=?` |
| List violations by category | `mcp1_adg_violations` | Same SQLite path, `SELECT ... FROM violations` |
| Read a file Cascade can reach | `mcp4_read_text_file` | Native `read_file` tool |
| Cache status spot-check | `mcp9_redis_keys` | Only when live Redis state needed; otherwise use the SQLite source of truth |
| Persistent memory recall | `mcp5_mem_recall_session_start` | No equivalent — this one MUST go through MCP (and alone in its response) |
| Notion writeback | `mcp6_API-post-page` | No equivalent — this one MUST go through MCP (and alone in its response) |

Rule of thumb: if the data lives in `artifacts/`, `.windsurf/`, or the working tree, read it directly. If it lives behind a remote API or a persistent service (Notion, memory graph, live Redis), then — and only then — issue an MCP call in its own isolated response.

## Hard Rule — SQLite-Direct Fallback Supersedes Grep (added 2026-04-26)

> ⛔ **MCP serialization is NEVER an excuse to fall back to `grep_search` for dependency analysis.** The canonical fallback hierarchy is:

```
1. ADG MCP (mcp1_adg_*)              ← preferred when MCP is healthy AND no other MCP call is in flight
2. Direct SQLite (sqlite3 module)     ← REQUIRED fallback when (1) is blocked for ANY reason
3. grep_search                        ← FORBIDDEN for dependency analysis, regardless of (1) and (2) state
```

Rationale: the ADG SQLite snapshot at `artifacts/adg/adg_indexed_<timestamp>.sqlite` is local, deterministic, and serves the same `nodes`/`edges`/materialized-view surface that `mcp1_adg_*` exposes. Grep cannot answer dependency questions correctly (false positives, false negatives, no transitive closure, no layer awareness — see `global_rules.md` ADG-First Retrieval-Tool Decision Tree).

If MCP is down OR you cannot make a second MCP call in the current response due to §25 serialization, you MUST use direct SQLite. Specifically:

```python
import sqlite3
from pathlib import Path

snapshot = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(snapshot)
cur = con.cursor()
# Imports of agentic_core.X by apps_eval files:
cur.execute("""
  SELECT COUNT(*) FROM edges e
  WHERE e.relation_type = 'imports'
    AND e.source_file LIKE 'apps_eval/%'
    AND EXISTS (SELECT 1 FROM nodes n WHERE n.id = e.dst_id AND n.resolved_path LIKE 'agentic_core/X/%')
""")
```

Falling back from MCP to grep when SQLite is reachable is a **`severity: critical`** violation logged by `post_cascade_adg_audit.py`. The DEGRADED_FALLBACK reason code is invalid if it cites only "MCP serialization" — the SQLite tier was not exhausted.

Acceptable DEGRADED_FALLBACK reasons (must include all of these conditions):

- ADG MCP unhealthy (verified by `mcp1_adg_health` showing red OR sentinel marks Redis cold), AND
- ADG SQLite snapshot file does not exist OR is locked OR schema query failed with explicit error, AND
- Reason code names BOTH the MCP failure mode AND the SQLite failure mode.

Anything else is a silent fallback.

## Escape Hatch

`MCP_SERIAL_BYPASS=1` in the environment — logs a bypass row to the violations log and treats that response as compliant. Use only for:

- Scripted batch runs where a human has accepted the risk.
- Acknowledged exploratory sessions where throughput matters more than turn reliability.
- Post-fix verification after the upstream race is resolved.

Every bypass is durable in `artifacts/windsurf/mcp_serialization_violations.jsonl` with `reason: "bypass"`.

## Sunset

This rule **auto-retires** when upstream `anthropics/claude-agent-sdk-typescript#41` closes and the Windsurf client ships the fix. Procedure:

1. Operator writes `.windsurf/config/mcp_serialization_ttl.json` with `{"retired_after": "<UTC-date>", "issue_url": "...", "verified_by": "<name>"}`.
2. `post_cascade_mcp_serialization_audit.py` reads that file; after `retired_after` it no-ops.
3. Set this rule's front-matter to `trigger: manual` with a deprecation banner; remove from always-on load after one full review cycle.

Same lifecycle shape as the deprecated `hitl-*` shim rules (see `.windsurf/RULES_INDEX.md`).

## Enforcement

- **Rule (this file)** — advisory; always-on; shapes composition every turn.
- **Post-response audit** — `.windsurf/scripts/post_cascade_mcp_serialization_audit.py` — deterministic; appends to `artifacts/windsurf/mcp_serialization_violations.jsonl`; fail-open (exit 0 on any internal error).
- **Violations log** — never silently truncated; session-start surfacer (future) may display running count to pressure convergence.

## Constitutional Tie-in

Constitutional rule §26 codifies the invariant. See `constitutional.md`.
