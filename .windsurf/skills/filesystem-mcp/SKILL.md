---
name: filesystem-mcp
description: Filesystem operations — directory trees, multi-file reads, recursive search, write/move/edit — via the in-house filesystem MCP server. Invoke ONLY when native Cascade file tools are insufficient — multi-file batch reads, full directory trees, or operations on directories outside the active workspace. For ordinary single-file reads, prefer native read_file. For ordinary single-file writes, prefer native edit/write_to_file. The filesystem MCP is the secondary path, not the default.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
---

# Filesystem MCP Skill

In-house. **Use sparingly.** Native Cascade file tools (`read_file`, `edit`, `write_to_file`, `find_by_name`, `grep_search`, `list_dir`) are the default; this MCP is the fallback for batch or out-of-workspace operations.

## When To Use This MCP

| User intent | Use filesystem MCP? | Native alternative |
|---|---|---|
| Read a single file | ❌ No | `read_file` |
| Edit a single file | ❌ No | `edit` / `multi_edit` |
| Create a single file | ❌ No | `write_to_file` |
| Search files by name | ❌ No | `find_by_name` |
| Search content | ❌ No | `grep_search` |
| List a directory | ❌ No | `list_dir` |
| Read 5+ files in one call | ✅ Yes | `read_multiple_files` |
| Get a recursive tree as structured JSON | ✅ Yes | `directory_tree` |
| Move/rename across allowed dirs | ✅ Yes | `move_file` |
| List allowed directories | ✅ Yes | `list_allowed_directories` |

## Tool Routing

| Goal | Tool |
|---|---|
| List allowed roots | `list_allowed_directories` |
| Single file read (text) | `read_text_file` |
| Single file read (image/audio) | `read_media_file` |
| Multi-file batch read | `read_multiple_files` |
| Directory listing | `list_directory` |
| Directory listing with sizes | `list_directory_with_sizes` |
| Recursive tree (JSON) | `directory_tree` |
| File metadata | `get_file_info` |
| Search files (glob) | `search_files` |
| Create directory | `create_directory` |
| Write file (overwrite) | `write_file` |
| Edit file (line-based diff) | `edit_file` |
| Move/rename | `move_file` |

## Hard Rules

1. **Native first.** Reach for `read_file`/`edit`/`grep_search` before this MCP. The native tools have better integration with Cascade's plan/edit cycle.
2. **MCP serialization (§25):** One MCP call per response.
3. **Allowed-directories sandbox:** All paths must be within `list_allowed_directories` output. The MCP enforces this.
4. **`write_file` overwrites silently** — use `edit_file` for in-place modifications when possible.
5. **`edit_file` supports `dryRun=true`** to preview a git-style diff without writing.

## Common Workflows

**Read 10+ related files for analysis:**
1. `read_multiple_files(paths=[...])` — single MCP call

**Get a JSON-structured project tree for downstream tooling:**
1. `directory_tree(path='agentic_core', excludePatterns=['__pycache__', '*.pyc'])`

## When NOT To Use

- Reading source for a quick edit cycle → native `read_file` + `edit`.
- Searching for symbols → `grep_search` (or `adg_sqlite` for dependency analysis).
- Listing a single directory → native `list_dir`.
