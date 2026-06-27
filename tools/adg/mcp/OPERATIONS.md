# ADG SQLite MCP — Operator Guide

## Canonical launch path

```
python -m tools.mcp.launch_adg_sqlite_mcp
```

This supervised launcher is the only supported launch path. It runs preflight
checks, normalizes ADG environment variables, writes transport state under
`artifacts/mcp_heartbeat/`, and then starts the stdio MCP server.

It is configured in root `.mcp.json` as:
```json
"command": "python", "args": ["-u", "-m", "tools.mcp.launch_adg_sqlite_mcp"]
```

For manual Windows launches, `tools\\adg\\mcp\\run_server.bat` delegates to the
same supervised launcher after resolving the repository root and setting
`PYTHONPATH` from that root. Do not pass `ADG_DIR` from a global
`AGENTIC_REPO_ROOT`; stale values can point the MCP at another checkout.

`tools/adg/mcp/server.py` remains the internal FastMCP server implementation.
Do not point MCP config at it directly. `tools/adg/mcp/server_launcher.py` and
`tools/adg/adg_mcp_entry.py` are **deprecated** legacy wrappers retained for
emergency use only. Do not add them to `.mcp.json`.

## Restart decision table

Two distinct restart types exist. Choosing the wrong one wastes time.

| Change made | Action required | Why |
|---|---|---|
| Edited `server.py`, `service.py`, `sqlite_backend.py`, or `models.py` | **Toggle adg_sqlite OFF then ON** in legacy editor MCP Settings | legacy editor kills and respawns the subprocess, loading fresh `.py` files |
| Edited `.mcp.json` (command, args, **env**) | **Restart the MCP client session** | MCP clients read subprocess config at startup; per-server toggles can reuse a stale command. This includes `ADG_REDIS_URL` changes. |
| New SQLite snapshot available (`adg_indexed_*.sqlite`) | Call **`adg_reload`** MCP tool | Data-only reload; does not restart the process or reload code |

## Verifying a restart took effect

Out-of-band transport check:

```
python tools/mcp/check_adg_sqlite_transport.py --json
```

This check is fail-closed for Codex callability: heartbeat/process evidence is
not enough for `status=open`. It reports open only when a fresh authoritative
heartbeat is paired with `CODEX_MCP_CALLABLE_ADG_SQLITE=healthy`, which must be
set only after a live `mcp__adg_sqlite.adg_health` or `adg_runtime_info` call
succeeds in the active Codex session.

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
python .codex/governance/scripts/sync_mcp_config.py
```

Then restart the MCP client session so it reads the new command.
