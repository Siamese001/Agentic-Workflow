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
  └─ ROUTE → mcp1_adg_nodes_by_file(file_path=X) → mcp1_adg_edge_fanin(tgt_id=<node_id>, relation_type="imports")
  └─ NEVER → grep_search("from X import") or grep_search("import X")

QUERY: "Who calls function Y / uses class Y / references symbol Y?"
  └─ Observable: query targets a specific function, class, or constant name
  └─ ROUTE → mcp1_adg_node(node_id=<symbol>) → mcp1_adg_edge_fanin(tgt_id=<node_id>, relation_type="calls")
  └─ NEVER → grep_search("Y(") or grep_search("class Y")

QUERY: "What does Z depend on / what does Z import?"
  └─ Observable: query asks about outgoing dependencies of a module/file
  └─ ROUTE → mcp1_adg_nodes_by_file(file_path=Z) → mcp1_adg_edge_fanout(src_id=<node_id>, relation_type="imports")
  └─ NEVER → grep_search("import", SearchPath=Z)

QUERY: "Blast radius of changing A / impact of modifying A?"
  └─ Observable: query mentions blast radius, impact, or affected files
  └─ ROUTE → mcp1_adg_nodes_by_file(file_path=A) → mcp1_adg_edge_fanin(tgt_id=<node_id>, relation_type="imports")
  └─ NEVER → grep_search("A", Includes=["*.py"])

QUERY: "All uses of CONSTANT_NAME / where is CONFIG_KEY used?"
  └─ Observable: query targets an ALL_CAPS constant or config key
  └─ ROUTE → mcp1_adg_node(node_id=<constant>) → mcp1_adg_edge_fanin(tgt_id=<node_id>, relation_type="references")
  └─ NEVER → grep_search("CONSTANT_NAME")

QUERY: "Which layer does X belong to / layer violations?"
  └─ Observable: query references architectural layers (L0-L6)
  └─ ROUTE → mcp1_adg_nodes_by_layer(layer=<layer>) or mcp1_adg_nodes_by_file(file_path=X)
  └─ NEVER → grep_search for layer inference

QUERY: "Find TODOs / FIXMEs / literal string / non-Python content"
  └─ Observable: query targets literal text, comments, or non-code content
  └─ ROUTE → grep_search ← THIS IS THE ONLY VALID USE
```

### Quick Reference: ADG MCP Tool Selection

| I need to find... | ADG MCP Tool | Relation Type |
|-------------------|-------------|---------------|
| Nodes in a file | `mcp1_adg_nodes_by_file` | — |
| Nodes in a layer | `mcp1_adg_nodes_by_layer` | — |
| Single node details | `mcp1_adg_node` | — |
| Who depends on X (consumers) | `mcp1_adg_edge_fanin` | `imports`, `calls`, `references` |
| What X depends on (suppliers) | `mcp1_adg_edge_fanout` | `imports`, `calls`, `references` |
| ADG health status | `mcp1_adg_health` | — |

### Workflow: Typical Dependency Query

```
Step 1: mcp1_adg_health()                          # Verify ADG is alive
Step 2: mcp1_adg_nodes_by_file(file_path="...")     # Get node IDs for the file
Step 3: mcp1_adg_edge_fanin(tgt_id="...", relation_type="imports")  # Who imports it
   OR:  mcp1_adg_edge_fanout(src_id="...", relation_type="imports") # What it imports
Step 4: (Optional) mcp1_adg_node(node_id="...")     # Detailed info on specific nodes
```

### When ADG Is Unavailable

If `mcp1_adg_health` returns unhealthy:
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
