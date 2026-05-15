---
name: memory-mcp
description: Persistent SQLite-backed knowledge graph for Cursor Agent — survives Cursor restarts. Invoke at session start (REQUIRED — constitutional §17), when the user asks about past context, before HITL decisions, when debugging modules with prior history, or when significant decisions/patterns/architectural invariants need to persist across sessions. Distinguishes the persistent memory MCP from Cursor's built-in create_memory and from vector_db (semantic search, not episodic recall). See sibling skill writeback-discipline for entity/observation shapes.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §12

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §12 — Memory MCP (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.cursor/skills/mcp-integration/SKILL.md` §12 for current guidance.

---

# Memory MCP Skill (Legacy)

In-house persistent knowledge graph. SQLite-backed at `artifacts/memory/knowledge_graph.sqlite`. Survives Cursor restarts.

**Sibling skills:** `writeback-discipline` (when/what to write), `ledger-consulter-memory-recall` (recall pattern)
**Doctrine:** `.cursor/rules/agents-memory-lifecycle.md`, `.cursor/rules/memory-management.md`

## When To Use This MCP

| User intent | Use Memory MCP? |
|---|---|
| Session start (mandatory recall) | ✅ Yes — `mem_recall_session_start` is the FIRST tool call of every session |
| User asks about past context | ✅ Yes |
| Before HITL / Author-Gate decision | ✅ Yes — load relevant ProceduralPatterns |
| After architecture decision / RCA / pattern discovery | ✅ Yes — write ProceduralPattern or ArchitecturalInvariant |
| User says "remember this" | ✅ Yes |
| Semantic similarity search | ❌ No | `vector_db` |
| Project status / wave / phase | ❌ No | `notion` |

## Tool Routing

| Goal | Tool |
|---|---|
| Session-start recall (mandatory) | `mem_recall_session_start` |
| Health probe | `memory_health` / `mem_health_check` |
| Stats | `mem_get_stats` |
| Read full graph (warning: large) | `read_graph` |
| Search entities/observations | `search_nodes` |
| Open specific entities | `open_nodes` |
| Create new entities | `create_entities` |
| Add observations to existing | `add_observations` |
| Create relations between entities | `create_relations` |
| Delete entities | `delete_entities` |
| Delete observations | `delete_observations` |
| Delete relations | `delete_relations` |
| Cleanup stale (>N days) | `mem_cleanup_stale` |
| Import ADG context | `mem_import_adg_context` |

## Entity Type Conventions (CRITICAL)

Only these types survive `mem_cleanup_stale`. Anything else (including `"general"`) is purged at 30 days:

| Type | Use |
|---|---|
| `ProceduralPattern` | Fix recipes, debugging playbooks, tool-usage patterns |
| `ProjectContext` | Active blockers, plan status, next-action |
| `ArchitecturalInvariant` | Code-topology rules that must not be violated |
| `EpisodicEvent` | Important one-time occurrences (rare — prefer ProceduralPattern) |

❌ **Never use `entityType: "general"`.** It will be purged.

## Hard Rules

1. **Constitutional §17:** First tool call of every session is `mem_recall_session_start`.
2. **15/3 Rule (writeback-discipline):** If solving took >15 min, spend up to 3 min writing back.
3. **MCP serialization (§25):** One MCP call per response — plan accordingly.
4. **Observations must be recall-actionable** — generic strings like "fixed bug" are useless to next-session Cursor Agent.
5. **Stale-source sniff test before writing `Project:*` entities.** Verify status against git log + filesystem before persisting.

## Common Workflows

**Session start:**
1. `mem_recall_session_start` → load durable entities

**After resolving recurring bug:**
1. `create_entities([{name: 'ProceduralPattern:VectorDbZombieDeadlock', entityType: 'ProceduralPattern', observations: [...recipe steps...]}])`

**Update plan status:**
1. `add_observations([{entityName: 'Project:plan-slug-6hex', contents: ['Status: W2 complete; W3 pending OAuth fix.']}])`

## Cross-Reference

Notion holds the searchable row for human audit; Memory holds the recall-actionable observation for next-session Cursor Agent. For cross-cutting decisions, write to **both** with a Notion URL inside the Memory observation.
