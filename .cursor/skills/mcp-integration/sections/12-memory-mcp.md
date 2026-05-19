## §12 — Memory MCP

**In-house.** Persistent SQLite-backed knowledge graph. Survives Cursor restarts.

### When To Use

| Intent | Use? |
|--------|------|
| Session start (mandatory) | ✅ Yes — `mem_recall_session_start` is FIRST call |
| User asks about past context | ✅ Yes |
| Before HITL/Author-Gate | ✅ Yes |
| After architecture decision/RCA | ✅ Yes |
| Semantic similarity | ❌ No — `vector_db` |
| Project status/wave/phase | ❌ No — `notion` |

### Tool Routing

| Goal | Tool |
|------|------|
| Session start | `mem_recall_session_start` |
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

### Entity Types (CRITICAL)

Only these survive `mem_cleanup_stale`:

| Type | Use |
|------|-----|
| `ProceduralPattern` | Fix recipes, debugging playbooks |
| `ProjectContext` | Active blockers, plan status |
| `ArchitecturalInvariant` | Code-topology rules |
| `EpisodicEvent` | Important one-time occurrences |

❌ **Never use `entityType: "general"`** — purged at 30 days.

### Hard Rules
1. **Constitutional §17** — first tool call is `mem_recall_session_start`
2. **15/3 Rule** — if solving took >15 min, spend up to 3 min writing back
3. **Observations must be recall-actionable**

---
