---
trigger: always_on
---

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Cascade enforcement split:** Advisory guidance lives here, but deterministic detection and audit capture belong in `.windsurf/scripts/post_cascade_mcp_serialization_audit.py` and its violation log.

# MCP Serialization — Remote MCPs Only (Hardened 2026-05-01)

> ⛔ **REMOTE / network-bound MCP tool calls MUST be issued one per response, with no sibling tool calls of any kind in the same `<function_calls>` block.** Local stdio MCPs may batch freely with each other and with native tools.

## The Invariant (scoped)

For every Cascade response:

1. **Remote MCPs serialize.** If the response contains a tool call to a *remote* MCP server (notion, tavily, deepwiki, context7, GitKraken — see Remote MCP Allowlist below), it MUST contain **exactly one tool call total**.
2. **Local MCPs batch freely.** Tools from local stdio MCP servers (`adg_sqlite`, `redis`, `memory`, `filesystem`, `vector_db`, `pytest_mcp`, `otel_mcp`, `task_manager`, `io.windsurf/mcp-playwright`) may be batched with each other and with native tools (`read_file`, `edit`, `run_command`, etc.) in the same `<function_calls>` block.
3. **Mixing local MCP with remote MCP is forbidden.** If a remote MCP call is in the batch, no other tool call (local MCP or native) is allowed in the same batch.
4. Multiple remote MCP calls in the same response are also a violation, even if they target the same remote server.

## Why scoped to remote

**Empirical observation, not a deduced root cause.** This rule's scope is grounded in what hangs in this repo's Cascade sessions, not in a verified causal claim about the upstream SDK race.

- Cascade's empirical observation: **Notion MCP calls hang when batched with sibling tool calls.** Other remote/HTTP MCPs (tavily, deepwiki, context7, GitKraken) are placed in the same allowlist by analogy because they share Notion's transport profile (HTTP, third-party API, large payloads).
- Local stdio MCPs (`adg_sqlite`, `redis`, `memory`, `filesystem`, `vector_db`, `pytest_mcp`, `otel_mcp`, `task_manager`, `io.windsurf/mcp-playwright`) **have not exhibited the same hang behavior** in this repo's sessions. They batch fine.
- Possible root causes for the Notion hangs include the documented Anthropic SDK race in `anthropics/claude-agent-sdk-typescript#41` (concurrent dispatch issues), Notion API rate-limiting, large-payload serialization in the MCP proxy, or Windsurf's specific MCP client implementation. **We have not isolated which.** The rule prevents the observed behavior regardless of root-cause attribution.
- Anthropic's own Nov 2025 *Code Execution with MCP* guidance and the *Programmatic Tool Calling* feature explicitly endorse tool-call batching as the recommended pattern. Over-serializing all `mcp*_` calls (the original interpretation, used 2026-04 through 2026-05-01) is an anti-pattern: it slows turns, blocks legitimate parallelism, and pushes Cascade toward direct-SQLite fallbacks when local MCP would have worked.

**If a local MCP starts hanging in your sessions: expand the remote-MCP allowlist.** This rule is empirical; it follows the hangs.

## Remote MCP Allowlist (as of 2026-05-01)

| Server | Why remote | Tool-name pattern (after stripping `mcpN_` prefix) |
|---|---|---|
| `notion` | Notion REST API over HTTP | `^API-` |
| `tavily` | Tavily search API | `^tavily[_-]` |
| `deepwiki` | Third-party DeepWiki API | `^(ask_question|read_wiki_)` |
| `context7` | Context7 docs API | `^(query-docs|resolve-library-id)$` |
| `GitKraken` | GitHub/GitLab/Bitbucket/Azure/Jira/Linear APIs | `^(git_|gitkraken_|gitlens_|issues_|pull_request_|repository_)` |

When in doubt about a new MCP server: if it makes outbound HTTP calls to a third-party service, treat as remote and serialize. If it runs as a local subprocess against on-disk data, batch freely.

## Local MCP Servers (batch freely)

`adg_sqlite`, `redis`, `memory`, `filesystem`, `vector_db`, `pytest_mcp`, `otel_mcp`, `task_manager`, `io.windsurf/mcp-playwright` (Playwright is local stdio even though it controls a browser).

Advisory tool prefix at any given moment is determined by `.windsurf/mcp_config.json` order; tool-name suffix patterns above are stable per server identity, prefixes are not.

## Upstream tracking (candidate root causes — not confirmed)

These issues describe MCP-related hangs in the Anthropic ecosystem. Whether any of them is THE root cause of the Notion hangs in this repo is unverified.

- `anthropics/claude-agent-sdk-typescript#41` — *"SDK MCP server: 'Stream closed' errors during concurrent tool calls"*.
- `anthropics/claude-code#38437` — MCP proxy silently drops tool results.
- `anthropics/claude-code#22451` — Desktop MCP tools hang ~5 min then fail.
- `anthropics/claude-code#44032` — Silent 4-minute timeout.
- `anthropics/claude-code#26156` — Race in `ensureToolResultPairing` corrupts thinking blocks.

## Hard Rule — SQLite-Direct Fallback Supersedes Grep (added 2026-04-26)

> ⛔ **MCP serialization is NEVER an excuse to fall back to `grep_search` for dependency analysis.** The canonical fallback hierarchy is:

```
1. ADG MCP (server: adg_sqlite)       ← preferred when MCP is healthy AND no other MCP call is in flight
2. Direct SQLite (sqlite3 module)     ← REQUIRED fallback when (1) is blocked for ANY reason
3. grep_search                        ← FORBIDDEN for dependency analysis, regardless of (1) and (2) state
```

Rationale: the ADG SQLite snapshot at `artifacts/adg/adg_indexed_<timestamp>.sqlite` is local, deterministic, and serves the same `nodes`/`edges`/materialized-view surface that the `adg_sqlite` MCP exposes. Grep cannot answer dependency questions correctly (false positives, false negatives, no transitive closure, no layer awareness — see `global_rules.md` ADG-First Retrieval-Tool Decision Tree).

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

- ADG MCP unhealthy (verified by `adg_health` (server: `adg_sqlite`) showing red OR sentinel marks Redis cold), AND
- ADG SQLite snapshot file does not exist OR is locked OR schema query failed with explicit error, AND
- Reason code names BOTH the MCP failure mode AND the SQLite failure mode.

Anything else is a silent fallback.

## Escape Hatch

`MCP_SERIAL_BYPASS=1` in the environment — logs a bypass row to the violations log and treats that response as compliant. Use only for:

- Scripted batch runs where a human has accepted the risk.
- Acknowledged exploratory sessions where throughput matters more than turn reliability.
- Post-fix verification after the upstream race is resolved.

Every bypass is durable in `artifacts/windsurf/mcp_serialization_violations.jsonl` with `reason: "bypass"`.

## Sunset + Enforcement

Auto-retires when upstream `anthropics/claude-agent-sdk-typescript#41` closes. Operator writes `.windsurf/config/mcp_serialization_ttl.json` with `{"retired_after", "issue_url", "verified_by"}`; the audit script honors it. Enforcement: this rule (advisory) + `post_cascade_mcp_serialization_audit.py` (fail-open) + `artifacts/windsurf/mcp_serialization_violations.jsonl`. Constitutional tie-in: §25.
