---
trigger: model_decision
description: Apply when reading or writing the persistent memory knowledge graph, purging stale entities, or deciding when to call the memory MCP at session boundaries.
---

> **Cascade enforcement split:** Advisory guidance lives here, but deterministic blocking, fail-closed checks, and audit capture belong in hooks and scripts rather than prompt prose.

# Memory Lifecycle (constitutional pointer)

The full lifecycle (when to read, when to write, entity-type conventions, tool routing) lives in the **`memory-mcp` skill** at `.windsurf/skills/memory-mcp/SKILL.md`. This rule asserts the constitutional invariants only.

## Constitutional Invariants

1. **Constitutional §17 — Session-start recall is mandatory.** The first tool call of every conversation MUST be `mem_recall_session_start`. Non-negotiable.
2. **15/3 Rule.** If solving a problem took >15 minutes, spend up to 3 minutes writing the procedural pattern back to memory. Skipping this is a violation of `memory-notion-writeback.md`.
3. **Protected entity types only for durable persistence.** `ProceduralPattern`, `ProjectContext`, `ArchitecturalInvariant`, `ArchitectureLayer`, `ConstitutionalRule`, `ArchitecturalDecision`, `EpisodicEvent`. Any other type (especially `"general"`) is purged at the staleness threshold — see `memory-management.md` for the maintenance protocol.
4. **No direct SQLite edits to `artifacts/memory/knowledge_graph.sqlite`.** Use the MCP tools or `tools/memory/purge_sync.py`.

## See Also

- **How-to:** `.windsurf/skills/memory-mcp/SKILL.md` — full tool routing, entity shapes, common workflows
- **Maintenance / CI:** `.windsurf/rules/memory-management.md` — purge thresholds, health gates, evidence trail
- **Writeback decision tree:** `.windsurf/rules/memory-notion-writeback.md` — Memory vs Notion vs neither
