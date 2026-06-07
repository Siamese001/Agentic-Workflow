## §6 — Vector DB

**In-house.** ChromaDB-backed semantic search. BAAI/bge-m3 embeddings.

### When To Use

| Intent | Use? |
|--------|------|
| "Find docs about X" — fuzzy concept | ✅ Yes |
| "What's similar to this passage?" | ✅ Yes |
| Cross-collection semantic recall | ✅ Yes |
| Structural code dependencies | ❌ NO — use `adg_sqlite` |
| Exact string match | ❌ No — use `grep_search` |
| Episodic recall | ❌ No — use `memory` MCP |

### Tool Routing

| Goal | Tool |
|------|------|
| Health probe | `readiness` |
| Server stats | `vector_stats` |
| List collections | `list_collections` |
| Collection info | `get_collection_info` |
| Create/delete collection | `create_collection` / `delete_collection` |
| Add documents | `add_documents` |
| Query collection | `query_collection` |
| Cross-collection search | `semantic_search` |
| Embed text | `embed_text` |

### Hard Rules
1. **Never use for dependency analysis** — `adg_sqlite` only
2. **Readiness check before heavy queries**
4. **Zombie-process awareness** — restart MCP if query hangs

---
