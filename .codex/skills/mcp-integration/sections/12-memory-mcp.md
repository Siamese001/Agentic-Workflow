## §12 - Memory MCP

**In-house optional projection.** Persistent SQLite-backed knowledge graph at
`artifacts/memory/knowledge_graph.sqlite`. Native file memory under `memory/`
is the project SSOT; Memory MCP is useful when its transport is healthy, but it
is not a session-start gate.

### When To Use

| Intent | Use? |
|--------|------|
| Session start | Read `memory/MEMORY.md`; optionally call `mem_recall_session_start` if MCP is already healthy. |
| User asks about past context | Yes, if graph recall is useful and the transport is healthy. |
| After architecture decision/RCA | Prefer file memory writeback; mirror to MCP only when healthy. |
| Semantic similarity | No - use `vector_db`. |
| Project status/wave/phase | No - use the repo plan/filesystem or Notion when explicitly requested. |

### Tool Routing

| Goal | Tool |
|------|------|
| Optional graph recall | `mem_recall_session_start` |
| Health | `memory_health` / `mem_health_check` |
| Stats | `mem_get_stats` |
| Search | `search_nodes` |
| Open entities | `open_nodes` |
| Create entities | `create_entities` |
| Add observations | `add_observations` |
| Create relations | `create_relations` |
| Delete | `delete_entities` / `delete_observations` / `delete_relations` |
| Cleanup stale | `mem_cleanup_stale` |
| Import ADG context | `mem_import_adg_context` |

### Degraded Transport

If Memory MCP returns a transport/startup error, note `[MEMORY UNAVAILABLE]`
when relevant and continue from native file memory. Do not retry the transport
in a loop and do not treat MCP callability as proof of project-memory recall.

### Entity Types

Only these survive `mem_cleanup_stale`:

| Type | Use |
|------|-----|
| `ProceduralPattern` | Fix recipes, debugging playbooks |
| `ProjectContext` | Active blockers, plan status |
| `ArchitecturalInvariant` | Code-topology rules |
| `EpisodicEvent` | Important one-time occurrences |

Never use `entityType: "general"` for facts that should persist.

### Hard Rules

1. **Constitutional §17** - native file memory is SSOT.
2. **15/3 Rule** - if solving took >15 min, spend up to 3 min writing back.
3. **Observations must be recall-actionable.**
4. **No direct SQLite edits** - use file memory or MCP tools.

---
