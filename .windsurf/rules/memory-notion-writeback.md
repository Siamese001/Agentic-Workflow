---
trigger: model_decision
description: Apply when non-trivial work completes and a writeback to Memory MCP (procedural patterns, invariants) or Notion MCP (ADRs, wave/phase status, MCP registry, decisions) is required. Demoted from always_on 2026-05-01 per Anthropic two-tier compliance.
---

# Memory ↔ Notion Writeback — Invariant-Only Stub

## Invariant

When solving a problem took >15 minutes (T2/T3 per constitutional Tier Classification), spend up to 3 minutes writing back. **The 15/3 rule is non-negotiable.**

## Where to write — quick decision

| Will Cascade need it next session? | Will a human audit it across days? | Target |
|---|---|---|
| ✅ | ❌ | **Memory MCP** only (`ProceduralPattern:*` / `ProjectContext:*`) |
| ❌ | ✅ | **Notion MCP** only (specific database per AGENTS.md routing) |
| ✅ | ✅ | **Both** — compact Memory entity with Notion URL in observations |
| ❌ | ❌ | Neither — disk artifact suffices |

## Auto-routing triggers (proactive)

These events fire writeback without a prompt:

1. New `docs/architecture/adr/ADR-*.md` → Notion ADR Registry
2. `.windsurf/mcp_config.json` change → Notion MCP Registry
3. Gate behavior change in `.windsurf/scripts/*_gate.py` → Notion MCP Registry Notes
4. Resolved scored `ask_user_question` → Notion Author-Gate Decision Ledger
5. New SC/AP defects from `generate_full_adg.py` → Notion SC/AP Violation Backlog (one row per new violation)
6. New plan file in `.windsurf/plans/` → Memory `Project:<plan-slug>`
7. Recurring bug or anti-pattern diagnosis → Memory `ProceduralPattern:*`

## Where the procedural detail lives

| Concern | Location |
|---|---|
| Full decision table + entity types + DB IDs | `.windsurf/skills/writeback-discipline/SKILL.md` + `AGENTS.md` Notion Workspace Map |
| Memory MCP usage | `.windsurf/skills/memory-mcp/SKILL.md` + `memory-management.md` |
| Auto-capture hook | `.windsurf/scripts/post_cascade_writeback_audit.py` |
| Stale-source sniff test | (this rule was SSOT — full text preserved in git history at HEAD~1) |
| Bypass | `WRITEBACK_AUDIT_BYPASS=1` |

## Forbidden patterns

- Notion narrative duplicating disk content (row should link, not repeat)
- `entityType: "general"` for anything intended to persist (auto-purged at 30 days)
- Skipping writeback because "it's small" — if 15/3 triggered, it's required
- Writing Project:* / Wave row without the stale-source sniff test (precedent: 2026-04-22 false-block)

## Constitutional cross-reference

§17 (Memory lifecycle mandatory). Sibling rule `.windsurf/rules/deferred-scope-capture.md` covers `DEFERRED_SCOPE:` markers (constitutional §24).
