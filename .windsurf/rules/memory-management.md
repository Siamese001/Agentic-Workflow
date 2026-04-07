---
trigger: always_on
---
# Memory Management Rules

## Purpose

Define discipline for maintaining a clean, performant memory graph. Prevent accumulation of stale session data that bloats queries and burns context window.

## Rule 1: Protected Types Never Deleted

The following entity types are **protected** and never purged:

| Type | Purpose |
|------|---------|
| `ArchitectureLayer` | L0–L6 layer definitions (durable structure) |
| `ProjectContext` | Project metadata like `Project:ADG` |
| `ConstitutionalRule` | Fundamental governance rules |

**Enforcement:** `mem_cleanup_stale` automatically skips these types.

## Rule 2: Staleness Threshold

Entities are considered stale when:
- Age > 7 days (`older_than_days=7`)
- Type is NOT in protected list

Stale entities are purged during memory sync.

## Rule 3: Purge Sync Trigger

**When to run memory purge sync:**

1. **Primary trigger:** After every ADG regeneration
2. **Historical frequency:** Every 3–7 days (based on ADG regen patterns)
## CI Integration

Memory health is checked via CI gate:
- Daily health check: `python ops_scripts/ci/check_memory_health.py`
- Triggers manual purge when threshold exceeded
- Blocks commits if memory corruption detected

Manual trigger: When `check_memory_health.py` reports warning

**Never run purge sync:**
- During active repair loops (risk of losing triage context)
- Without fresh ADG available (cannot re-import context)

## Rule 4: Health Thresholds

CI gate `check_memory_health.py` warns when:
- Entity count > 500
- Oldest non-protected entity age > 14 days

**Healthy state:** < 500 entities, all ages < 14 days, protected types intact.

## Rule 5: Evidence Trail

Every purge sync must produce evidence:
- Before/after statistics
- Purged entity count
- Reduction percentage
- Timestamp

Location: `docs/reports/telemetry/memory_purge_YYYYMMDD_HHMMSS.json`

## Rule 6: ADG Context Import

After purge, always re-import fresh ADG context:
- `Project:ADG` with current timestamp
- `Layer:L0` through `Layer:L6`
- Relations linking layers to project

This ensures `mem_recall_session_start` has current data.

## Rule 7: No Manual Database Edits

**Forbidden:**
- Direct SQL edits to `knowledge_graph.sqlite`
- Manual deletion of entities via SQLite tools
- Bypassing `mem_cleanup_stale` or `purge_sync.py`

**Required:** Always use the purge sync tool or MCP memory tools.

## Enforcement

| Layer | Mechanism |
|-------|-----------|
| **Windsurf rule** | This file (`.windsurf/rules/memory-management.md`) |
| **Workflow** | `.windsurf/workflows/memory-purge-sync.md` — invoke with `/memory-purge-sync` |
| **CI gate** | `ops_scripts/ci/check_memory_health.py` — daily health check |
| **Tool** | `tools/memory/purge_sync.py` — executable implementation |

## Related

- **ADG Redis refresh:** `.windsurf/workflows/adg-redis-refresh.md`
- **ADG repair discipline:** `.windsurf/rules/adg-repair-discipline.md`
- **Session start:** `mem_recall_session_start` loads protected types only
