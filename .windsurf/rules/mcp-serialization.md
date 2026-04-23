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
