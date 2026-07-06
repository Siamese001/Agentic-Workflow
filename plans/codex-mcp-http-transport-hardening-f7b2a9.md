---
plan_id: codex-mcp-http-transport-hardening-f7b2a9
plan_format: v2
plan_type: infra
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Codex MCP HTTP Transport Hardening

Move the fragile Codex stdio routes for `adg_sqlite` and `memory` to persistent Streamable HTTP MCP services with fail-closed live callability proof.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: BLOCKED
CURRENT_WAVE: W7
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-07-05

---

## Context (SCQA)

- Situation - `adg_sqlite` and `memory` are required MCP routes in `.mcp.json`; ADG SQLite backing data is healthy, and memory is configured.
- Complication - Live Codex MCP calls to both routes fail with `Transport closed`; process liveness and stale proof files can make the backing services look healthier than the active Codex route.
- Question - How do we harden Codex MCP transport so required ADG and memory routes remain callable without repeated Codex restarts or unsafe process cleanup?
- Answer - Freeze the current failure class, quarantine stdio, add persistent Streamable HTTP services, cut the MCP SSOT to URL routes, and update gates so only fresh live HTTP route proof can mark the route open.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1, W0.2, W0.3 | Evidence freeze and failure classifier | ~4K | Read-only evidence is enough to classify the current route failure | DONE | Plan and paired W0 reports exist; affected servers and target route are named |
| W1 | W1.1, W1.2, W1.3 | Stdio quarantine and guard wrapper | ~12K | Existing stdio launchers remain available as fallback probes | DONE | Guard preserves stdout byte-for-byte, drains stderr, and records receipts |
| W2 | W2.1, W2.2, W2.3 | Persistent HTTP MCP services | ~18K | Existing FastMCP tool registration can be reused behind HTTP launchers | DONE | ADG and memory HTTP preflight plus direct protocol probes pass |
| W3 | W3.1, W3.2, W3.3 | MCP SSOT cutover to HTTP | ~10K | One controlled MCP client config reload is allowed after route cutover | DONE | `.mcp.json` and rendered Codex config use required HTTP URL routes |
| W4 | W4.1, W4.2, W4.3 | Gates and diagnosis understand HTTP proof | ~18K | Live Codex tool proof remains distinct from protocol and heartbeat proof | DONE | Fresh HTTP live proof opens the route; stale or protocol-only proof fails closed |
| W5 | W5.1, W5.2, W5.3 | No-restart stress harness | ~14K | HTTP services can be validated directly before active-session proof | BLOCKED | Direct 500-call stress passed; 50-call active-session sequence blocked by Codex active route still returning `Transport closed` |
| W6 | W6.1, W6.2 | Recovery receipt and runbook lock | ~8K | Recovery receipt can record operator action without performing unsafe cleanup | BLOCKED | Runbooks locked; pass receipts blocked until active-session proof exists |
| W7 | W7.1, W7.2 | Final release gate | ~8K | Prior waves have produced fresh route and stress receipts | BLOCKED | Final readiness fails closed on missing active-session proof |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Capture read-only transport evidence | DONE |
| W0.2 | Classify current failure and safety constraints | DONE |
| W0.3 | Create W0 plan and reports | DONE |
| W1.1 | Add `tools/mcp/codex_stdio_guard.py` | DONE |
| W1.2 | Add stdio guard unit tests | DONE |
| W1.3 | Harden `tools/mcp/mcp_bootstrap.py` logging environment | DONE |
| W2.1 | Add shared HTTP service supervisor | DONE |
| W2.2 | Add ADG and memory HTTP launchers | DONE |
| W2.3 | Add or extend direct HTTP probe receipts | DONE |
| W3.1 | Change `.mcp.json` primary routes to HTTP URLs | DONE |
| W3.2 | Update MCP config sync and docs | DONE |
| W3.3 | Run sync checks and user-config sync | DONE |
| W4.1 | Add HTTP-aware classifications | DONE |
| W4.2 | Update readiness, diagnosis, and hook gates | DONE |
| W4.3 | Add fail-closed proof tests | DONE |
| W5.1 | Add direct HTTP stress harness | DONE |
| W5.2 | Add stress tests and reports | DONE |
| W5.3 | Run no-restart active-session proof sequence | BLOCKED |
| W6.1 | Update recovery receipt script and runbooks | DONE |
| W6.2 | Record ADG and memory recovery receipts | BLOCKED |
| W7.1 | Run final green matrix | BLOCKED |
| W7.2 | Close plan only after all final checks pass | BLOCKED |

---

## Out Of Scope

- Killing or manually pruning Codex-owned MCP processes.
- Setting `CODEX_MCP_CALLABLE_*` or attached-PID environment proof overrides.
- Claiming ADG is green from SQLite, heartbeat, port, or protocol-only evidence.
- Replacing ADG or memory business/tool logic instead of preserving existing handlers behind transport changes.
- Restarting Codex as a recovery path before HTTP service health and active route proof are checked.

---

## Wave 0 - Evidence Freeze / Failure Classifier

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: APPROVED_BY_USER - User approved W0 execution on 2026-07-05.

**Phases**:
- **W0.1** - Capture read-only transport evidence | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.2** - Classify current failure and safety constraints | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W0.3** - Create W0 plan and reports | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- No process killing.
- No environment proof override.
- No ADG green claim.
- Failure report names target route: Streamable HTTP MCP.

---

## Wave 1 - Stdio Quarantine / Guard Wrapper

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W1.1** - Add `tools/mcp/codex_stdio_guard.py` | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Add `tests/unit/tools/mcp/test_codex_stdio_guard.py` and `tests/unit/tools/mcp/test_mcp_bootstrap_logging.py` | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** - Update `tools/mcp/mcp_bootstrap.py` for stderr log path, stderr level, unbuffered Python, UTF-8 IO, and tokenizer parallelism controls | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Guard forwards Codex stdin to child stdin byte-for-byte.
- Guard forwards child stdout to Codex stdout byte-for-byte.
- Guard drains child stderr continuously to `artifacts/mcp/<server>.stderr.log`.
- Guard never writes diagnostics to stdout.
- Guard writes receipts to `artifacts/mcp/<server>_stdio_guard.jsonl`.
- Guard exits nonzero if child exits before initialize/tools-list.
- Heavy stderr stress does not corrupt stdout.
- Partial stderr lines do not hang the guard.
- Existing stdio servers remain documented fallback only.

---

## Wave 2 - Persistent HTTP MCP Services

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W2.1** - Add shared `tools/mcp/http_service_supervisor.py` | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Add `tools/mcp/launch_adg_sqlite_http_mcp.py` and `tools/mcp/launch_memory_http_mcp.py` | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** - Add or extend HTTP launcher receipts and `scripts/governance/probe_mcp_http_server.py` if absent | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- ADG binds `http://127.0.0.1:8765/mcp`.
- Memory binds `http://127.0.0.1:8766/mcp`.
- Existing FastMCP tool registration and handlers are preserved.
- Required HTTP tools include `adg_health`, `adg_process_identity`, `adg_runtime_info`, `memory_health`, and `mem_process_identity`.
- Preflight-only launchers pass for ADG and memory.
- Direct HTTP initialize, tools/list, and health probes pass without Codex restart.

---

## Wave 3 - MCP SSOT Cutover to HTTP

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: D

**Phases**:
- **W3.1** - Change `.mcp.json` routes for `adg_sqlite` and `memory` to HTTP URLs | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Update `.codex/governance/scripts/sync_mcp_config.py`, `docs/codex-primary-execution.md`, `tools/adg/mcp/OPERATIONS.md`, and generated quick reference if sync requires it | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.3** - Run MCP config sync check, dry-run, and user-config sync | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Rendered Codex config has URL route for `adg_sqlite`.
- Rendered Codex config has URL route for `memory`.
- Both routes remain `required = true`.
- No direct Python stdio command remains primary for `adg_sqlite` or `memory`.
- Exactly one controlled MCP client config reload is allowed after this wave.

---

## Wave 4 - Gates / Diagnosis Understand HTTP Proof

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: E

**Phases**:
- **W4.1** - Add classifications `http_service_down`, `http_protocol_unhealthy`, `codex_http_route_unproven`, `codex_http_route_callable`, and `legacy_stdio_closed` | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** - Update supervisor, audit, diagnosis, readiness, and pre-user-prompt gates | ~9K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.3** - Add tests for HTTP proof semantics and stale-proof rejection | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- HTTP initialize/tools-list is protocol viability only.
- Live Codex tool call proof is required for active-session callability.
- ADG opens only when route kind is HTTP, fresh live proof succeeded with an allowed proof tool, endpoint matches configured URL, and server is `adg_sqlite`.
- Port-open, curl-only, tools/list-only, stale proof, heartbeat-only, and readable-SQLite evidence are rejected as green.
- Targeted governance and hook tests pass.

---

## Wave 5 - No-Restart Stress Harness

WAVE_ID: W5
WAVE_STATUS: BLOCKED
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: F

**Phases**:
- **W5.1** - Add `scripts/governance/stress_codex_mcp_transport.py` | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** - Add stress tests and stress reports | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.3** - Run direct HTTP and active-session no-restart proof sequence | ~4K tokens | PHASE_STATUS: BLOCKED | PHASE_COMPLETE: NO

**Blocker**: Direct HTTP stress passed for both services (`500/500` ADG and `500/500` memory), but active Codex calls still return `Transport closed` in this session. Diagnosis classifies both routes as `codex_http_route_unproven`.

**Acceptance**:
- 0 `Transport closed`.
- 0 repeated Codex restarts.
- 0 stale proof accepted.
- 0 stdout protocol corruption.
- 500/500 ADG direct HTTP health calls pass.
- 500/500 memory direct HTTP health calls pass.
- 50/50 Codex active-session MCP calls pass.
- `codex_readiness.py` passes.
- Diagnosis classifies both `adg_sqlite` and `memory` callable.

---

## Wave 6 - Recovery Receipt / Runbook Lock

WAVE_ID: W6
WAVE_STATUS: BLOCKED
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: G

**Phases**:
- **W6.1** - Update recovery receipt script, Codex primary execution docs, ADG operations docs, and memory runbook | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W6.2** - Record ADG and memory recovery receipts for HTTP cutover | ~3K tokens | PHASE_STATUS: BLOCKED | PHASE_COMPLETE: NO

**Blocker**: ADG and memory receipts were recorded as `FAIL_CLOSED` because after-state remains `codex_http_route_unproven` with `after_proof_status=absent`. Passing receipts require active-session HTTP proof after Codex MCP client reload/reconnect.

**Acceptance**:
- If `adg_sqlite` or `memory` close mid-turn, runbooks check HTTP service health and active route proof age before restart.
- Only repo-managed HTTP MCP service restart is allowed when service health is down.
- Codex restart is reserved for config changes or inability to route to any configured MCP HTTP URL.
- Process liveness is never accepted as active-session proof.
- Recovery receipts report `recovery_status=PASS`, `after_classification=callable`, `after_proof_status=healthy`, `script_performed_recovery=false`, and `unsafe_process_kill_used=false`.

---

## Wave 7 - Final Release Gate

WAVE_ID: W7
WAVE_STATUS: BLOCKED
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: H

**Phases**:
- **W7.1** - Run final green matrix | ~6K tokens | PHASE_STATUS: BLOCKED | PHASE_COMPLETE: NO
- **W7.2** - Close plan only after all W7 checks pass | ~2K tokens | PHASE_STATUS: BLOCKED | PHASE_COMPLETE: NO

**Blocker**: `codex_readiness.py --json` fails closed on missing active-session route proof for `adg_sqlite` and `memory`; final close is blocked until Codex reloads/reconnects to the HTTP URL routes and live tool calls succeed.

**Acceptance**:
- `.mcp.json` primary routes for `adg_sqlite` and `memory` are HTTP URLs.
- `sync_mcp_config` projects HTTP URL routes into Codex config.
- Direct HTTP initialize/tools-list passes.
- Direct HTTP 500-call stress passes for both servers.
- Codex active-session health and identity calls pass for both servers.
- `codex_readiness.py` passes.
- Diagnosis classifies both servers callable.
- No stale stdio PID proof, manual process kill, or repeated Codex restart is used.

---

## Execution Details

### W0.1 - Capture Read-Only Transport Evidence

**Scope**: Run the requested commands and live route proof calls without cleanup or overrides.

**Commands**:
```bash
python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json
python scripts/governance/diagnose_codex_mcp_transport.py --server memory --json
python scripts/governance/audit_codex_mcp_transports.py --json
python tools/mcp/check_adg_sqlite_transport.py --json
```

**Live Codex proof calls**:
```text
mcp__adg_sqlite.adg_health
mcp__memory.memory_health
```

### W0.2 - Classify Failure

**Scope**: Freeze failure class as `codex_stdio_transport_closes_midturn` for `adg_sqlite` and `memory`.

**Evidence artifacts**:
- `docs/reports/codex/codex_mcp_transport_http_migration_f7b2a9.md`
- `docs/reports/codex/codex_mcp_transport_http_migration_f7b2a9.json`

### W1-W7 - Follow-On Execution

**Scope**: Each follow-on wave requires a separate approval checkpoint before edits, with no claim of route recovery until the wave-specific acceptance criteria pass.

---

## Gap Register

**GAP-1: HTTP server implementation detail**
- Details: Existing FastMCP registration shape must be inspected before choosing the least invasive HTTP launcher wiring.
- Impact: W2 may need a small adapter layer, but must not duplicate ADG or memory tool logic.

**GAP-2: Active Codex HTTP route proof mechanism**
- Details: W4 must define how fresh live Codex proof records endpoint, tool, server, and proof age after the URL route cutover.
- Impact: Protocol-only probes remain blocked until live proof semantics are implemented.

**GAP-3: Controlled reload handoff**
- Details: W3 allows one controlled MCP client config reload after route cutover.
- Impact: The reload step must be explicitly recorded so repeated Codex restarts remain rejected recovery.

---

## Definition of Done

DoD-1: Stdio failure frozen honestly.
- Evidence: W0 reports classify `codex_stdio_transport_closes_midturn`, name `adg_sqlite` and `memory`, reject repeated Codex restarts, and name Streamable HTTP MCP as target route.
- Status: DONE

DoD-2: Stdio fallback quarantined.
- Evidence: `python -m pytest -q tests/unit/tools/mcp/test_codex_stdio_guard.py tests/unit/tools/mcp/test_mcp_bootstrap_logging.py` passes.
- Status: DONE

DoD-3: HTTP services are directly viable.
- Evidence: ADG and memory preflight-only launchers pass, and `probe_mcp_http_server.py` passes initialize/tools-list/health for ports 8765 and 8766.
- Status: DONE

DoD-4: MCP SSOT routes are HTTP.
- Evidence: `.mcp.json`, rendered Codex config, and sync receipts show required URL routes for `adg_sqlite` and `memory`.
- Status: DONE

DoD-5: Gates fail closed on unproven callability.
- Evidence: Targeted governance and hook tests pass for stale proof, protocol-only proof, fresh HTTP proof, and legacy stdio proof precedence.
- Status: DONE

DoD-6: No-restart stress passes.
- Evidence: Direct 500-call HTTP stress passes for both servers and 50/50 active-session MCP calls pass without `Transport closed`.
- Status: BLOCKED - direct 500-call HTTP stress passed for both servers; active-session calls still return `Transport closed`.

DoD-7: Recovery runbook locked.
- Evidence: Recovery receipts pass with no script-performed recovery and no unsafe process kill.
- Status: BLOCKED - runbooks locked and fail-closed receipts recorded; pass receipts require active-session HTTP proof.

DoD-8: Final release matrix passes.
- Evidence: W7 green matrix is recorded, `codex_readiness.py` passes, and both diagnosis commands classify routes callable.
- Status: BLOCKED - readiness fails closed on `codex_http_route_unproven` for `adg_sqlite` and `memory`.

---

## Next-Step Execution Update (2026-07-05 20:39 UTC)

### Newly Executed

- Rechecked root `.mcp.json`: `adg_sqlite` and `memory` are HTTP URL routes.
- Found stale user Codex projection in `C:\Users\amita\.codex\config.toml`: both servers were still rendered as legacy stdio commands.
- Ran `python .codex/governance/scripts/sync_mcp_config.py --sync-user-config --json`: `status=PASS`, `changed=true`.
- Ran `python .codex/governance/scripts/sync_mcp_config.py --check-user-config --json`: `status=PASS`.
- Confirmed projected user config now has `adg_sqlite.url=http://127.0.0.1:8765/mcp` and `memory.url=http://127.0.0.1:8766/mcp`.

### Latest Proof State

- Direct HTTP probes still pass for both servers:
  - `adg_sqlite`: initialize/tools-list/`adg_health` passed; snapshot `07042026_1748`, nodes `187972`, edges `1090016`.
  - `memory`: initialize/tools-list/`memory_health` passed; HTTP service PID `47680`.
- Active Codex MCP handles did not hot-rebind after config sync:
  - `mcp__adg_sqlite.adg_health` still failed with `Transport closed`.
  - `mcp__memory.memory_health` succeeded, but the response came from legacy stdio PID `48184`, not the HTTP service PID `47680`; this is not accepted as HTTP endpoint-matched proof.
- `stress_codex_mcp_transport.py --require-active-proof` failed closed for both servers after `direct_http: 1/1 passed` and `active_session_proof: fail`.
- Latest diagnosis remains `codex_http_route_unproven` for both servers.
- Latest recovery receipts:
  - `artifacts/mcp/recovery_receipts/20260705T203927_adg_sqlite_2805dd.json`
  - `artifacts/mcp/recovery_receipts/20260705T203927_memory_562092.json`

### Current Stop Condition

The repo and user config are now aligned on HTTP, and the HTTP services are healthy. The remaining blocker is the already-attached Codex MCP client: it is still using stale stdio handles in this session and must be reconnected/reloaded before W5.3, W6.2, or W7 can pass.

### Follow-Up After First Reconnect (2026-07-06 00:06 UTC)

- Live calls succeeded, but diagnosis showed they were still served by legacy stdio processes:
  - `mcp__adg_sqlite.adg_health`: `status=ok`, but active process state used `tools.mcp.launch_adg_sqlite_mcp` PID `35372`.
  - `mcp__memory.memory_health`: `status=ok`, but active process state used `tools/memory/adg_memory_server.py` PID `41680`.
- Root cause: repo-local `.codex/config.toml` still rendered `adg_sqlite` and `memory` as legacy stdio routes and re-poisoned the user projection on reconnect.
- Fix applied: `.codex/config.toml` now uses:
  - `adg_sqlite.url=http://127.0.0.1:8765/mcp`
  - `memory.url=http://127.0.0.1:8766/mcp`
- User config was synced again: `python .codex/governance/scripts/sync_mcp_config.py --sync-user-config --json` returned `status=PASS`, `changed=true`.
- Regression guard added: `tests/unit/codex_governance/test_sync_mcp_config_http_routes.py` now asserts repo-local `.codex/config.toml` keeps `adg_sqlite` and `memory` on HTTP URL routes with no `command` or `args`.
- Focused test result: `2 passed in 0.12s`.

### Revised Stop Condition

Both repo-local and user-level Codex configs are now aligned on HTTP. Another controlled reconnect is required because the current successful live calls are still stdio-backed and cannot be accepted as HTTP endpoint-matched proof.

### Fresh Thread Fail-Closed Follow-Up (2026-07-06 00:13 UTC)

**Live calls in fresh thread**:

- `mcp__adg_sqlite.adg_health`: `status=ok`, SQLite `healthy`, Redis `healthy`, snapshot `07042026_1748`, nodes `187972`, edges `1090016`.
- `mcp__memory.memory_health`: `status=ok`, process PID `47680`, entity count `352`, observation count `196`.
- Additional ADG identity proof probes:
  - `mcp__adg_sqlite.adg_process_identity`: `status=ok`, process PID `34504`.
  - `mcp__adg_sqlite.adg_runtime_info`: `status=ok`, PID `34504`, startup nonce `6ab4aa8362e7`.

**Diagnosis after live calls**:

- `python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json` still returns `classification=codex_http_route_unproven`.
- `python scripts/governance/diagnose_codex_mcp_transport.py --server memory --json` still returns `classification=codex_http_route_unproven`.
- `artifacts/mcp/codex_mcp_callability_proofs.json` still has `"servers": {}`.
- `artifacts/mcp_heartbeat/adg_sqlite_callable_proof.json` is still stale (`proved_at=2026-07-03T16:55:44.524230+00:00`, PID `14688`).

**RCA**:

The fresh MCP calls appear to reach the HTTP service processes (`adg_sqlite` PID `34504`; `memory` PID `47680`), but the active-session callability ledger remains empty and no endpoint-matched HTTP proof is recorded. Diagnosis therefore correctly fails closed with `proof_not_healthy`, `proof_route_kind_not_http`, and `proof_endpoint_mismatch`. The stale stdio heartbeat/process cohort remains visible (`adg_sqlite` legacy launcher PID `35372`; memory legacy server PID `41680`), but it is not accepted as proof. W5.3, W6.2, and W7 were not rerun as green because the acceptance gate still rejects the proof ledger.

**Current stop condition**:

Fail closed until PostToolUse/callability proof recording writes fresh `route_kind=http` entries with endpoint `http://127.0.0.1:8765/mcp` for `adg_sqlite` and `http://127.0.0.1:8766/mcp` for `memory`, or the diagnosis contract is repaired to ingest the live HTTP MCP proof payload without env overrides.

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=codex-mcp-http-transport-hardening-f7b2a9 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=codex-mcp-http-transport-hardening-f7b2a9 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=codex-mcp-http-transport-hardening-f7b2a9 reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Supersedes

_None - net-new plan._

---

## Marker Quick Reference

Wave lifecycle markers:

```text
WAVE_START: plan=codex-mcp-http-transport-hardening-f7b2a9 wave=<N>
WAVE_COMPLETE: plan=codex-mcp-http-transport-hardening-f7b2a9 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=codex-mcp-http-transport-hardening-f7b2a9 phase=<W1.1>
PLAN_COMPLETE: plan=codex-mcp-http-transport-hardening-f7b2a9 note="<final outcome>"
```
