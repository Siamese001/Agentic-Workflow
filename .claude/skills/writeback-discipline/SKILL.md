---
name: writeback-discipline
description: Invoke when a non-trivial task completes and a writeback to file memory (procedural patterns, architectural invariants, project context) is required. Produces the exact memory-fact shapes to write. Third-person, deterministic, token-efficient.
metadata:
  enforcement_layer: cursor
  enforcement_timing: after_task_completion
  enforcement_type: behavioural
---

# Writeback Discipline Skill

**PURPOSE:** Produce ready-to-write file-memory fact shapes so writebacks are correct, consistent, and fast — no freestyling.

This skill is **templates + routing logic only**. Policy SSOT is `.claude/rules/memory-management.md` + constitutional §17 (15/3 rule).

> **Notion writeback removed (`notion-wave-enforcement-removal`).** The windsurf/cursor-era Notion
> writeback machinery (ADR / MCP / Author-Gate / Wave-Phase / SC-AP row shapes, the
> `post_agent_writeback_audit.py` hook, the `memory-notion-writeback.md` rule) never functioned and is
> retired. Durable backlog rows in Notion are an *optional manual* action only (constitutional §24);
> there is no enforced Notion writeback. Writebacks below target **file memory only**.

## When to Invoke

Invoke this skill when ANY of these triggers fire in the current response (and the work took >15 min — §17 15/3 rule):

| Trigger | Target | Template file |
|---|---|---|
| Fixed a recurring bug / diagnosed a pattern | Memory `ProceduralPattern` | `templates/memory_entity_shapes.md` §1 |
| Resolved a project blocker / changed status | Memory `ProjectContext` | `templates/memory_entity_shapes.md` §2 |
| Discovered a topology / gravity / structural rule | Memory `ArchitecturalInvariant` | `templates/memory_entity_shapes.md` §3 |

## Usage

1. **Identify trigger(s)** from the table above. Multiple may fire per response.
2. **Open the referenced template section(s)**.
3. **Fill in the shape verbatim** — keep the field set; recall depends on consistent shapes.
4. **Write the fact** to file memory (`memory/` — one fact per file + a `MEMORY.md` index line), or via the memory MCP if in use.
5. **Verify** by naming the fact slug in the response.

## Files

- `templates/memory_entity_shapes.md` — file-memory fact templates (protected types)

## Doctrine

- Memory is for **Claude Code's next-session recall** — facts must be recall-actionable ("run `python X` with flag `-n 0`"), not diary prose ("fixed the bug today").
- **Never duplicate large disk content into memory** — link to `docs/...` / a path, don't repeat it.
- **Never use a `"general"` type** for anything you want to persist — use the protected types only.
- **One writeback per trigger**. Do not split across multiple facts when one will do; do not batch unrelated triggers into one fact.
