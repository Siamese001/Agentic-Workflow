# Fail-Closed Discipline

When ADG MCP is unavailable or returns an error, the correct response is to fix the MCP — not to substitute grep or text search.

## Hard Rules

- If `mcp1_adg_health` returns unhealthy → **STOP immediately**
- Do NOT silently fall back to `grep_search` for dependency analysis
- Do NOT claim "no dependencies" without graph analysis
- Do NOT assume relationships without graph proof

## Recovery Sequence (mandatory order)

1. Run `/mcp-failure-rca` workflow
2. Check `~/adg_mcp_server.log` for error details
3. Remove `tools/adg/core/__pycache__` if stale
4. Restart ADG MCP server in Windsurf (Ctrl+Shift+P → Restart MCP)
5. Re-run `mcp1_adg_health` to confirm recovery
6. Record failure + recovery in `artifacts/adg/mcp_health_report.json`

## Partial-Result Discipline

If graph cannot be fully built:
- Record all errors in evidence as `UNRESOLVED`
- Mark all graph-derived conclusions as `PARTIAL`
- Do not proceed with T2/T3 edits until graph is healthy

## Evidence Format

```
## ADG_HEALTH
Status: UNHEALTHY / PARTIAL / HEALTHY
Tool: mcp1_adg_health
Error: <exact error message>
Recovery: <steps taken>
Result: BLOCKED / RESOLVED
```

## grep_search Permitted Uses (narrow)

- Confirming a specific string literal exists in a file (after ADG located the file)
- Finding TODO comments or log messages
- Locating a known constant value

grep_search is NEVER permitted as a substitute for ADG fan-in/fanout, layer queries, or import tracing.
