---
trigger: always_on
---

# MCP Serialization — Remote MCPs Only (Hardened 2026-05-01)

> ⛔ **REMOTE / network-bound MCP tool calls MUST be isolated: each remote-MCP call occupies its own `<function_calls>` block with NO sibling tool calls in that block.** Multiple such blocks may appear sequentially within a single response. Local stdio MCPs may batch freely.

## The Invariant (scoped — per-block, not per-response)

For every `<function_calls>` block in a Cascade response:

1. **Remote MCPs isolate per block.** A `<function_calls>` block containing a remote-MCP call (notion, tavily, deepwiki, context7, GitKraken — see allowlist) MUST contain **exactly one tool call** and NO sibling tools in that same block.
2. **Sequential remote-MCP blocks are fine.** A single response MAY contain multiple sequential `<function_calls>` blocks, each with one remote-MCP call, as long as each block is isolated. This enables plan-end Notion batching without forcing the user to prompt for every row.
3. **Local MCPs batch freely.** Tools from local stdio MCPs (`adg_sqlite`, `redis`, `memory`, `filesystem`, `vector_db`, `pytest_mcp`, `otel_mcp`, `task_manager`, `io.windsurf/mcp-playwright`) may batch with each other and with native tools within the same block.
4. **Mixing local MCP with remote MCP in the same block is forbidden.**
5. **Multiple remote-MCP calls in the same block is forbidden** (targeting same or different servers).

## Why scoped to remote — empirical, not deduced

Cascade has empirically observed Notion MCP calls hanging when batched with siblings; other remote/HTTP MCPs (tavily, deepwiki, context7, GitKraken) share Notion's transport profile (HTTP, third-party API) and are placed in the allowlist by analogy. Local stdio MCPs have not exhibited the hang behavior in this repo's sessions. Root cause is unisolated — see `mcp-serialization` skill for upstream issue tracking. Anthropic's *Code Execution with MCP* + *Programmatic Tool Calling* guidance explicitly endorses tool-call batching; the original "all `mcp*_` calls serialize" interpretation (2026-04 → 2026-05-01) was an over-correction. **If a local MCP starts hanging: expand the allowlist.**

## Remote MCP Allowlist (as of 2026-05-01)

| Server | Why remote | Tool-name pattern (after stripping `mcpN_` prefix) |
|---|---|---|
| `notion` | Notion REST API | `^API-` |
| `tavily` | Tavily search API | `^tavily[_-]` |
| `deepwiki` | DeepWiki API | `^(ask_question|read_wiki_)` |
| `context7` | Context7 docs API | `^(query-docs|resolve-library-id)$` |
| `GitKraken` | GitHub/GitLab/Bitbucket/Azure/Jira/Linear APIs | `^(git_|gitkraken_|gitlens_|issues_|pull_request_|repository_)` |

When in doubt: outbound HTTP to third-party = remote, serialize. Local subprocess against on-disk data = batch freely.

## Local MCP Servers (batch freely)

`adg_sqlite`, `redis`, `memory`, `filesystem`, `vector_db`, `pytest_mcp`, `otel_mcp`, `task_manager`, `io.windsurf/mcp-playwright`.

Tool prefixes (`mcp0_`, `mcp1_`, …) shift with `mcp_config.json` ordering; tool-name suffix patterns are stable per server identity — prefer suffix pattern in rule text.

## Hard Rule — SQLite-Direct Fallback Supersedes Grep (added 2026-04-26)

> ⛔ **MCP serialization is NEVER an excuse to fall back to `grep_search` for dependency analysis.** Canonical fallback hierarchy:

```
1. ADG MCP (server: adg_sqlite)       ← preferred when MCP healthy AND no other MCP call in flight
2. Direct SQLite (sqlite3 module)     ← REQUIRED when (1) blocked for ANY reason
3. grep_search                        ← FORBIDDEN for dependency analysis
```

The ADG SQLite snapshot at `artifacts/adg/adg_indexed_<ts>.sqlite` is local, deterministic, and exposes the same `nodes`/`edges`/MV surface as the MCP. Falling back from MCP to grep when SQLite is reachable is `severity: critical` (logged by `post_cascade_adg_audit.py`). DEGRADED_FALLBACK reason citing only "MCP serialization" is invalid — the SQLite tier was not exhausted.

Acceptable DEGRADED_FALLBACK reasons must satisfy ALL: (a) ADG MCP unhealthy (verified by `adg_health` red OR Redis cold sentinel), AND (b) ADG SQLite snapshot missing/locked/schema-failed with explicit error, AND (c) reason code names BOTH failure modes. Anything else = silent fallback.

For SQL examples and the canonical query template, see the `adg-sqlite` skill.

## Escape Hatch

`MCP_SERIAL_BYPASS=1` env — logs a bypass row to violations log and treats response as compliant. Use for scripted batch runs, acknowledged exploratory sessions, or post-fix verification. Every bypass durable in `artifacts/windsurf/mcp_serialization_violations.jsonl` with `reason: "bypass"`.

## Sunset + Enforcement

Auto-retires when upstream `anthropics/claude-agent-sdk-typescript#41` closes (operator writes `.windsurf/config/mcp_serialization_ttl.json`). Enforcement: this rule (advisory) + `post_cascade_mcp_serialization_audit.py` (fail-open) + `artifacts/windsurf/mcp_serialization_violations.jsonl`. Constitutional §25.
