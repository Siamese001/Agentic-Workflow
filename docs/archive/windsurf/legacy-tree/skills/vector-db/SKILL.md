---
name: vector-db
description: Semantic search, embeddings, and vector collection management via the in-house vector_db MCP server (ChromaDB-backed). Invoke for fuzzy/conceptual matching, "find similar X", or when keywords would miss semantic relatives. Distinguishes vector_db (semantic similarity) from adg_sqlite (structural code dependencies — FORBIDDEN replacement) and from grep_search (exact match). Wraps tools/mcp/vector_db_server.py.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §6

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §6 — Vector DB (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.windsurf/skills/mcp-integration/SKILL.md` §6 for current guidance.

---

# Vector DB Skill (Legacy)

In-house. ChromaDB-backed semantic search via BAAI/bge-m3 embeddings.

## When To Use This MCP

| User intent | Use vector_db? |
|---|---|
| "Find docs about X" — fuzzy concept | ✅ Yes |
| "What's similar to this passage?" | ✅ Yes |
| Cross-collection semantic recall | ✅ Yes |
| Structural code dependencies | ❌ NO — use `adg_sqlite` |
| Exact string match | ❌ No | `grep_search` |
| Episodic recall ("what did we decide last session") | ❌ No | `memory` MCP |

## Tool Routing

| Goal | Tool |
|---|---|
| Health probe | `readiness` |
| Server stats | `vector_stats` |
| List collections | `list_collections` |
| Collection info | `get_collection_info` |
| Create collection | `create_collection` |
| Delete collection | `delete_collection` |
| Add documents | `add_documents` |
| Query a single collection | `query_collection` |
| Cross-collection semantic search | `semantic_search` |
| Embed text (return vectors) | `embed_text` |

## Hard Rules

1. **Never use for dependency analysis.** Constitutional rule — `adg_sqlite` is the only authority.
2. **Readiness check before heavy queries.** `readiness` returns model warmup state; `query_collection` during prewarm will block-wait up to the timeout.
3. **MCP serialization (§25):** One MCP call per response.
4. **Zombie-process awareness:** If `query_collection` hangs, multiple `vector_db_server.py` processes may be deadlocked on ChromaDB SQLite WAL. The server now self-cleans via `_kill_zombie_siblings()` on startup, but if a query stalls, restart the MCP.

## Common Workflows

**Semantic search across all collections:**
1. `readiness` → confirm `model_loaded=true`
2. `semantic_search(query='...', n_results=5)` → cross-collection top-N

**Targeted collection query:**
1. `query_collection(collection_name='docs', query_text='...', n_results=10, where={'category': 'arch'})`

**Add documents:**
1. `add_documents(collection_name='docs', documents=[...], metadatas=[...], ids=[...])`

## Configuration

- Embedding model: BAAI/bge-m3 (loaded lazily via DeferredLoader, ~6s warm time from cache)
- ChromaDB persist path: `data/cache/chromadb/`
- Tokenizer parallelism: disabled (`TOKENIZERS_PARALLELISM=false`)
- Zombie-sibling cleanup runs on startup (opt out: `VECTOR_DB_SKIP_ZOMBIE_KILL=1`)
