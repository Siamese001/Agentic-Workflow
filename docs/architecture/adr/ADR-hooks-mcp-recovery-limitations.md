# ADR: Windsurf Hooks Cannot Auto-Recover Red MCP Servers

**Date:** 2026-04-08
**Status:** Accepted
**Context:** Investigation into why Cascade hooks were not auto-diagnosing and restoring red ADG MCP server

## Decision

Accept that Windsurf hooks **cannot fully automate MCP recovery** due to platform limitations, and implement the best possible mitigation within those constraints.

## Bugs Fixed (2026-04-08)

### Bug 1: Wrong JSON field name (Critical — hook was a complete no-op)
- **File:** `ops_scripts/hooks/windsurf/pre_prompt_classifier.py`
- **Bug:** `tool_info.get("prompt", "")` — Windsurf sends `"user_prompt"`, not `"prompt"`
- **Impact:** The entire tier classifier, plan check, and ADG health gate never executed
- **Fix:** Changed to `tool_info.get("user_prompt", "") or tool_info.get("prompt", "")`

### Bug 2: Dead-loop in pre_mcp_gate (recovery tools blocked by their own gate)
- **File:** `ops_scripts/hooks/windsurf/pre_mcp_gate.py`
- **Bug:** When ADG is stale, the gate blocks ALL adg_sqlite tools — including `mcp1_adg_health` which is the only way to recover
- **Impact:** Cascade cannot probe or restore ADG health because the probe itself is blocked
- **Fix:** Added `ADG_RECOVERY_TOOLS` whitelist: `adg_health`, `adg_status`, `adg_close_connections`, `adg_reopen_connections` always pass

## Platform Limitations (Cannot Fix — Windsurf Architecture)

### Limitation 1: No MCP lifecycle hook event
Windsurf provides 12 hook events, all triggered by **Cascade actions** (read, write, command, MCP call, prompt, response). There is no hook for:
- MCP server crash / exit
- MCP server health state change
- MCP initialization failure
- MCP connection loss

**Consequence:** If ADG goes red between conversations (e.g., server process dies, SQLite locked by external tool), no hook fires until the user submits a prompt. Detection is reactive, not proactive.

### Limitation 2: Hooks cannot trigger MCP tool calls or restart servers
Hooks are subprocess scripts that communicate via exit codes (0=allow, 2=block). They cannot:
- Call MCP tools (no access to Windsurf's MCP client)
- Restart MCP server processes (no access to Windsurf's process manager)
- Refresh MCP connections (no API for this)
- Modify the MCP server registry at runtime

**Consequence:** Even after detecting a red MCP, the hook can only:
1. Block the action (exit 2) with a message in stderr
2. Hope that Cascade reads the stderr message and takes corrective action

The Windsurf changelog confirms: *"Refresh button for error states: Show refresh button for MCPs in error state to allow **manual** recovery."*

## Mitigation Strategy (What We Can Do)

1. **`pre_user_prompt` hook (fixed):** Detects T2/T3 prompts, probes ADG health via subprocess, blocks if red with actionable message
2. **`pre_mcp_tool_use` hook (fixed):** Blocks ADG queries when stale/locked, but allows recovery tools through
3. **Constitutional rule §13:** Cascade rules instruct the model to run `mcp1_adg_health` at session start
4. **Manual recovery:** User clicks refresh button in Windsurf MCP panel, or Cascade runs `/mcp-failure-rca` workflow

## Future Improvement Opportunities

- **Windsurf feature request:** `on_mcp_health_change` hook event with server name and status
- **Windsurf feature request:** Hook ability to trigger MCP server restart via API
- **Sidecar process:** A background watchdog that periodically probes MCP health and restarts crashed servers (outside Windsurf's hook system)

## References

- [Windsurf Cascade Hooks docs](https://docs.windsurf.com/windsurf/cascade/hooks)
- [Windsurf Changelog — Hooks](https://windsurf.com/changelog) (Wave 13, patch notes)
- [Windsurf MCP docs](https://docs.windsurf.com/windsurf/cascade/mcp)
