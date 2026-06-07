# MCP server notes (Claude Code)

Source of truth for MCP config is [`.mcp.json`](../.mcp.json) at repo root. This file holds the
operational notes that don't fit JSON. Migrated from `.cursor/mcp.json` (Cursor legacy).

## Bootstrap env vars
Set these as OS environment variables before launching Claude Code:
- `AGENTIC_REPO_ROOT` — absolute path to this repo root.
- `GITKRAKEN_GK_PATH` — path to the GitKraken CLI executable (for the `GitKraken` server).
- `ADG_REDIS_URL` — Redis URL for ADG hot cache (used by `adg_sqlite`, `memory`).

Claude Code expands `${VAR}` (and `${VAR:-default}`) in `.mcp.json` — note this differs from
Cursor's `${env:VAR}` syntax.

## Auth-gated servers
- **notion** — requires `NOTION_TOKEN` (`setx NOTION_TOKEN secret_...`). Internal integration token
  from https://www.notion.so/my-integrations . Plans + Backlog DBs only (five DBs archived → filesystem SSOT).
- **tavily** — requires `TAVILY_API_KEY` (`setx TAVILY_API_KEY tvly-...`). Key from
  https://app.tavily.com/home . Free tier: 1000 credits/month.
- **context7** — no key required on free tier; optional `CONTEXT7_API_KEY` raises rate limits.

## Servers NOT migrated (were `disabled: true` in Cursor — active-only scope)
- **filesystem** — shadow-disabled 2026-05-02 (Author-Gate F4, ADR-095): native file tools
  (Read/Write/Edit/Glob/Grep) fully substitute. Re-add to `.mcp.json` if needed.
- **task_manager** — shadow-disabled 2026-05-02: `structured-reasoning` skill covers multi-step
  workflow needs. Re-add to `.mcp.json` if needed.

## Notes carried over
- **GitKraken** is the project SSOT for git/PR MCP. GitLens duplicate disabled via
  `gitlens.gitkraken.mcp.autoEnabled=false` (see `.vscode/settings.json`).
- **vector_db** runtime defaults (batch sizes, timeouts) live in `tools/retrieval/vector_config.py`;
  only non-default overrides + required vars are pinned in `.mcp.json`.
- **playwright** writes browser session output to repo-root `.playwright-mcp/` (gitignored).
- **adg_sqlite** tool names appear as `mcp__adg_sqlite__<tool>` in Claude Code (e.g.
  `mcp__adg_sqlite__adg_health`).
