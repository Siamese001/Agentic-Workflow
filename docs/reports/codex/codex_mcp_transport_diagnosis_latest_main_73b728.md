# Codex MCP Transport Diagnosis - Latest Main

Plan: `codex-mcp-transport-diagnosis-latest-main-73b728`
Branch: `codex-mcp-transport-diagnosis-latest-main`
Generated: 2026-07-04T11:49:20Z
Base: `origin/main` = `cd55fca88e8fa473120c0f191a9da4d08b5214f6`

## Latest Main Baseline

Latest `main` already had the broad MCP transport work:

- `scripts/governance/audit_codex_mcp_transports.py`
- route-evidence classifications: `CALLABLE`, `EXPOSED_BLOCKED`, `PROCESS_ONLY`, `HOST_MCP_REQUIRED`, `PLUGIN_SUBSTITUTE`, `SUBSTITUTE_CALLABLE`, `DEGRADED_FALLBACK`
- `scripts/governance/codex_readiness.py` closed-transport RCA
- `.codex/governance/scripts/mcp_callability_epoch.py` session epoch and callability proof ledger
- `tools.adg.mcp.supervisor.transport_status()` for out-of-band `adg_sqlite` state
- `docs/codex-primary-execution.md` MCP lifecycle cleanup guard
- in-progress plan `plans/codex-mcp-transport-parity-4b9c7e.md`

This branch does not replace the parity plan. It adds only a deterministic diagnosis and recovery recommendation wrapper for the remaining operational gap.

## Branch Additions

- `plans/codex-mcp-transport-diagnosis-latest-main-73b728.md`
- `scripts/governance/diagnose_codex_mcp_transport.py`
- `tests/unit/scripts/governance/test_diagnose_codex_mcp_transport.py`
- this report and JSON sibling
- a minimal `docs/codex-primary-execution.md` pointer under the MCP Lifecycle Cleanup Guard

The wrapper is read-only. It does not launch servers, kill processes, call Codex MCP tools, or treat direct SQLite access as green ADG MCP proof.

## Current Diagnosis Output

Command:

```bash
python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json
```

Current top-level output:

```json
{
  "schema_version": "codex-mcp-transport-diagnosis/v1",
  "server_id": "adg_sqlite",
  "classification": "server_healthy_codex_transport_closed",
  "recommended_action": "Host/TUI MCP reconnect is required; a shell cannot reattach Codex to a closed stdio transport. Use Codex host MCP management, then prove a live mcp__adg_sqlite.adg_health call before setting callability overrides.",
  "codex_restart_required": "unknown",
  "shell_reopen_supported": false,
  "safe_to_cleanup_processes": false,
  "degraded_fallback_available": false
}
```

Evidence summary:

| Field | Value |
|---|---|
| Route classification | `EXPOSED_BLOCKED` |
| Route fallback | `closed_transport` |
| Process classification | `single` |
| Process count | `1` |
| ADG launcher PID | `6104` |
| Supervisor transport status | `closed` |
| Transport open | `false` |
| Session epoch callability status | `absent` |
| File proof status | `stale_file_proof` |
| Stale proof PID | `14688` |
| Stale proof PID alive | `false` |
| Diagnosis root | `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-mcp-transport-diagnosis-latest-main` |
| Runtime root | `C:\Git\Agentic-Workflow-FRESH` |
| ADG snapshot | `adg_indexed_07032026_2302.sqlite` |

The key distinction is deliberate: SQLite and the ADG launcher are present, but the active Codex MCP stdio route is not callable. This is transport diagnosis evidence only, not ADG green readiness.

## Stale Evidence Finding

`docs/reports/codex/codex_mcp_transport_lifecycle_audit.json` is stale for current recovery decisions.

- It was generated for W4 of `codex-mcp-transport-parity-4b9c7e` on 2026-06-10.
- It captured ADG snapshot `06082026_1212` and ADG PIDs `11052` / `12236`.
- It also references the older eval-harness-era registry/runtime context.
- Current diagnosis on 2026-07-04 sees latest `origin/main` at `cd55fca88e8f`, runtime root `C:\Git\Agentic-Workflow-FRESH`, ADG snapshot `07032026_2302`, launcher PID `6104`, and stale proof PID `14688` dead.

Use the new diagnosis command for current-session recovery. Treat the lifecycle audit as historical parity-plan evidence only.

## Local Runtime Difference

The branch worktree is based on latest `origin/main`, but the active runtime still resolves `AGENTIC_REPO_ROOT` to the primary checkout at `C:\Git\Agentic-Workflow-FRESH`. The primary checkout currently has unrelated dirty ADG/report and baseline files. This branch did not modify those files.

## Validation

| Command | Result |
|---|---|
| `python -m py_compile scripts/governance/diagnose_codex_mcp_transport.py` | PASS |
| `python -m pytest -q tests/unit/scripts/governance/test_diagnose_codex_mcp_transport.py` | PASS, 6 tests |
| `python -m pytest -q tests/unit/scripts/governance/test_audit_codex_mcp_transports.py tests/unit/scripts/governance/test_codex_readiness.py` | PASS, 63 tests |
| `python scripts/governance/audit_codex_mcp_transports.py --json` | PASS exit 0; reports current duplicate cohorts and existing pycache access-denied entries for two script compile probes |
| `python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json` | PASS exit 0; classification `server_healthy_codex_transport_closed` |
| `python scripts/governance/codex_readiness.py --json --skip-searxng` | FAIL exit 1; expected stop condition due required MCP callability and ADG active-session transport failure |

## Remaining Manual Recovery

Manual recovery remains required:

1. Use Codex host/TUI MCP management to restart or reconnect `adg_sqlite`.
2. Prove a live `mcp__adg_sqlite.adg_health`, `adg_runtime_info`, or process-identity call in the active Codex session.
3. Do not claim ADG green readiness from direct SQLite, launcher state, heartbeat files, or process liveness.
4. Do not kill Codex-owned duplicate MCP processes without active host-attached PID proof.
