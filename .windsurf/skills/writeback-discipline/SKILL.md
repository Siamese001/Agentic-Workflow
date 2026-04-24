---
name: writeback-discipline
description: Invoke when a non-trivial task completes and a writeback to Memory MCP (procedural patterns, architectural invariants, project context) or Notion MCP (ADRs, wave/phase status, Author-Gate decisions, MCP registry changes, SC/AP violations) is required. Produces the exact entity shapes and row shapes to paste into the respective MCP calls. Third-person, deterministic, token-efficient.
metadata:
  enforcement_layer: windsurf
  enforcement_timing: after_task_completion
  enforcement_type: behavioural
---

# Writeback Discipline Skill

**PURPOSE:** Produce ready-to-paste Memory entity shapes and Notion row shapes so writebacks are correct, consistent, and fast — no freestyling.

This skill is **templates + routing logic only**. Policy SSOT is `memory-notion-writeback.md` rule; deterministic enforcement is the `post_cascade_writeback_audit.py` hook.

## When to Invoke

Invoke this skill when ANY of these triggers fire in the current response:

| Trigger | Target | Template file |
|---|---|---|
| Fixed a recurring bug / diagnosed a pattern | Memory `ProceduralPattern` | `templates/memory_entity_shapes.md` §1 |
| Resolved a project blocker / changed status | Memory `ProjectContext` | `templates/memory_entity_shapes.md` §2 |
| Discovered a topology / gravity / structural rule | Memory `ArchitecturalInvariant` | `templates/memory_entity_shapes.md` §3 |
| Created/ratified an ADR | Notion ADR Registry | `templates/notion_row_shapes.md` §1 |
| Modified `.windsurf/mcp_config.json` or a gate | Notion MCP Registry | `templates/notion_row_shapes.md` §2 |
| Resolved a scored `ask_user_question` | Notion Author-Gate Decision Ledger | `templates/notion_row_shapes.md` §3 |
| Plan wave/phase status changed | Notion Wave/Phase Convergence | `templates/notion_row_shapes.md` §4 |
| New SC/AP violations from ADG run | Notion SC/AP Violation Backlog | `templates/notion_row_shapes.md` §5 |

## Usage

1. **Identify trigger(s)** from the table above. Multiple may fire per response.
2. **Open the referenced template section(s)**.
3. **Fill in the shape verbatim** — do not reshape fields; Notion validation will 400 on schema drift.
4. **Execute the write** via `memory.create_entities` / `memory.add_observations` / `notion.API-post-page` / `notion.API-patch-page`.
5. **Verify** by echoing the returned ID back in the response so the post_cascade hook can confirm the writeback landed.

## Files

- `templates/memory_entity_shapes.md` — Memory MCP entity templates (4 protected types)
- `templates/notion_row_shapes.md` — Notion row templates keyed to the 8 canonical databases from `@c:/Git/Agentic-Workflow/AGENTS.md`

## Writeback Receipt Format

After every writeback, emit a compact receipt line so `post_cascade_writeback_audit.py` sees it:

```
WRITEBACK: target=<memory|notion>, kind=<entity_type|database_name>, id=<entity_name|page_id>
```

Example:
```
WRITEBACK: target=memory, kind=ProceduralPattern, id=ProceduralPattern:QwenVLLMTopology
WRITEBACK: target=notion, kind=MCPRegistry, id=33f27693-f55c-812b-8f73-e49069c78280
```

The hook parses these receipts; missing receipts when a trigger fired → violation logged.

## Doctrine

- Memory is for **Cascade's next-5-minutes recall** — observations must be recall-actionable ("run `python X` with flag `-n 0`"), not diary prose ("fixed the bug today").
- Notion is for **human audit over days/weeks** — rows carry typed properties (status, date, owner), not narrative.
- **Never duplicate disk content into Notion** — row links to `docs/...` file, doesn't repeat it.
- **Never use `entityType: "general"`** for anything you want to persist — 30-day auto-purge applies. Use the 4 protected types only.
- **One writeback per trigger**. Do not split across multiple entities when one will do; do not batch unrelated triggers into one entity.
