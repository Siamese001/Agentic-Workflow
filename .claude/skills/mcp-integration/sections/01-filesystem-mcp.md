## §1 — Filesystem MCP

**In-house.** Use **sparingly.** Claude Code file tools are the default; this MCP is for batch or out-of-workspace operations.

### When To Use

| Intent | Use MCP? | Native Alternative |
|--------|----------|-------------------|
| Single file read | ❌ No | `read_file` |
| Single file edit | ❌ No | `edit` / `multi_edit` |
| 5+ files in one call | ✅ Yes | `read_multiple_files` |
| Recursive JSON tree | ✅ Yes | `directory_tree` |
| Move across allowed dirs | ✅ Yes | `move_file` |

### Tool Routing

| Goal | Tool |
|------|------|
| List allowed roots | `list_allowed_directories` |
| Batch file read | `read_multiple_files` |
| Recursive tree (JSON) | `directory_tree` |
| Directory listing | `list_directory` / `list_directory_with_sizes` |
| File metadata | `get_file_info` |
| Glob search | `search_files` |
| Create directory | `create_directory` |
| Write file (overwrite) | `write_file` |
| Line-based edit | `edit_file` |
| Move/rename | `move_file` |

### Hard Rules
1. **Native first** — use `read_file`/`edit` before this MCP
3. **Allowed-directories sandbox** — paths must be within allowed roots
4. **`edit_file` supports `dryRun=true`** — preview changes

---
