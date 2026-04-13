# ADG SQLite MCP — Operator Guide

## Canonical launch path

```
python -m tools.adg.mcp.server
```

This is the only supported launch path — configured in `.windsurf/mcp_config.json` as:
```json
"command": "python", "args": ["-m", "tools.adg.mcp.server"]
```

`tools/adg/mcp/server_launcher.py` and `tools/adg/adg_mcp_entry.py` are **deprecated** legacy wrappers retained for emergency use only. Do not add them to `mcp_config.json`.

## Restart decision table

Two distinct restart types exist. Choosing the wrong one wastes time.

| Change made | Action required | Why |
|---|---|---|
| Edited `server.py`, `service.py`, `sqlite_backend.py`, or `models.py` | **Toggle adg_sqlite OFF then ON** in Windsurf MCP Settings | Windsurf kills and respawns the subprocess, loading fresh `.py` files |
| Edited `.windsurf/mcp_config.json` (command, args, **env**, cwd) | **Fully restart Windsurf IDE** | Windsurf reads global MCP config only at IDE startup; per-server toggle reuses the stale command. This includes `ADG_DIR` and `ADG_REDIS_URL` changes. |
| New SQLite snapshot available (`adg_indexed_*.sqlite`) | Call **`adg_reload`** MCP tool | Data-only reload; does not restart the process or reload code |

## Verifying a restart took effect

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
`artifacts/windsurf/adg_first_violations.jsonl` with `severity: critical`.

## ADG generation lock-release workflow

Use this sequence when the ADG needs full regeneration while Windsurf is running:

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

`post_write_code` hook auto-syncs `.windsurf/mcp_config.json` → `~/.codeium/windsurf/mcp_config.json` whenever the repo file is written (detected via mtime within 10 s). Manual fallback:

```
python .windsurf/scripts/sync_mcp_config.py
```

The hook output confirms sync: `[mcp_sync] Synced N servers to global config.`
