---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\rca-otel-mcp-transport-closed-2026-04-23.md'
original_relative_path: 'rca-otel-mcp-transport-closed-2026-04-23.md'
source_sha256: 15e4b1d1001cdd36e56071f556d10ae3d668d998012df52a6f0c8f9e22c1fe8a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: `otel_mcp` Health Check Failed with Transport Closed — 2026-04-23

**Status**: RESOLVED (no code change required; operational cause identified)
**Severity**: Low (observability-only; transient)
**Reporter**: Cursor Agent
**Time of symptom**: 2026-04-23 ~22:34 UTC-04
**Incident tool call**: `mcp7_otel_server_info`
**Error**: `transport error: transport closed`

## TL;DR

The `otel_mcp` health check failed **not because of an upstream MCP client race** (as initial diagnosis suggested), but because **the otel_mcp server process had died silently ~2 hours earlier and Windsurf's MCP supervisor did not auto-respawn it**. The same fate had befallen every other Python-backed MCP server in the active Windsurf session.

## Timeline

| Time (UTC-04) | Event |
|---|---|
| 16:38 | Active Windsurf session started (log dir `20260423T163836`) |
| 20:27:46 | `otel_mcp` initialized successfully (v1.26.0); last Windsurf-exthost log mention |
| 20:37:04 | Last MCP stdio traffic in exthost log (unrelated server; ~1s request/response cycle) |
| 20:37:15 | Last write to `Windsurf.log` in this session |
| ~20:43–22:26 | **5 empty new log session directories created** — indicative of Windsurf window restarts / reload attempts that did not fully bring up logging |
| 22:34 | Cursor Agent called `mcp7_otel_server_info` → `transport closed` |
| 22:36 | RCA started; process scan shows **zero Python MCP servers running** |

## Evidence

### 1. No Python MCP processes running

```
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ... -like '*mcp*'
→ 0 matches
```

All Python MCP servers are gone: `otel_mcp`, `adg_sqlite`, `redis`, `memory`, `pytest_mcp`, `vector_db`, `enhanced_http`.

### 2. The server binary is healthy

Started manually:

```
python -u tools/otel/otel_mcp_server.py
```

→ Initializes cleanly. FastMCP server boots, tracer + runtime-adg-store prewarms complete, `GUARD_CLEAN: no sibling processes` logged, process remains alive. **Zero code-side defects in `otel_mcp`.**

### 3. Windsurf exthost stopped writing its MCP log ~2h before the failed call

Last `Windsurf.log` write: 20:37:15. Failed call: 22:34:00. Windsurf was alive and responsive (Cursor Agent itself continued running) but the MCP bridge to the exthost side was stale.

### 4. Config and environment are valid

- `.windsurf/mcp_config.json` entry for `otel_mcp` matches the documented schema (`command`, `args`, `disabled`, `env` — no schema-invalid fields per constitutional §26)
- `AGENTIC_REPO_ROOT` = `C:/Git/Agentic-Workflow` (User scope, resolved correctly)
- `python` command resolves to Python 3.12

Rules out: env-variable expansion failures, schema-invalid fields silently disabling the server (§26), PATH issues.

### 5. The MCP client correctly reported the symptom, not the cause

The Windsurf MCP transport layer keeps the client-side pipe registered even after the server process exits. Subsequent writes succeed locally; the next read returns EOF → the transport wrapper surfaces this as `transport closed`. This is semantically correct but not root-cause-ful.

## Root Cause

**Windsurf's MCP supervisor does not auto-respawn dead stdio-backed subprocess servers.** Once an MCP server dies for any reason (OOM, unhandled exception, signal from another process, sibling-guard cleanup from a concurrent Windsurf window), the client-side registration persists but the server is gone. Tool calls appear to succeed in dispatch, then surface `transport closed` on the read side.

### Proximate cause of this specific server death

Undetermined from available logs (Windsurf did not log the exit event, and no stderr artifact survived). Based on timing correlation with multiple empty new-session log dirs between 20:43 and 22:26, the **most plausible sequence** is:

1. A second Windsurf window was opened (or the active window reloaded), triggering a new MCP bootstrap attempt.
2. Each Python MCP server has a `GUARD_CLEAN` check in its bootstrap (see `tools.otel.otel_mcp_server`'s `mcp_bootstrap` module) that kills sibling processes matching its script marker to avoid split-brain.
3. The new window's servers killed the old session's servers via GUARD_CLEAN, then the new window itself closed/crashed before its own servers fully registered → **split-brain orphan: old session has dead MCP entries, new session no longer exists**.
4. The original (still-running) Cursor Agent session retained stale client handles.

## Classification per `mcp-serialization.md`

This incident is **NOT** an instance of the documented upstream race (`anthropics/claude-agent-sdk-typescript#41`). That race manifests as tool-call HANGS when MCP calls are issued concurrently with other tool calls. This incident is a process-lifecycle issue: dead server + no auto-respawn + stale client handle.

The symptom looked similar (single MCP call → error) but the mechanism is distinct:
- Serialization race: stream closed mid-flight during concurrent dispatch
- This RCA: transport already closed because the peer is a corpse

## Resolution

**Operational (immediate, already in effect):**
Reload the Windsurf window to trigger a fresh MCP bootstrap. This respawns all Python MCP servers under the current Windsurf process. No user action beyond the window reload.

**No code change required.**

## Corrective Actions (completed)

1. ✅ Confirmed `otel_mcp` server binary is healthy (manual subprocess start test)
2. ✅ Confirmed `.windsurf/mcp_config.json` is schema-compliant (no §26 violation)
3. ✅ Confirmed `AGENTIC_REPO_ROOT` env is set correctly
4. ✅ This RCA written as operational precedent

## Preventive Recommendations (deferred; not gating this session)

| Priority | Action |
|---|---|
| P3 | Add a heartbeat probe from Cursor Agent at session start (`mcp_health` on each Python MCP) — surfaces dead servers before a real query hits the stale handle |
| P4 | Consider a lightweight watchdog script in `.windsurf/scripts/` that checks for missing Python MCP processes periodically and logs a warning |
| P5 | Investigate whether `mcp_bootstrap.GUARD_CLEAN` can be made less aggressive (only kill sibling if heartbeat is dead, not just because marker matches) to reduce split-brain risk during Windsurf window churn |

These are optional hardening; the primary discipline is "reload the window if Python MCP calls start erroring."

## Deferred-Scope Markers

DEFERRED_SCOPE: plan=NEW:mcp-heartbeat-on-session-start wave=OPS phase=OPS.P1 layer=L_OPS fan_in=10 surface=Observability coverage_gap_pct=20.0 est_tokens=2000 reason=Add mcp health heartbeat probe at Cursor Agent session start to catch dead stdio servers before real queries

DEFERRED_SCOPE: plan=NEW:mcp-guard-clean-hardening wave=OPS phase=OPS.P2 layer=L_TOOLS fan_in=7 surface=Execution coverage_gap_pct=10.0 est_tokens=3000 reason=Make mcp_bootstrap GUARD_CLEAN heartbeat-aware to reduce split-brain risk during Windsurf window churn

## References

- `.windsurf/mcp_config.json` — otel_mcp config entry (lines 86–97)
- `.windsurf/rules/mcp-serialization.md` — distinguished mechanism (not this RCA)
- `.windsurf/rules/constitutional.md` §26 — schema purity for mcp_config.json (verified)
- Log: `%APPDATA%\Windsurf\logs\20260423T163836\window3\exthost\codeium.windsurf\Windsurf.log`
