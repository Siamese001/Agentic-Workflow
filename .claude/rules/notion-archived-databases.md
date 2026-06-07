
<!-- Converted from `.claude/rules/notion-archived-databases.md`. Original Cursor trigger: `model_decision`. -->

# Notion Archived Databases — Do Not Write

> ⛔ The following Notion databases were **archived 2026-05-02** as part of the
> Notion consolidation (plan `notion-integration-consistency-audit-b2c4d8`).
> Filesystem is the sole SSOT. **No new Notion writes to these databases.**

## Archived Databases

| Database | Old IDs | Archived Reason | Filesystem SSOT |
|---|---|---|---|
| **ADR Registry** | DB `6ed25e12-...` / DS `e59d7640-...` | On-disk ADR markdown is canonical; Notion mirror was redundant and drifted | `docs/architecture/adr/*.md` |
| **MCP Registry** | DB `59693bbc-...` / DS `e7b149b4-...` | `.mcp.json` is the SSOT; Notion mirror caused drift | `.mcp.json` |
| **Constitutional Rules Registry** | DB `1c1379bc-...` / DS `9bd2523e-...` | Rules live in `.claude/rules/*.md`; Notion mirror was never reliable | `.claude/rules/*.md` |
| **SC/AP Violation Backlog** | DB `0a3b8072-...` / DS `803834e1-...` | ADG SQLite is the authoritative source; Notion mirror caused double-tracking | `artifacts/adg/*.sqlite` + violation JSON |
| **Author-Gate Decision Ledger** | DB various | SQLite ledger is the SSOT; captured via `tools/capture/append_marker.py` | `.claude/state/refactor_decisions/refactor_decision_ledger.sqlite` |
| **Anti-Pattern Burndown** | DB `80b30bc9-...` / DS `4599fe37-...` | 404 confirmed 2026-05-11 — DB not accessible to integration; filesystem ratchet files are canonical | `artifacts/adg/` ratchet files |

## What Changed

- `post_cursor_agent_adr_registry_capture.py` — now logs `kind: adr_filesystem_only` to JSONL; no Notion write
- `post_write_mcp_config_sync.py` — Notion MCP Registry sync block removed
- `memory-notion-writeback.md` auto-routing triggers 1–5 — updated to filesystem paths
- `mcp-config-ssot.md` Sync Contract — step 4 (Notion MCP Registry upsert) removed
- `_notion_constants.py` — archived DB IDs retained for reference with archival comments

## Active Databases (Do Not Archive)

| Database | Data Source ID | Purpose |
|---|---|---|
| Plans DB | `ac53d31b-3068-4039-9ebe-856c12caab32` | Plan registration, wave lifecycle, status tracking |
| Backlog Items | `fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7` | Deferred scope items, next-step capture |
| Wave/Phase Convergence | `WAVE_PHASE_DATA_SOURCE_ID` (in `_notion_constants.py`) | Phase evidence, P-band tracking |

## Hard Rules

- ❌ NEVER write to an archived DB ID — Notion silently accepts the write but the row is invisible in views
- ❌ NEVER recreate the archived databases
- ❌ NEVER add new Notion integrations without updating AGENTS.md Notion Workspace Map and this rule
- ✅ Filesystem artifacts are the recovery path for any historical data from archived DBs
- ✅ Constants in `_notion_constants.py` for archived DBs are **retained for reference** — do not delete them; they carry archival comments
- ✅ Keep **AGENTS.md** ``NOTION-MAP`` table aligned with this file (same archived vs active rows)

## References

AGENTS.md Notion Workspace Map (archived rows marked with ~~strikethrough~~). Plan `notion-integration-consistency-audit-b2c4d8`.
