---
trigger: model_decision
description: Apply when reading or writing the persistent memory knowledge graph, purging stale entities, or deciding when to call the memory MCP at session boundaries.
---

> **Claude always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries, routing cues, and non-negotiable standards here. Move long procedures, examples, templates, and execution playbooks into skills or workflows.
>
> **Claude retrieval discipline:** When this rule affects research or synthesis, prefer local-first retrieval, exact or structural matches before broad semantic search, and evidence or quote extraction before final synthesis on high-risk tasks.
>
> **Claude enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Memory Lifecycle

The `memory` MCP server provides **persistent, cross-session knowledge** via a SQLite-backed knowledge graph. Unlike Windsurf's built-in `create_memory`, this survives IDE restarts and supports structured entities, relations, and observations.

## When to Read (mandatory)

| Trigger | Action |
|---------|--------|
| **Start of every conversation** | Call `mem_recall_session_start` to load persistent project context (layers, constitutional rules, architectural decisions). This is the **first tool call** in any session. |
| User asks "what do you know about X", "past decisions", "project context" | Call `search_nodes(query=X)` or `open_nodes(names=[...])` |
| Before HITL decisions | Call `search_nodes` to check for historical precedent on similar decisions |
| Debugging or investigating a module | Call `search_nodes` with module/layer name to retrieve stored context |

## When to Write (proactive)

| Trigger | Action |
|---------|--------|
| **Significant architecture decision made** | `create_entities` with `entityType="ArchitecturalDecision"` + observations describing the decision, rationale, and outcome |
| **HITL decision resolved** | `add_observations` to record the chosen option and reasoning |
| **New pattern or convention established** | `create_entities` with `entityType="ProceduralPattern"` |
| **User explicitly says "remember this"** | `create_entities` or `add_observations` |
| **After ADG regeneration** | `mem_import_adg_context` to refresh layer/project context |
| **Refactor or major change completed** | `add_observations` to the affected entity with outcome and lessons learned |

## When to Maintain

| Trigger | Action |
|---------|--------|
| Weekly or after major milestones | `mem_cleanup_stale(older_than_days=7)` to prune session-scoped entities |
| Memory health check needed | `mem_get_stats` to inspect entity/observation/relation counts |
| After ADG regeneration + cleanup | `mem_import_adg_context` to re-seed fresh context |

## Entity Type Conventions

| Type | Purpose | Protected |
|------|---------|-----------|
| `ArchitectureLayer` | L0–L6 layer definitions | Yes |
| `ProjectContext` | Project metadata (e.g., `Project:ADG`) | Yes |
| `ConstitutionalRule` | Governance rules | Yes |
| `ArchitecturalDecision` | ADR-level decisions | Yes |
| `ProceduralPattern` | Established patterns/conventions | Yes |
| `EpisodicEvent` | Session-scoped events (purgeable after 7d) | Yes |
| *(other)* | General/session entities | No — pruned by `mem_cleanup_stale` |

## References

- Full maintenance protocol: `.windsurf/rules/memory-management.md`
- Authority definition: constitutional §17 (memory lifecycle mandatory)
