---
plan_id: adg-mcp-reopen-hardening-e8f9a0
plan_type: infra
---

# ADG MCP Reopen Hardening (Planning Only)

- **Status**: Planning — Author-Gate pending
- **Authored**: 2026-05-02
- **Backlog rows**: 3 P2 rows (max impact 254) — "adg-mcp-reopen-hardening" cluster

## Context (SCQA)

- **Situation** — `adg_sqlite` MCP holds SQLite write-locks that block `tools/generate_full_adg.py` from regenerating snapshots. The documented workflow (`/adg-redis-refresh`) requires `adg_close_connections` → regenerate → `adg_reopen_connections`. The reopen step fails silently in some conditions; operators have reported hung MCP restarts.
- **Complication** — silent reopen failures break the ADG freshness invariant (rule `adg-sqlite-lock-protocol`). The MCP stays "healthy" per `adg_health` but serves stale data.
- **Question** — how to make the reopen path observable, idempotent, and lock-aware?
- **Answer** — this plan scopes: (1) a lock-state probe helper in `adg_sqlite` MCP server, (2) a reopen handshake that refuses to report healthy until snapshot path + mtime + node_count are verified fresh, (3) a Windsurf hook emitting a warning when `adg_reload` is called without a preceding `adg_close_connections`.

## Wave Structure

| Wave | Phase IDs | Focus | Tokens | Status |
|---|---|---|---:|---|
| W1 | P0 | Author-Gate approval | ~500 🟢 | Pending |
| W2 | P1 | Lock-state probe + reopen handshake | ~5 000 🟡 | Blocked on W1 |
| W3 | P2 | Windsurf hook (advisory warning) | ~2 000 🟢 | Blocked on W2 |
| W4 | P3 | Integration test: restart-under-lock scenario | ~3 000 🟢 | Blocked on W2 |

## Out Of Scope

- Schema changes to SQLite snapshot — that's `tools/generate_full_adg.py` scope
- MCP protocol changes — stay within `adg_sqlite` server's existing tool surface
- Redis hot-cache changes — separate `/adg-redis-refresh` workflow

## Author-Gate Trade-offs

- **AG-1**: Reopen semantics — (a) wait with timeout, (b) fail fast, (c) retry with backoff. ⭐ Recommended: (c) retry with exponential backoff up to 30s total, then fail fast with structured error.
- **AG-2**: Freshness proof — compare `(path, mtime, node_count)` triple vs `(path, snapshot_id, node_count)` triple. ⭐ Recommended: snapshot_id (cryptographic — immune to mtime manipulation).

## Success Criteria

- [ ] `adg_close_connections` → regen → `adg_reopen_connections` round-trip verifiable in one pytest fixture
- [ ] Silent reopen failure impossible (health endpoint refuses healthy until verified)
- [ ] 3 backlog rows flip Completed after W2 + W3 land

## References

- Rule: `.windsurf/rules/adg-repair-discipline.md`
- MCP server: `tools/mcp/adg_sqlite_server.py`
- Tracker plan: `.windsurf/plans/d-bucket-w3-burndown-b3d5e2.md`
- Companion workflow: `.windsurf/workflows/adg-redis-refresh.md`
