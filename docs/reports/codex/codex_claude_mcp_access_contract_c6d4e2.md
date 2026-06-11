# Codex Claude MCP Access Contract

Generated: 2026-06-11  
Plan: `codex-claude-mcp-access-parity-c6d4e2` W2  
Scope: define Codex exposure routes for every Claude-configured MCP without creating a parallel registry.

## W2 Result

W2 is complete.

- **W2.1 complete:** selected the Codex exposure route for each live `.mcp.json` MCP.
- **W2.2 complete:** defined no-parallel-registry invariants and standard failure/fallback messages.

The contract does not edit `.mcp.json`, secrets, or MCP runtime configuration. It is a routing and disclosure contract for W3/W4 implementation and verification.

## Invariants

| ID | Rule | Enforcement |
|---|---|---|
| `NO_PARALLEL_REGISTRY` | Codex must not maintain a second MCP server registry for this repository. | All configured-server truth comes from root `.mcp.json`; Codex reports are evidence snapshots only. |
| `PROCESS_IS_NOT_CALLABLE` | A live MCP OS process is not proof that Codex can call the MCP. | Reports must separate configured, process-visible, and callable states. |
| `FALLBACK_IS_NOT_PARITY` | CLI, plugin, web, or direct-DB fallbacks are degraded routes unless they expose the same MCP contract. | Fallback messages must name the unavailable MCP and substitute used. |
| `HOST_OWNS_STDIO` | Detached manual stdio MCP launches are not equivalent to host-attached MCP access. | Codex may audit process health, but parity requires the Codex host to expose callable tools. |
| `NO_SECRET_CHURN` | This plan does not change credentials or environment variable values. | W2 records required env state and route decisions only. |

## Standard Messages

| Key | Message |
|---|---|
| `raw_mcp_unavailable` | `DEGRADED_FALLBACK: <server_id> is configured in .mcp.json for Claude, but Codex has no callable MCP tool surface in this session; using <substitute> instead.` |
| `process_only` | `BLOCKED: <server_id> has a visible MCP process, but Codex cannot call its tools; process presence is not MCP parity.` |
| `closed_transport` | `BLOCKED: <server_id> tool namespace is exposed, but the transport is closed; restart or reattach through the MCP host before claiming parity.` |
| `plugin_substitute` | `SUBSTITUTE_ROUTE: <server_id> is available through a Codex plugin or adjacent tool with different API shape; verify schema/tool-name differences before mutation.` |
| `no_substitute` | `BLOCKED: <server_id> is unavailable in Codex and has no honest substitute for this operation.` |

## Route Contract

| MCP | Selected Codex Route | Owner | Mutation Policy | W2 Decision |
|---|---|---|---|---|
| `GitKraken` | Degraded fallback: native `git` CLI and GitHub plugin only when task scope permits. | Codex host for parity exposure; Codex agent for fallback disclosure. | Mutating git actions allowed only under normal Codex git safety rules; do not claim GitKraken authority. | Require host-level GitKraken MCP exposure for parity. |
| `adg_sqlite` | Host MCP required: `mcp__adg_sqlite` only when the stdio transport is open. | Codex host owns MCP attachment. | Read-only structural queries; direct SQLite fallback must be labeled degraded. | Current route is blocked until `adg_health` succeeds from Codex; detached manual launch is not parity. |
| `deepwiki` | Degraded fallback: GitHub plugin, Tavily/web, or official docs as named substitutes. | Codex host for parity exposure; Codex agent for fallback disclosure. | Read-only research substitute; cite actual sources used. | Require host-level DeepWiki exposure for parity. |
| `memory` | Host MCP required. No accepted substitute for persistent memory compliance. | Codex host must expose callable Memory MCP tools. | Do not claim memory recall/writeback unless tools are callable. | Memory is parity-critical; process-only visibility remains blocked. |
| `vector_db` | Degraded fallback: `rg`, ADG structural search, or direct Chroma inspection when fit for purpose. | Codex host for semantic parity; Codex agent for fallback disclosure. | Read/search only; lexical search must not be represented as semantic search. | Require host-level Vector DB exposure for semantic parity. |
| `notion` | Plugin substitute: `mcp__codex_apps__notion` tools. | Codex Notion plugin for current route; Codex host for raw MCP parity if required later. | Writes allowed for Plans/Backlog when schema is fetched first; archived DBs remain filesystem SSOT. | Accept plugin substitute for this plan; record API-shape delta. |
| `context7` | Degraded fallback: official docs/web or domain-specific plugin docs. | Codex host for raw Context7 parity; Codex agent for source disclosure. | Read-only; cite primary official docs. | Require host-level Context7 exposure for raw parity. |
| `playwright` | Callable substitute: `node_repl` browser automation and Browser plugin skills. | Codex node/browser tooling for substitute; Codex host for raw MCP parity. | Browser automation allowed; label as substitute when raw `browser_*` tools are absent. | Accept substitute route unless raw Claude Playwright MCP parity is explicitly required. |

## Route Details

### `GitKraken`

Claude expects GitKraken to be the git/PR authority. Codex has no callable GitKraken tools in this snapshot. Native `git` and the GitHub plugin are allowed only as explicit degraded fallbacks.

Required wording:

`DEGRADED_FALLBACK: GitKraken is configured in .mcp.json for Claude, but Codex has no callable GitKraken MCP surface in this session; using native git/GitHub substitute instead.`

### `adg_sqlite`

Codex exposes an `mcp__adg_sqlite` namespace, but the W2 `adg_health` proof still returns `Transport closed`. The process audit currently sees one ADG process, which proves process presence only.

Required wording:

`BLOCKED: adg_sqlite tool namespace is exposed, but the transport is closed; restart or reattach through the MCP host before claiming parity.`

### `deepwiki`

DeepWiki is configured as a remote MCP URL in `.mcp.json`, but Codex has no `read_wiki_structure`, `read_wiki_contents`, or `ask_question` tool surface. Web or GitHub research is not DeepWiki-backed.

### `memory`

Memory is governance-critical because session-start recall and durable decision writeback have no honest substitute. Direct database access can inspect facts, but it does not satisfy the Memory MCP workflow.

Required wording:

`BLOCKED: memory is unavailable in Codex and has no honest substitute for this operation.`

### `vector_db`

Vector DB remains process-visible but not callable. `rg` and ADG are useful substitutes for lexical and structural questions, but not semantic retrieval parity.

### `notion`

The Codex Notion plugin is accepted as a substitute route for this plan because it successfully fetched the Plans data source, created the plan row, and updated the W1 status. The contract requires schema fetches before property writes and exact property names from the data source.

Plans data source:

`collection://ac53d31b-3068-4039-9ebe-856c12caab32`

### `context7`

Context7 is process-visible but raw tools are not callable in Codex. Use official docs or domain-specific plugin docs as degraded, cited substitutes until the host exposes `resolve-library-id` and `get-library-docs`.

### `playwright`

Codex has a practical browser automation substitute through `node_repl` and Browser plugin skills. This is acceptable for UI verification, but it is not raw Claude Playwright MCP parity because `browser_navigate`, `browser_snapshot`, and related raw tools are absent.

## W3 Inputs

W3 should implement or extend audit logic so reports emit these classifications directly:

- `HOST_MCP_REQUIRED`
- `EXPOSED_BLOCKED`
- `PLUGIN_SUBSTITUTE`
- `SUBSTITUTE_CALLABLE`
- `DEGRADED_FALLBACK`
- `PROCESS_ONLY`
- `NOT_EXPOSED`

W3 should also add fixture-backed tests for blocked transport, process-only, plugin-substitute, and degraded-fallback states.
