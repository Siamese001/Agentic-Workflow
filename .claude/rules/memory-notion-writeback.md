
<!-- Converted from `.claude/rules/memory-notion-writeback.md`. Original Cursor trigger: `model_decision`. -->

# Memory ↔ Notion Writeback — Invariant-Only Stub

## Invariant

When solving a problem took >15 minutes (T2/T3 per constitutional Tier Classification), spend up to 3 minutes writing back. **The 15/3 rule is non-negotiable.**

## Where to write — quick decision

| Will Claude Code need it next session? | Will a human audit it across days? | Target |
|---|---|---|
| ✅ | ❌ | **Memory MCP** only (`ProceduralPattern:*` / `ProjectContext:*`) |
| ❌ | ✅ | **Notion MCP** only (specific database per AGENTS.md routing) |
| ✅ | ✅ | **Both** — compact Memory entity with Notion URL in observations |
| ❌ | ❌ | Neither — disk artifact suffices |

## Auto-routing triggers (proactive)

These events fire writeback without a prompt:

1. New `docs/architecture/adr/ADR-*.md` → **filesystem SSOT only** (ADR Registry archived 2026-05-02; on-disk markdown is the sole canonical record)
2. `.mcp.json` change → **filesystem SSOT only** (MCP Registry archived 2026-05-02; no Notion write)
3. Gate behavior change in `.claude/governance/scripts/*_gate.py` → commit message + Memory MCP only (MCP Registry archived 2026-05-02)
4. Resolved scored `ask_user_question` → `.claude/state/refactor_decisions/refactor_decision_ledger.sqlite` via `tools/capture/append_marker.py` (Author-Gate Decision Ledger archived 2026-05-02)
5. New SC/AP defects from `generate_full_adg.py` → `artifacts/adg/*.sqlite` + violation JSON (SC/AP Violation Backlog archived 2026-05-02; no Notion write)
6. New plan file in `plans/` (or legacy `.claude/plans/`) → Memory `Project:<plan-slug>` + Notion Plans DB row (§36)
7. Recurring bug or anti-pattern diagnosis → Memory `ProceduralPattern:*`

## Where the procedural detail lives

| Concern | Location |
|---|---|
| Full decision table + entity types + DB IDs | `.claude/skills/writeback-discipline/SKILL.md` + `AGENTS.md` Notion Workspace Map |
| Memory MCP usage | `.claude/skills/memory-mcp/SKILL.md` + `memory-management.md` |
| Auto-capture hook | `.claude/governance/scripts/post_cursor_agent_writeback_audit.py` |
| Stale-source sniff test | (this rule was SSOT — full text preserved in git history at HEAD~1) |
| Bypass | `WRITEBACK_AUDIT_BYPASS=1` |

## Forbidden patterns

- Notion narrative duplicating disk content (row should link, not repeat)
- `entityType: "general"` for anything intended to persist (auto-purged at 30 days)
- Skipping writeback because "it's small" — if 15/3 triggered, it's required
- Writing Project:* / Wave row without the stale-source sniff test (precedent: 2026-04-22 false-block)

## Constitutional cross-reference

§17 (Memory lifecycle mandatory). Sibling rule `.claude/rules/deferred-scope-capture.md` covers `DEFERRED_SCOPE:` markers (constitutional §24).
