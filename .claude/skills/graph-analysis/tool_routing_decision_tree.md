# Retrieval-Tool Decision Tree — ADG-First Routing

> **Source**: OpenDev paper §3.2 — "Encoding a retrieval-tool decision tree directly into the
> agent's prompt reduced unnecessary grep calls. The key is that the decision criteria must be
> concrete and anchored to observable features of the query."

## STOP-AND-ROUTE: Before ANY Search

**Before calling `grep_search`, check these conditions IN ORDER.**
**If ANY condition matches → use the ADG MCP tool instead. No exceptions.**

### Decision Tree (keyed on observable query features)

```
QUERY: "Who imports / from X import / consumers of module X?"
  └─ Observable: query contains import/from/consumer/reference + module/file path
  └─ ROUTE → mcp__adg_sqlite__adg_nodes_by_file(file_path=X) → mcp__adg_sqlite__adg_edge_fanin(tgt_id=<node_id>, relation_type="imports")
  └─ NEVER → grep_search("from X import") or grep_search("import X")

QUERY: "Who calls function Y / uses class Y / references symbol Y?"
  └─ Observable: query targets a specific function, class, or constant name
  └─ ROUTE → mcp__adg_sqlite__adg_node(node_id=<symbol>) → mcp__adg_sqlite__adg_edge_fanin(tgt_id=<node_id>, relation_type="calls")
  └─ NEVER → grep_search("Y(") or grep_search("class Y")

QUERY: "What does Z depend on / what does Z import?"
  └─ Observable: query asks about outgoing dependencies of a module/file
  └─ ROUTE → mcp__adg_sqlite__adg_nodes_by_file(file_path=Z) → mcp__adg_sqlite__adg_edge_fanout(src_id=<node_id>, relation_type="imports")
  └─ NEVER → grep_search("import", SearchPath=Z)

QUERY: "Blast radius of changing A / impact of modifying A?"
  └─ Observable: query mentions blast radius, impact, or affected files
  └─ ROUTE → mcp__adg_sqlite__adg_nodes_by_file(file_path=A)
             → for EACH symbol node: mcp__adg_sqlite__adg_edge_fanin(tgt_id=<symbol_id>, relation_type="imports")
             → merge all results
  └─ NEVER → grep_search("A", Includes=["*.py"])

QUERY: "All uses of CONSTANT_NAME / where is CONFIG_KEY used?"
  └─ Observable: query targets an ALL_CAPS constant or config key
  └─ ROUTE → mcp__adg_sqlite__adg_node(node_id=<constant>) → mcp__adg_sqlite__adg_edge_fanin(tgt_id=<node_id>, relation_type="references")
  └─ NEVER → grep_search("CONSTANT_NAME")

QUERY: "Which layer does X belong to / layer violations?"
  └─ Observable: query references architectural layers (L0-L6)
  └─ ROUTE → mcp__adg_sqlite__adg_nodes_by_layer(layer=<layer>) or mcp__adg_sqlite__adg_nodes_by_file(file_path=X)
  └─ NEVER → grep_search for layer inference

QUERY: "Find TODOs / FIXMEs / literal string / non-Python content"
  └─ Observable: query targets literal text, comments, or non-code content
  └─ ROUTE → grep_search ← THIS IS THE ONLY VALID USE
```

### File-Path vs ADG-Name Routing (CRITICAL)

```
INPUT: bare file path (e.g., "tools/mcp/vector_db_server.py")
  └─ ROUTE → mcp__adg_sqlite__adg_nodes_by_file(file_path="tools/mcp/vector_db_server.py")
  └─ NEVER → mcp__adg_sqlite__adg_find_node("tools/mcp/vector_db_server.py")
     WHY: adg_find_node matches on adg_name (format: "ADG::Module::..."),
          NOT bare file paths. Bare paths return 0 results — silent failure.

INPUT: ADG-format name (e.g., "ADG::Module::tools/mcp/vector_db_server.py")
  └─ ROUTE → mcp__adg_sqlite__adg_find_node(name="ADG::Module::tools/mcp/vector_db_server.py")

INPUT: Python dotted module (e.g., "tools.mcp.vector_db_server")
  └─ ROUTE → mcp__adg_sqlite__adg_find_node(name="tools.mcp.vector_db_server")
     OR    → mcp__adg_sqlite__adg_nodes_by_file(file_path="tools/mcp/vector_db_server.py")
```

### Quick Reference: ADG MCP Tool Selection

| I need to find... | ADG MCP Tool | Relation Type |
|-------------------|-------------|---------------|
| Nodes in a file | `mcp__adg_sqlite__adg_nodes_by_file` | — |
| Nodes in a layer | `mcp__adg_sqlite__adg_nodes_by_layer` | — |
| Single node details | `mcp__adg_sqlite__adg_node` | — |
| Who depends on X (consumers) | `mcp__adg_sqlite__adg_edge_fanin` | `imports`, `calls`, `references` |
| What X depends on (suppliers) | `mcp__adg_sqlite__adg_edge_fanout` | `imports`, `calls`, `references` |
| ADG health status | `mcp__adg_sqlite__adg_health` | — |

### Workflow: Typical Dependency Query

```
Step 1: mcp__adg_sqlite__adg_health()                          # Verify ADG is alive
Step 2: mcp__adg_sqlite__adg_nodes_by_file(file_path="...")     # Get node IDs for the file
Step 3: mcp__adg_sqlite__adg_edge_fanin(tgt_id="...", relation_type="imports")  # Who imports it
   OR:  mcp__adg_sqlite__adg_edge_fanout(src_id="...", relation_type="imports") # What it imports
Step 4: (Optional) mcp__adg_sqlite__adg_node(node_id="...")     # Detailed info on specific nodes
```

### When ADG Is Unavailable

If `mcp__adg_sqlite__adg_health` returns unhealthy:
1. Run `/mcp-failure-rca`
2. Wait for recovery
3. **DO NOT fall back to grep_search for dependency analysis**
4. Report to user: "ADG MCP is unhealthy. Cannot perform dependency analysis until recovered."

### Why grep_search Is The Wrong Tool for Dependencies

1. **False positives**: grep finds string matches in comments, docstrings, dead code, test fixtures
2. **False negatives**: grep misses re-exports, dynamic imports, aliased references
3. **No transitive closure**: grep shows direct matches, not dependency chains
4. **No layer awareness**: grep doesn't know which architectural layer a match belongs to
5. **Context pollution**: grep output floods context window with irrelevant matches (70-80% of context per OpenDev §3.1)
