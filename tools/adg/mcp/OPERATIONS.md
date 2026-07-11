# ADG SQLite MCP — Operator Guide

## Canonical launch path

```
python -m tools.mcp.launch_adg_sqlite_http_mcp
```

This persistent Streamable HTTP launcher is the primary supported Codex route.
It runs preflight checks, normalizes ADG environment variables, writes launcher
state under `artifacts/mcp_heartbeat/`, writes service JSONL receipts under
`artifacts/mcp/`, and then starts the FastMCP Streamable HTTP service.

It is configured in root `.mcp.json` as:
```json
"url": "http://127.0.0.1:8765/mcp"
```

The legacy stdio launcher remains available only as a fallback/probe:

```
python -m tools.mcp.launch_adg_sqlite_mcp
```

For manual Windows stdio fallback launches, `tools\\adg\\mcp\\run_server.bat`
delegates to the supervised stdio launcher after resolving the repository root
and setting `PYTHONPATH` from that root. Do not pass `ADG_DIR` from a global
`AGENTIC_REPO_ROOT`; stale values can point the MCP at another checkout.

`tools/adg/mcp/server.py` remains the internal FastMCP server implementation.
Do not point MCP config at it directly. `tools/adg/mcp/server_launcher.py` and
`tools/adg/adg_mcp_entry.py` are **deprecated** legacy wrappers retained for
emergency use only. Do not add them to `.mcp.json`.

On startup, the supervised launcher performs an ADG-only pre-guard cleanup for
older launcher siblings under the same Codex parent process. This is narrower
than the shared heartbeat guard: cross-window siblings are preserved, but stale
same-parent launchers from a Codex restart cannot keep owning heartbeat files
or split the stdio route. A currently running broken transport must be restarted
to load this launcher code.

The HTTP launcher does not kill existing stdio processes. If the HTTP service is
down, restart only the repo-managed HTTP MCP service and then prove a live Codex
HTTP route call. Do not use process liveness, heartbeat files, or direct SQLite
preflight as active-session proof.

## Restart decision table

Two distinct restart types exist. Choosing the wrong one wastes time.

| Change made | Action required | Why |
|---|---|---|
| Edited `server.py`, `service.py`, `sqlite_backend.py`, or `models.py` | **Restart the repo-managed ADG HTTP MCP service** | The persistent service must reload edited Python code |
| Edited `.mcp.json` route URL | **Restart/reload the MCP client session once** | MCP clients read route URLs at startup; service restarts do not update client config |
| New SQLite snapshot available (`adg_indexed_*.sqlite`) | Call **`adg_reload`** MCP tool | Data-only reload; does not restart the process or reload code |

## Verifying a restart took effect

Out-of-band transport check:

```
python tools/mcp/check_adg_sqlite_transport.py --json
python scripts/governance/probe_mcp_http_server.py --url http://127.0.0.1:8765/mcp --tool adg_health --json
```

This check is fail-closed for Codex callability: heartbeat/process evidence is
not enough for `status=open`. For the HTTP route, ADG opens only when the
current-session callability ledger
`artifacts/mcp/codex_mcp_callability_proofs.json` contains a fresh
`route_kind=http` proof for `adg_sqlite`, the proof endpoint matches
`http://127.0.0.1:8765/mcp`, and the tool is one of
`adg_health`, `adg_runtime_info`, or `adg_process_identity`.

Legacy `CODEX_MCP_CALLABLE_ADG_SQLITE=healthy` and attached-PID proof can help
diagnose stdio fallback behavior, but it does not open the primary HTTP route
because it cannot prove the active Codex client used the configured URL.

Ordinary T2/T3 prompts are blocked while this check is not open; explicit ADG
transport recovery/RCA prompts may proceed so the route can be repaired.

For duplicate-cohort cleanup, use:

```
python scripts/governance/cleanup_duplicate_mcp_cohorts.py --json
```

Codex-owned cleanup remains blocked unless explicit attached-PID proof is
provided. The cleanup script matches ADG, memory, and vector Python MCPs only by
direct module/script argv entries, so diagnostic commands that merely contain a
marker string are not treated as MCP launchers.

Call `adg_runtime_info` before and after. A genuine process restart shows:

- **`pid`** changed
- **`startup_nonce`** changed (unique per OS process spawn, not per reconnect)
- **`stack_fingerprints`** / **`combined_fingerprint`** match the current on-disk files

If `pid` and `startup_nonce` are unchanged after a toggle, the process was not respawned — check that the server status shows as reconnected, not just as connected.

## Routing and selection policy

All structural graph queries **must** use `adg_sqlite` tools first. `grep_search` is FORBIDDEN as a
first-choice tool for dependency analysis.

| Query type | Required tool | grep allowed? |
|---|---|---|
| imports / consumers / blast radius / fanin / fanout | `mcp1_adg_edge_fanin` / `mcp1_adg_edge_fanout` | **NO** |
| function / class / constant name in `*.py` | `mcp1_adg_find_node` → `mcp1_adg_edge_fanin` | **NO** |
| Layer analysis (L0–L6) | `mcp1_adg_nodes_by_layer` | **NO** |
| File-level deps | `mcp1_adg_nodes_by_file` | **NO** |
| Semantic / concept / meaning-based | `vector_db` semantic_search | explicit fallback only |
| Runtime traces / spans / anomalies | `otel_mcp` | — |
| Literal text / TODOs / comments / non-Python | `grep_search` / `filesystem` | ✅ always OK |

### Health-first rule

Before using `grep_search` as a fallback for any graph query:
1. Call `mcp1_adg_health`
2. If status is red/unavailable, fallback is allowed — **but must** emit `DEGRADED_FALLBACK: reason=<adg_red|snapshot_missing|...>` in the response
3. If status is ok, `adg_sqlite` MUST be used — no fallback permitted

**Silent grep-for-graph** (no health check + no reason code) is a policy violation logged to
`artifacts/cursor/adg_first_violations.jsonl` with `severity: critical`.

## ADG generation lock-release workflow

Use this sequence when the ADG needs full regeneration while legacy editor is running:

```
1. adg_close_connections      # releases SQLite file lock; returns closed=true
2. python tools/generate_full_adg.py   # writes new adg_indexed_<timestamp>.sqlite
3. adg_reopen_connections     # creates fresh ADGService; returns reopened=true
   (or: adg_reload            # if only the snapshot changed, not source code)
```

**Key semantics:**
- `adg_close_connections` — tears down the service (`_service = None`), releases all file handles. A subsequent query auto-reinitialises the service, but will pick up the old snapshot unless `adg_reload` or `adg_reopen_connections` is called first.
- `adg_reopen_connections` — creates a new `ADGService` pointing at the latest snapshot on disk. Use this after regeneration to guarantee the fresh snapshot is active.
- `adg_reload` — keeps the running service but repoints SQLite to the newest snapshot file. Use this when you only have a new snapshot and haven't regenerated from scratch.
- **Do not** call `adg_reopen_connections` and `adg_reload` together; `adg_reopen_connections` already initialises on the latest snapshot.

## Config sync

Root `.mcp.json` is the project MCP SSOT. After editing it, validate and sync
generated references:

```
python .codex/governance/scripts/sync_mcp_config.py --check
python .codex/governance/scripts/sync_mcp_config.py --dry-run
python .codex/governance/scripts/sync_mcp_config.py --sync-user-config
```

Then perform one controlled MCP client config reload so it reads the new URL
route.

## HTTP recovery sequence

Use this order when ADG reports `Transport closed` or `codex_http_route_unproven`:

1. Run `python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json`.
2. If the class is `http_service_down`, restart only `python -m tools.mcp.launch_adg_sqlite_http_mcp`.
3. If the class is `http_protocol_unhealthy`, inspect `artifacts/mcp/adg_sqlite_http_service.jsonl` and rerun the HTTP probe above.

## Windows lifecycle owner

Normal Windows operation uses Scheduled Task `AgenticWorkflow-ADG-HTTP-MCP`, defined by `ops_scripts/windows/codex_mcp_http_services.psd1` and run through `run_codex_http_mcp_service.ps1`. Install or repair it together with Memory, then prove the real health tool:

```powershell
pwsh -NoProfile -File .\ops_scripts\windows\codex_mcp_service_tasks.ps1 -Install -EnsureRunning -Json
python scripts/governance/probe_mcp_http_server.py --url http://127.0.0.1:8765/mcp --tool adg_health --json
```

The runner state is `artifacts/mcp/adg_sqlite_windows_runner.json`; stdout, stderr, and service events are under `artifacts/mcp/adg_sqlite_http_*`. Redis has a bounded `continue_degraded` policy for ADG because SQLite remains authoritative. The task and child service enter through the synchronous `run_hidden_wait.vbs` adapter, which prevents console windows while preserving task ownership and exit codes. A listener whose PID does not match the runner or launcher receipt is a foreign-port conflict and is never terminated automatically.

To verify restart-on-failure, first capture `service_pid` from `-Status -Json`, confirm ownership is `managed`, stop only that verified task-owned PID, wait at least the configured one-minute restart interval, then rerun status and the probe. A different PID plus initialize, tools/list, and `adg_health` success is the restart proof. This direct HTTP proof still does not replace a live endpoint-matched Codex tool call.
4. If the class is `codex_http_route_unproven`, reload/reconnect the Codex MCP client once, then call live `mcp__adg_sqlite.adg_health` or `mcp__adg_sqlite.adg_process_identity`.
5. Record the recovery receipt only after a fresh active-session proof exists. Process liveness, heartbeat freshness, direct SQLite, port-open, curl, and tools/list are diagnostics only.
