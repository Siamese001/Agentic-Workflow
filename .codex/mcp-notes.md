# MCP server notes (legacy Claude Code compatibility)

Source of truth for MCP config is [`.mcp.json`](../.mcp.json) at repo root. This file holds the
compatibility notes that don't fit JSON.

## Bootstrap env vars
Set these as OS environment variables before launching Claude Code:
- `AGENTIC_REPO_ROOT` — absolute path to this repo root.
- `GITKRAKEN_GK_PATH` — path to the GitKraken CLI executable (for the `GitKraken` server).
- `ADG_REDIS_URL` — Redis URL for ADG hot cache (used by `adg_sqlite`, `memory`).

Claude Code expands `${VAR}` (and `${VAR:-default}`) in `.mcp.json` — note this differs from
legacy editor's `${env:VAR}` syntax.

## Auth-gated servers
- **notion** — requires `NOTION_TOKEN` (`setx NOTION_TOKEN secret_...`). Internal integration token
  from https://www.notion.so/my-integrations . Plans + Backlog DBs only (five DBs archived → filesystem SSOT).
- **context7** — no key required on free tier; optional `CONTEXT7_API_KEY` raises rate limits.

## Servers dropped after the needs-review (2026-06-07) — native substitute exists
Dropped because Claude Code's native tooling covers them; re-add the block to `.mcp.json` if you
want the structured surface back. (`tavily` also needs `TAVILY_API_KEY` from https://app.tavily.com/home.)

```jsonc
"pytest_mcp": {                         // substitute: `python -m pytest` via Bash
  "command": "python",
  "args": ["-u", "${AGENTIC_REPO_ROOT}/tools/mcp/pytest_server.py"],
  "env": { "PYTHONPATH": "${AGENTIC_REPO_ROOT}", "PYTHONUNBUFFERED": "1" }
},
"redis": {                              // substitute: `redis-cli` via Bash
  "command": "python",
  "args": ["-u", "${AGENTIC_REPO_ROOT}/tools/mcp/redis_mcp_server.py"],
  "env": { "REDIS_DB": "0", "REDIS_HOST": "localhost", "REDIS_PORT": "6379",
           "REDIS_TIMEOUT": "5", "PYTHONPATH": "${AGENTIC_REPO_ROOT}", "PYTHONUNBUFFERED": "1" }
},
"otel_mcp": {                           // on-demand: runtime trace/anomaly debugging (collector must be up)
  "command": "python",
  "args": ["-u", "${AGENTIC_REPO_ROOT}/tools/otel/otel_mcp_server.py"],
  "env": { "PYTHONPATH": "${AGENTIC_REPO_ROOT}", "PYTHONUNBUFFERED": "1",
           "OTEL_MCP_RUNTIME_ADG_DIR": "${AGENTIC_REPO_ROOT}/agentic_core/L4_state/memory/runtime_adg" }
},
"tavily": {                             // substitute: native WebSearch / WebFetch
  "command": "cmd",
  "args": ["/c", "npx", "-y", "tavily-mcp"],
  "env": { "TAVILY_API_KEY": "${TAVILY_API_KEY}" }
}
```

## Servers never migrated (were `disabled: true` in legacy editor)
- **filesystem** — shadow-disabled 2026-05-02 (Author-Gate F4, ADR-095): native file tools
  (Read/Write/Edit/Glob/Grep) fully substitute.
- **task_manager** — shadow-disabled 2026-05-02: `structured-reasoning` skill covers multi-step
  workflow needs.

## Notes carried over
- **GitKraken** is the project SSOT for git/PR MCP. GitLens duplicate disabled via
  `gitlens.gitkraken.mcp.autoEnabled=false` (see `.vscode/hooks.json`).
- **Codex Desktop startup projection**: every enabled server in root `.mcp.json` must appear in
  the Codex user config projection with `required = true`. Refresh and verify with:
  `python .codex/governance/scripts/sync_mcp_config.py --sync-user-config --json` and
  `python .codex/governance/scripts/sync_mcp_config.py --check-user-config --json`.
- **Major MCP exposure audit**: config sync is not enough. Run
  `python .codex/governance/scripts/mcp_tool_exposure_audit.py` to distinguish declared
  MCPs, native server health, and optional Codex `tool_search` exposure evidence. The
  startup set is all enabled servers in `.mcp.json`; historical route-contract snapshots do not
  prove current-session callability. Session start runs the audit in advisory mode and logs
  details to `artifacts/mcp/session_start_mcp_bootstrap.jsonl`.
- **vector_db** runtime defaults (batch sizes, timeouts) live in `tools/retrieval/vector_config.py`;
  only non-default overrides + required vars are pinned in `.mcp.json`.

## Required Windows HTTP routes

`adg_sqlite` (`http://127.0.0.1:8765/mcp`) and `memory` (`http://127.0.0.1:8766/mcp`) remain required Streamable HTTP routes. On Windows their pre-Codex lifecycle owner is the pair of current-user Scheduled Tasks defined in `ops_scripts/windows/codex_mcp_http_services.psd1`:

- `AgenticWorkflow-ADG-HTTP-MCP`
- `AgenticWorkflow-Memory-HTTP-MCP`

Install/repair with `pwsh -NoProfile -File .\ops_scripts\windows\codex_mcp_service_tasks.ps1 -Install -EnsureRunning -Json`. Verify without launching Codex with `pwsh -NoProfile -File .\ops_scripts\windows\launch_codex_agentic.ps1 -RepoRoot $PWD -NoLaunch -Json`. The supported daily entrypoint is the current-user `Codex — Agentic Workflow` shortcut created by `install_codex_agentic_shortcut.ps1`.

SessionStart is status-only because required routes initialize before the hook executes. TCP/process evidence is diagnostic only; readiness requires initialize, tools/list, and the configured health tool, while active-session acceptance additionally requires fresh endpoint-matched Codex tool proof. Foreign listeners fail closed and are never killed by lifecycle scripts.

The Scheduled Tasks and shortcut use `run_hidden_wait.vbs`, not a visible PowerShell target. The adapter waits synchronously and preserves exact exit codes. ADG's Redis dependency is `continue_degraded` with SQLite remaining authoritative; Memory's Redis dependency is `block`. Task repair compares the complete principal, action, trigger, restart, battery, execution-limit, enabled, and `IgnoreNew` fingerprint before declaring the task healthy.
- **playwright** writes browser session output to `artifacts/mcp/playwright/` (gitignored).
- **adg_sqlite** tool names appear as `mcp__adg_sqlite__<tool>` in Claude Code (e.g.
  `mcp__adg_sqlite__adg_health`).
