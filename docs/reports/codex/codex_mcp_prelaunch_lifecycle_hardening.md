# Codex MCP Prelaunch Lifecycle Hardening

## ROLLBACK_CHECKPOINT

**Checkpoint ID**: CHK-20260711-001
**Files to modify**: 13
**Scope justification**: The required HTTP MCP lifecycle spans the Windows service definition, task-owned runner, task manager, Codex preflight/launcher/shortcut, advisory SessionStart verification, focused tests, active runbooks, and this durable receipt.
**Baseline commit**: `d8fea0ec26a64882eee4864fecab8abfac92c336`
**Checkpoint created**: `2026-07-11T16:23:31.3750158-04:00`
**Clean baseline**: `git diff --name-only HEAD` and `git status --short` returned no paths.
**Recovery command**: Revert the finished local commit with `git revert <commit>` after closeout. Before commit, restore only the paths listed in this report from baseline commit `d8fea0ec26a64882eee4864fecab8abfac92c336`; do not use destructive workspace-wide commands.

## SCOPE_DECLARATION

1. `ops_scripts/windows/codex_mcp_http_services.psd1` - shared service definition required by the lifecycle contract.
2. `ops_scripts/windows/run_codex_http_mcp_service.ps1` - foreground task-owned service runner.
3. `ops_scripts/windows/codex_mcp_service_tasks.ps1` - current-user Scheduled Task install, repair, status, ensure, and uninstall lifecycle.
4. `ops_scripts/windows/codex_mcp_preflight.ps1` - pre-Codex config synchronization and fail-closed protocol readiness.
5. `ops_scripts/windows/launch_codex_agentic.ps1` - supported prelaunch path.
6. `ops_scripts/windows/install_codex_agentic_shortcut.ps1` - current-user supported shortcut installer.
7. `.codex/hooks/session_start_mcp_bootstrap.py` - advisory status recording after MCP initialization.
8. `tests/unit/ops_scripts/windows/test_codex_mcp_windows_lifecycle.py` - deterministic Windows lifecycle contracts.
9. `tests/unit/ops_scripts/hooks/codex/test_session_start_mcp_bootstrap.py` - SessionStart status-only behavior.
10. `docs/codex-primary-execution.md` - primary Codex execution operator contract.
11. `tools/adg/mcp/OPERATIONS.md` - ADG HTTP lifecycle operations.
12. `tools/mcp/OPERATIONS.md` - shared MCP lifecycle operations.
13. `.codex/mcp-notes.md` - active MCP route and recovery notes.
14. `docs/reports/codex/codex_mcp_prelaunch_lifecycle_hardening.md` - human-readable evidence receipt.
15. `docs/reports/codex/codex_mcp_prelaunch_lifecycle_hardening.json` - machine-readable evidence receipt.

The initial count was 13 implementation/runbook surfaces; the two required report artifacts bring the declared tracked-file total to 15.

## DEPENDENCY_GRAPH

**Graph roots**: `.codex/hooks/session_start_mcp_bootstrap.py`, `tools/mcp/http_service_supervisor.py`, and the two HTTP launcher modules.
**Backend provenance**: `degraded_sqlite` (explicit MCP lifecycle recovery/RCA).
**Live query result**: `mcp__adg_sqlite__adg_health` failed because `http://127.0.0.1:8765/mcp` was unavailable.
**Scope-lossiness**: The policy-named `tools/adg/adg_test_selector.py` is absent in this checkout. The approved user contract and adjacent existing MCP/config/SessionStart tests therefore define the bounded recovery scope. No dependency conclusion is inferred from grep.

## DEDUP_SEARCH

The existing `tools/mcp/http_service_supervisor.py` was inspected and retained as the one-shot Python launcher. It is not a persistent restart owner. Existing user-profile task launchers are non-authoritative and are replaced in place by repo-owned task actions. No second Python supervisor or MCP configuration registry is introduced.

## PRE_CODE_GATE

**Changed surfaces**: service definition, foreground runner, Scheduled Task manager, preflight, launcher, shortcut installer, and advisory SessionStart status step.
**Existing coverage**: HTTP launcher, MCP config projection, and SessionStart tests passed at the baseline (12 collected, 12 passed).
**Required new coverage**: exact service definitions, shared-definition consumption, repo-owned task actions, drift/idempotency contracts, healthy/stopped/foreign-port branches, unexpected-exit handling, log redaction, health-tool gating, `-NoLaunch`, path discovery, and SessionStart status-only behavior.
**Dimensions**: success, malformed/drifted state, repeated install/ensure, dependency failure, foreign ownership fail-closed behavior, deterministic JSON contracts, and no-launch side-effect protection.

## PHASE_GATE

**Phase**: Windows HTTP MCP prelaunch lifecycle
**Gate 1 - Rollback checkpoint**: PASS
**Gate 2 - MCP validation**: PASS; live `adg_health` schema was validated and the call produced the expected transport failure.
**Gate 3 - Dependency graph**: PASS under explicit `degraded_sqlite` recovery/RCA exception.
**Gate 4 - Scope declared**: PASS
**Gate 5 - Test requirements**: PASS
**Overall**: PASS - proceed.

## Implementation And Verification

### Root cause

The required URL MCP routes were correct, but no durable owner started them before Codex initialized required servers. SessionStart runs after that initialization point, the existing preflight only synchronized config, and the manually created tasks pointed to user-profile scripts. During live hardening, two Windows-specific details were also corrected: an ordered receipt could crash the runner after child launch, and Task Scheduler did not restart an on-demand instance from Python's `-1` termination code. The runner now emits stable positive code `70`, and each task has both schema-valid native restart metadata and a one-minute repeating Task Scheduler watchdog trigger.

### Architecture and ownership

- `.mcp.json` remains the route SSOT; both routes remain HTTP, exact endpoint matched, and required.
- `codex_mcp_http_services.psd1` is the sole Windows lifecycle definition for task names, modules, endpoints, tools, paths, dependencies, and restart metadata.
- Each current-user task invokes the repo runner in the foreground. The runner waits for Redis, runs launcher preflight, records runner/child identity, and waits for child exit.
- Task repair/uninstall may stop a child only when receipt PID, listener PID, server ID, endpoint, repo root, and module command line all match.
- `IgnoreNew` plus the one-minute watchdog trigger prevents duplicates while providing bounded recovery.
- The supported launcher synchronizes config, repairs/ensures tasks, probes initialize/tools/list/health, and only then opens Codex.
- SessionStart invokes status only and remains advisory.

### Task definitions

| Service | Task | Endpoint | Health tool | Restart ownership |
|---|---|---|---|---|
| `adg_sqlite` | `AgenticWorkflow-ADG-HTTP-MCP` | `http://127.0.0.1:8765/mcp` | `adg_health` | Windows Task Scheduler, one-minute native policy plus watchdog trigger |
| `memory` | `AgenticWorkflow-Memory-HTTP-MCP` | `http://127.0.0.1:8766/mcp` | `memory_health` | Windows Task Scheduler, one-minute native policy plus watchdog trigger |

Both tasks use interactive current-user logon, limited run level, logon and repeating triggers, `StartWhenAvailable`, battery execution, unlimited execution time, restart count `255`, and `IgnoreNew`.

### Test and live evidence

- Baseline focused tests: 12 collected, 12 passed.
- Test-first red run: 8 collected, 7 failed, 1 passed because lifecycle files were absent.
- Focused implementation run: 20 collected, 20 passed.
- PowerShell parser validation: PASS for all six touched `.ps1`/`.psd1` lifecycle files.
- Config sync/check: PASS, 9 servers; user projection reason `ok`.
- Prelaunch `-NoLaunch`: PASS with both route invariants and both health-tool probes.
- Shortcut install: PASS at the current-user desktop using stable target `shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App`.
- Direct ADG probe: PASS; initialize true, tools/list 19, `adg_health` true, SQLite and Redis healthy.
- Direct Memory probe: PASS; initialize true, tools/list 16, `memory_health` true.
- Idempotency: PASS; second install returned `unchanged` and ensure returned `already_healthy` for both services.

### Restart proof

Only PIDs proven by endpoint listener, live runner receipt, live runner process, and exact module command line were terminated.

- ADG: old PID `37716` -> new PID `41176`; replacement appeared after about 34 seconds; initialize, tools/list, and `adg_health` passed.
- Memory: old PID `6608` -> new PID `39432`; replacement appeared after about 44 seconds; initialize, tools/list, and `memory_health` passed.

The earlier native-policy-only attempts did not restart on-demand instances. Those failures drove the stable exit-code normalization and repeating Task Scheduler watchdog; they are not counted as successful proof.

### Active Codex session

All four live calls through the active Codex tool surface passed:

- `mcp__adg_sqlite__adg_health`: status `ok`.
- `mcp__adg_sqlite__adg_process_identity`: PID `41176`.
- `mcp__memory__memory_health`: status `ok`, final PID `25068`.
- `mcp__memory__mem_process_identity`: final PID `25068`.

The endpoint-matched PostToolUse ledger did not update because these deferred calls were nested under `functions.exec`, while the hook matcher observes top-level `mcp__.*` events. Consequently both diagnosis commands still report `codex_http_route_unproven`. No environment override or synthetic ledger write was used.

### Operator commands

```powershell
# Install/repair and ensure healthy
pwsh -NoProfile -File .\ops_scripts\windows\codex_mcp_service_tasks.ps1 -Install -EnsureRunning -Json

# Status only
pwsh -NoProfile -File .\ops_scripts\windows\codex_mcp_service_tasks.ps1 -Status -Json

# Verify the supported prelaunch path without opening Codex
pwsh -NoProfile -File .\ops_scripts\windows\launch_codex_agentic.ps1 -RepoRoot $PWD -NoLaunch -Json

# Install/repair the supported desktop shortcut
pwsh -NoProfile -File .\ops_scripts\windows\install_codex_agentic_shortcut.ps1 -RepoRoot $PWD -Json

# Remove only the two managed tasks
pwsh -NoProfile -File .\ops_scripts\windows\codex_mcp_service_tasks.ps1 -Uninstall -Json
```

Normal daily use is the `Codex — Agentic Workflow` shortcut. Foreign listeners fail closed and are never killed automatically.

### Remaining risks and pending proof

1. Physical reboot/logon verification is pending. After reboot run `pwsh -NoProfile -File .\ops_scripts\windows\codex_mcp_service_tasks.ps1 -Status -Json`; both services must report logon plus time triggers, task `Running`, ownership `managed`, and overall `healthy`.
2. Endpoint-matched proof ledger acceptance remains pending despite successful active-session calls. Start a fresh task from the managed shortcut and rerun the four live tools plus both diagnosis commands.
3. Repo governance verification is blocked by pre-existing `C:\Git\Agentic-Workflow-FRESH\.agents`, reported as `repo_duplicate_enforcement_home`. This path was not created or modified by this change.

Foreign-port fail-closed proof also passed: temporary non-MCP listener PID `41036` occupied `8766`; ensure returned exit `1`, classified `foreign_port_conflict`, and left that PID alive. The test exposed and fixed a watchdog/ensure race by making unhealthy repair an atomic disable, verified cleanup, re-enable, and single-start transaction. Memory was restored healthy and managed at final PID `25068`.

Rejected fixes remain: `required = false`, primary stdio rollback, timeout inflation, process-only readiness, and port-only readiness.
