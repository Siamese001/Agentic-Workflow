# Tool Parameter Discipline

Prevents use of invented or hallucinated tool parameters.

---

## Core Rule

**NEVER use a tool parameter that has not been confirmed in one of:**
1. The tool's schema definition (visible in this session's tool list)
2. A prior successful call in THIS session that returned the parameter
3. Official documentation read via `read_url_content` in this session

---

## Pre-Call Checklist

Before calling ANY MCP tool with a parameter not used before:

- [ ] Parameter name appears in the tool's JSON schema definition
- [ ] Parameter type matches what the schema declares
- [ ] Parameter is not marked as deprecated in schema
- [ ] Value being passed matches the declared enum/type constraints

If ANY box is unchecked → **do NOT use that parameter**.

---

## Known Invented Parameters (BLOCKLIST)

These parameters have been confirmed non-existent in past sessions.
Using them will silently fail or be ignored:

| Tool | Invented Parameter | Confirmed Non-Existent |
|------|--------------------|----------------------|
| Windsurf workspace settings | `windsurf.search.rankFilesBeforeCommits` | RCA_windsurf_at_symbol_final.md |
| Windsurf workspace settings | `windsurf.semanticSearch.excludeGitCommits` | RCA_windsurf_at_symbol_final.md |
| Windsurf workspace settings | `windsurf.symbolIndex.excludeGitObjects` | RCA_windsurf_at_symbol_final.md |
| Windsurf workspace settings | `windsurf.search.commitResultWeight` | RCA_windsurf_at_symbol_final.md |
| Windsurf workspace settings | `windsurf.codeIndex.excludeGitHistory` | RCA_windsurf_at_symbol_final.md |

**Confirmed REAL parameters:**
- `windsurf.codeIndex.priorityPatterns` — works, verified in session

---

## When Uncertain About a Parameter

1. Read the tool schema from the available tool definitions
2. If schema is ambiguous, try a minimal test call with only required parameters
3. If the parameter is optional and behavior is unclear → omit it
4. Document in evidence: "Parameter X omitted — not confirmed in schema"

---

## MCP Tool Reliability Notes

Based on observed behavior:

| Tool | Reliability | Notes |
|------|------------|-------|
| `mcp5_write_file` | Medium | Silent failure with special characters in path; verify after every call |
| `write_to_file` | High | Preferred for workspace files; always verify |
| `mcp5_read_text_file` | High | Reliable; use for post-write verification |
| `mcp5_get_file_info` | High | Reliable stat check; use for existence verification |
| `mcp5_list_directory` | High | Reliable; use for directory existence checks |
