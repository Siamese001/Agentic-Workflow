# Codex MCP Dormant Server Policy

Generated: 2026-06-10  
Plan: `codex-mcp-transport-parity-4b9c7e` W3  
Scope: dormant/re-add MCP server parity for Codex.

## W3 Result

W3 is complete. Codex must not silently treat any dormant server as live. The
current authority remains:

| Source | Role |
|---|---|
| `.mcp.json` | Live Claude MCP server SSOT; these dormant servers are intentionally absent |
| `.codex/mcp-notes.md` | Exact re-add blocks for dormant servers |
| `.codex/skills/mcp-integration/sections/*.md` | Access ladders, substitutes, and safety rules |
| `C:\Users\amita\env\.env` | Local credential storage for `TAVILY_API_KEY` |

## Evidence Snapshot

| Check | Result |
|---|---|
| `redis-cli` | `C:\Program Files\Redis\redis-cli.EXE`; `PING` returned `PONG` |
| `ADG_REDIS_URL` | Set in the current Codex environment |
| `tools/adg/adg_redis_ingest.py --help` | Exposes `--check`, `--dry-run`, and `--force` |
| `tools/adg/adg_redis_ingest.py --check` in eval worktree | Failed because `C:\Git\eval-harness\artifacts\adg` is absent |
| Primary ADG artifacts | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg` exists |
| `TAVILY_API_KEY` | Set in current environment; also present in `C:\Users\amita\env\.env` line 79, length 41 |
| `python -m pytest --version` | `pytest 9.0.2` |
| Dormant server scripts | `tools/mcp/pytest_server.py`, `tools/mcp/redis_mcp_server.py`, `tools/otel/otel_mcp_server.py`, and `tools/adg/adg_redis_ingest.py` all compile |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD` | Unset in current shell; repo policy requires setting it for test runs |
| `OTEL_MCP_RUNTIME_ADG_DIR` | Unset in current shell; re-add block supplies it from `${AGENTIC_REPO_ROOT}` |

## Dormant Policy Matrix

| Server ID | `.mcp.json` Status | Current Storage / Re-add SSOT | Current Substitute | Re-add Prerequisites | Codex Policy |
|---|---|---|---|---|---|
| `redis` | Absent as standalone server | `.codex/mcp-notes.md` `redis` block; `mcp-integration` Redis section | `redis-cli` for standalone cache inspection; ADG graph access through `adg_sqlite`; Redis hot projection via `ADG_REDIS_URL` | Local Redis on `localhost:6379`; `tools/mcp/redis_mcp_server.py`; `PYTHONPATH=${AGENTIC_REPO_ROOT}` | Do not expose standalone Redis as live unless explicitly re-added. SQLite remains ADG canonical; mutate/warm projection via `tools/adg/adg_redis_ingest.py`, not ad hoc key writes. |
| `tavily` | Absent | `.codex/mcp-notes.md` `tavily` block; local key in `C:\Users\amita\env\.env` | Claude: native WebSearch/WebFetch. Codex: Tavily plugin tools when exposed, otherwise web tooling with degraded note. | `TAVILY_API_KEY`; `npx -y tavily-mcp` from re-add block | Do not claim raw `tavily` MCP availability in Codex unless re-added. Use only for external web content, not repo code or structural analysis. |
| `pytest_mcp` | Absent | `.codex/mcp-notes.md` `pytest_mcp` block; pytest policy in repo governance | `python -m pytest` with repo pytest policy | `tools/mcp/pytest_server.py`; `PYTHONPATH=${AGENTIC_REPO_ROOT}`; `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` for runs | Keep dormant. For Codex verification, run direct pytest commands with plugin autoload disabled and no weakened assertions/skips. |
| `otel_mcp` | Absent, on-demand only | `.codex/mcp-notes.md` `otel_mcp` block; OTel section of `mcp-integration` | No live substitute for trace/anomaly MCP; use static ADG for static dependency analysis | Collector/runtime trace source must be running; `OTEL_MCP_RUNTIME_ADG_DIR=${AGENTIC_REPO_ROOT}/agentic_core/L4_state/memory/runtime_adg` | Keep dormant/on-demand. First live health call after re-add is `otel_server_info`; do not use it for static graph work. |

## Redis Storage Answer

Standalone Redis MCP is not stored in `.mcp.json`. Its exact re-add definition is
stored in `.codex/mcp-notes.md`. Runtime Redis connectivity is stored in
environment variables, primarily `ADG_REDIS_URL` for ADG/memory and
`REDIS_HOST`/`REDIS_PORT`/`REDIS_DB` in the dormant re-add block. Redis data is a
hot projection/cache; ADG SQLite artifacts remain canonical. Cache population
and mutation go through `tools/adg/adg_redis_ingest.py`.

## Tavily Storage Answer

Tavily MCP is not stored in `.mcp.json`. Its exact re-add definition is stored in
`.codex/mcp-notes.md`. The local Tavily credential is present in
`C:\Users\amita\env\.env` as `TAVILY_API_KEY` and is also set in the current
Codex environment. Codex may use Tavily plugin tools when exposed, but that is a
plugin substitute, not proof that the dormant raw MCP is live.

## Guardrails

- A dormant server row must always include `dormant`, `substitute`, and `re-add`
  fields before it is considered compliant.
- Re-adding a dormant server requires copying the exact block from
  `.codex/mcp-notes.md` and satisfying every listed env/script prerequisite.
- Substitutes must be labeled as substitutes, even when they cover the same user
  workflow.
- Redis cache mutation must be script-mediated; direct key inspection is allowed
  only for diagnosis and must not make Redis authoritative over SQLite.
- OTel is runtime/on-demand only. Static dependency, blast-radius, and layer
  analysis stay with `adg_sqlite`.
