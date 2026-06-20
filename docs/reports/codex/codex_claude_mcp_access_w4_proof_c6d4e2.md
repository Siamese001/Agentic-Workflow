# Codex Claude MCP Access W4 Proof

Generated: 2026-06-11  
Plan: `codex-claude-mcp-access-parity-c6d4e2` W4  
Scope: callable proof and operating procedure closeout for Claude-configured MCP access from Codex.

## W4 Result

W4 is complete. The result is honest parity classification, not blanket success.

| Classification | MCPs |
|---|---|
| `CALLABLE` | _None as raw Claude-equivalent MCPs_ |
| `PLUGIN_SUBSTITUTE` | `notion` |
| `SUBSTITUTE_CALLABLE` | `playwright` |
| `EXPOSED_BLOCKED` | `adg_sqlite` |
| `PROCESS_ONLY` | `memory`, `vector_db`, `context7` |
| `DEGRADED_FALLBACK` | `GitKraken`, `deepwiki` |

## Proof Matrix

| MCP | Target Proof | W4 Result | Evidence | Next Step for Raw Parity |
|---|---|---|---|---|
| `GitKraken` | `git_status` or equivalent GitKraken MCP call | `DEGRADED_FALLBACK` | No Codex GitKraken MCP surface discovered. Native `git rev-parse --show-toplevel` returned `C:/Git/Agentic-Workflow-FRESH`. | Expose GitKraken MCP through the Codex host. |
| `adg_sqlite` | `adg_health` succeeds from Codex | `EXPOSED_BLOCKED` | Direct `mcp__adg_sqlite.adg_health` returned `Transport closed`; W4 audit classified `closed_transport`. | Restart or reattach through the MCP host, then verify `adg_health`. |
| `deepwiki` | `read_wiki_structure`, `read_wiki_contents`, or `ask_question` succeeds | `DEGRADED_FALLBACK` | No Codex DeepWiki tool surface discovered. | Expose remote DeepWiki MCP through the Codex host. |
| `memory` | `mem_recall_session_start` succeeds | `PROCESS_ONLY` | Audit sees a single memory process, but Codex has no Memory tool surface. | Expose Memory MCP through the Codex host. |
| `vector_db` | `semantic_search`, `vector_stats`, or `list_collections` succeeds | `PROCESS_ONLY` | Audit sees a single Vector DB process, but Codex has no Vector DB tool surface. `rg --version` returned `ripgrep 15.1.0` as lexical fallback proof. | Expose Vector DB MCP through the Codex host. |
| `notion` | Plans page/data source fetch succeeds | `PLUGIN_SUBSTITUTE` | Codex Notion plugin `_fetch` successfully fetched the plan page. | Continue plugin route with schema-fetch discipline, or expose raw Claude Notion MCP if identical API names are required. |
| `context7` | `resolve-library-id` / `get-library-docs` succeeds | `PROCESS_ONLY` | Audit sees a single Context7 launch tree, but raw tools are not callable from Codex. | Expose Context7 MCP through the Codex host. |
| `playwright` | Browser/session call succeeds | `SUBSTITUTE_CALLABLE` | `mcp__node_repl.js` returned `{"ok":true,"cwd":"C:\\Git\\Agentic-Workflow-FRESH","hasRequestMeta":true}`. | Use node/browser substitute, or expose raw Playwright MCP if Claude `browser_*` parity is required. |

## Operating Procedure

1. Read `.mcp.json` and `.codex/mcp-notes.md` first. They remain the MCP SSOT.
2. Run:

   ```bash
   python scripts/governance/audit_codex_mcp_transports.py --json
   ```

3. If direct proof calls were run in the current session, pass evidence through environment values before the audit:

   ```text
   CODEX_MCP_CALLABLE_ADG_SQLITE=closed_transport
   CODEX_MCP_CALLABLE_NOTION=plugin_callable
   CODEX_MCP_CALLABLE_PLAYWRIGHT=substitute_callable
   ```

4. Interpret `route_evidence`:
   - `CALLABLE` means a healthy callable route was proven.
   - `EXPOSED_BLOCKED` means the namespace/route exists but is blocked.
   - `PLUGIN_SUBSTITUTE` and `SUBSTITUTE_CALLABLE` are useful Codex routes, not raw Claude MCP parity.
   - `PROCESS_ONLY` means an OS process exists but Codex cannot call it.
   - `DEGRADED_FALLBACK` means use the named substitute and say so.

5. Never launch detached stdio MCPs and call that parity. The Codex host must own the stdio attachment.

## Verification

| Command / Tool | Result |
|---|---|
| `mcp__adg_sqlite.adg_health` | `Transport closed` |
| `mcp__codex_apps__notion._fetch` on the plan page | Success |
| `mcp__node_repl.js` simple execution | Success |
| `python scripts/governance/audit_codex_mcp_transports.py --json` with callable evidence env overrides | Exit 0; emitted `route_evidence` |
| `git rev-parse --show-toplevel` | `C:/Git/Agentic-Workflow-FRESH` |
| `rg --version` | `ripgrep 15.1.0` |

## Closeout

This plan establishes an auditable Codex access procedure. It does not make unavailable Claude MCPs magically callable; it makes the distinction visible, testable, and hard to misreport.
