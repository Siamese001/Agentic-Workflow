> ⚠️ Superseded W3 (`claude-native-supersession-9d3f7a`, ADR-095): the mandatory
> `mem_recall_session_start` first-call ritual and the MCP purge/staleness gates are retired.
> Native **file-based memory** (`memory/MEMORY.md` + per-fact files) is the SSOT; the
> knowledge-graph MCP is optional for genuine graph queries. The maintenance guidance below
> applies only when the MCP is in use.


<!-- Converted from `.claude/rules/memory-management.md`. Original Cursor trigger: `model_decision`. -->

> See `CLAUDE.md` for shared retrieval / enforcement guidance.

# Memory Management Rules

## Purpose

Define discipline for maintaining a clean, performant memory graph. Prevent accumulation of stale session data that bloats queries and burns context window. Also asserts the constitutional lifecycle invariants for the memory MCP (merged 2026-05-01 from `agents-memory-lifecycle.md`).

## See First

For lifecycle (when to read, write, maintain) and tool routing, see the **`memory-mcp` skill** at `.claude/skills/memory-mcp/SKILL.md`. This rule covers maintenance policy, CI gates, and storage hygiene that are NOT in the skill.

## Constitutional Lifecycle Invariants (merged from agents-memory-lifecycle.md)

1. **Constitutional §17 — Session-start recall is mandatory.** The first tool call of every conversation MUST be `mem_recall_session_start`. Non-negotiable.
2. **15/3 Rule.** If solving a problem took >15 minutes, spend up to 3 minutes writing the procedural pattern back to file memory (`memory/`). Constitutional §17.
3. **Protected entity types only for durable persistence.** `ProceduralPattern`, `ProjectContext`, `ArchitecturalInvariant`, `ArchitectureLayer`, `ConstitutionalRule`, `ArchitecturalDecision`, `EpisodicEvent`. Any other type (especially `"general"`) is purged at the staleness threshold.
4. **No direct SQLite edits to `artifacts/memory/knowledge_graph.sqlite`.** Use the MCP tools or `tools/memory/purge_sync.py`.

> Note on tool prefixes: live `mcpN_` prefixes shift when server order changes (constitutional Tool Prefix Stability rule). Use bare tool names (`mem_recall_session_start`, `search_nodes`, `mem_cleanup_stale`) and let the runtime resolve the prefix.

## Knowledge File Hygiene

Memory-linked guidance must stay split by purpose. Avoid giant monolithic reference files that try to carry architecture, procedures, and examples in one place. If a knowledge file grows unwieldy, fragment it into smaller purpose-built documents and keep canonical repo paths explicit so future retrieval stays grounded.

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
| **Claude Code rule** | This file (`.claude/rules/memory-management.md`) |
| **Workflow** | `.claude/commands/memory-purge-sync.md` — invoke with `/memory-purge-sync` |
| **CI gate** | `ops_scripts/ci/check_memory_health.py` — daily health check |
| **Tool** | `tools/memory/purge_sync.py` — executable implementation |

## Related

- **ADG Redis refresh:** `.claude/commands/adg-redis-refresh.md`
- **ADG repair discipline:** `.claude/rules/adg-analysis-procedures.md` §5
- **Session start:** `mem_recall_session_start` loads protected types only
