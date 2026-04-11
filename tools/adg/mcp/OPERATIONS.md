# ADG SQLite MCP — Operator Restart Guide

Two distinct restart types exist. Choosing the wrong one wastes time.

## When to do what

| Change made | Action required | Why |
|---|---|---|
| Edited `server.py`, `service.py`, `sqlite_backend.py`, or `models.py` | **Toggle adg_sqlite OFF then ON** in Windsurf MCP Settings | Windsurf kills and respawns the subprocess, loading fresh `.py` files |
| Edited `.windsurf/mcp_config.json` (command, args, env, cwd) | **Fully restart Windsurf IDE** | Windsurf reads global MCP config only at IDE startup; per-server toggle reuses the command that was loaded when the IDE started |
| New SQLite snapshot available (`adg_indexed_*.sqlite`) | Call **`adg_reload`** MCP tool | Data-only reload; does not restart the process or reload code |

## Verifying a restart took effect

Call `adg_runtime_info` before and after. A genuine process restart shows:

- **`pid`** changed
- **`startup_nonce`** changed (unique per OS process spawn, not per reconnect)
- **`stack_fingerprints`** / **`combined_fingerprint`** match the current on-disk files

If `pid` and `startup_nonce` are unchanged after a toggle, the process was not respawned — check that the server status shows as reconnected, not just as connected.

## Config sync

`post_write_code` hook auto-syncs `.windsurf/mcp_config.json` → `~/.codeium/windsurf/mcp_config.json` whenever the repo file is written (detected via mtime within 10 s). Manual fallback:

```
python .windsurf/scripts/sync_mcp_config.py
```

The hook output confirms sync: `[mcp_sync] Synced N servers to global config.`
