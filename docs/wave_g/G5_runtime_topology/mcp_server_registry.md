# G5 — MCP Server Registry and Runtime Topology

wave: G5
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
upstream_artefacts:
  - .mcp.json
  - docs/wave_g/G2b_provider_gateway/mcp_as_transport.md
  - docs/wave_g/G4b_control_plane/config_knob_catalogue.yaml

ADG snapshot timestamp used: `04182026_0814`.

## Registry summary

- Total configured MCP servers: **12**
- Transport split (reconciled):
  - **9** local stdio servers
  - **2** local binary-subprocess launchers
  - **1** pure external HTTPS endpoint

## Server matrix

| Stable server ID | Launch command/url | Runtime class | Transport | External egress | Health/readiness surface |
|---|---|---|---|---|---|
| `adg_sqlite` | `python -u -m tools.adg.mcp.server` | python stdio subprocess | stdio loopback | local Redis optional | `adg_health`, `adg_status`, `adg_runtime_info` |
| `memory` | `python -u tools/memory/adg_memory_server.py` | python stdio subprocess | stdio loopback | local Redis optional | `mem_recall_session_start`, `mem_get_stats` |
| `vector_db` | `python -u tools/mcp/vector_db_server.py` | python stdio subprocess | stdio loopback | conditional HF egress when download enabled | `readiness`, `vector_stats` |
| `otel_mcp` | `python -u tools/otel/otel_mcp_server.py` | python stdio subprocess | stdio loopback | none (query/ingest local artefacts) | `otel_status`, `otel_server_info` |
| `redis` | `python -u tools/mcp/redis_mcp_server.py` | python stdio subprocess | stdio loopback | localhost Redis | `redis_health`, `redis_namespace_stats` |
| `pytest_mcp` | `python -u tools/mcp/pytest_server.py` | python stdio subprocess | stdio loopback | none | `discover_tests`, `list_pytest_config` |
| `enhanced_http` | `python -u tools/mcp/enhanced_http_server.py` | python stdio subprocess | stdio loopback | yes, arbitrary HTTP by design | `test_connectivity`, request-level failures |
| `notion` | `cmd /c npx -y @notionhq/notion-mcp-server` | node stdio subprocess | stdio loopback | yes (`api.notion.com`) | `API-get-self` |
| `task_manager` | `cmd /c npx -y @blizzy/mcp-task-manager stdio` | node stdio subprocess | stdio loopback | none | `task_info` |
| `filesystem` | `node .codex/governance/scripts/filesystem_mcp_launcher.js <repo_root>` | binary subprocess | node wrapper stdio | none | launcher readiness marker + startup watchdog |
| `GitKraken` | `${env:GITKRAKEN_GK_PATH} mcp --host=codex ...` | binary subprocess | vendor bridge | conditional to git providers | `git_status` |
| `deepwiki` | `https://mcp.deepwiki.com/mcp` | external endpoint | HTTPS MCP | yes (remote endpoint) | endpoint connectivity |

## MCP env injection classes by server

| Server | Main injected env classes |
|---|---|
| `adg_sqlite` | `mcp_runtime_env`, `path_override`, `runtime_tunable` |
| `memory` | `mcp_runtime_env`, `path_override`, `runtime_tunable` |
| `vector_db` | `mcp_runtime_env`, `path_override`, `runtime_tunable`, `feature_flag` |
| `redis` | `mcp_runtime_env`, `path_override`, `runtime_tunable`, `secret` (optional password) |
| `notion` | `mcp_runtime_env`, `secret` (`NOTION_TOKEN`) |
| `enhanced_http` / `pytest_mcp` / `otel_mcp` / `task_manager` | mostly `mcp_runtime_env` bootstrap vars |
| `filesystem` / `GitKraken` | launcher path/env tokens rather than repo runtime knobs |

## Process boundaries that matter operationally

1. MCP subprocesses are **not** repo app runtime processes; they are IDE-launched operators.
2. `deepwiki` is the only zero-subprocess remote endpoint in registry.
3. `vector_db` readiness and warm state are process-local; stale/zombie process duplication can produce lock/hang behavior in local Chroma path.
4. `otel_mcp` has explicit stale-process probe (`otel_server_info.source_is_stale`) before restart decisions.
5. `filesystem` launcher enforces a startup timeout and child cleanup, reducing orphan process risk.

## Startup dependencies (MCP-specific)

- `adg_sqlite` needs latest ADG snapshot; Redis is optional acceleration.
- `memory` depends on SQLite path and optionally Redis hot cache for ADG import tooling.
- `vector_db` depends on Chroma path and embedding model warmup.
- `redis` MCP depends on local Redis availability at configured host/port/db.
- `notion`, `GitKraken`, `deepwiki`, `enhanced_http` depend on external network egress.

## Restart semantics (MCP-specific)

- Most MCP servers: restart by legacy editor process lifecycle.
- ADG snapshot freshness can be advanced without full restart via `adg_reload`.
- OTel stale-source detection: inspect `otel_server_info` before restart.
- Unknown/opaque restart internals: `GitKraken` and external `deepwiki` service.

## Ambiguities explicitly retained

- Exact persistence model for `task_manager` subprocess is external-tool-owned and not repo-authored.
- `GitKraken` credential and retry internals are outside repo source control.
- `deepwiki` uptime/SLA and remote failure causes are external to repo runtime ownership.
