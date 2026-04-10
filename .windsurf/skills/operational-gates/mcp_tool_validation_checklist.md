# MCP Tool Validation Checklist

Run before any MCP tool call with parameters not previously validated in this session.

## Checklist

- [ ] Tool name exists in the MCP server's tool list (visible in system prompt)
- [ ] All required parameters are provided
- [ ] Parameter types match the tool schema (string, int, bool, array, object)
- [ ] Optional parameters use correct defaults
- [ ] Array parameters contain correct item types
- [ ] Object parameters have correct structure
- [ ] No undocumented parameters are included
- [ ] Parameter values are within allowed ranges or constraints

## Common Mistakes

| Mistake | Example | Correct |
|---|---|---|
| Hallucinated parameter | `mcp5_write_file(path=..., extra=True)` | Remove `extra` |
| Wrong parameter name | `find_by_name(path=...)` | Use `SearchDirectory=` |
| Missing required param | `mcp1_adg_node()` | Provide `node_id=` |
| Wrong type | `limit="50"` | Use `limit=50` (int) |

## Evidence Format

```
## MCP_TOOL_VALIDATION
**Tool**: <tool_name>
**Parameters validated**: <list>
**Validation result**: PASS / FAIL
**Source**: system prompt tool schema
```
