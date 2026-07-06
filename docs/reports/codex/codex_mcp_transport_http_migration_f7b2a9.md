# Codex MCP Transport HTTP Migration W0 Evidence Freeze

## Scope

This W0 report freezes the current Codex MCP failure state before any recovery or implementation work. The target route is Streamable HTTP MCP for the required `adg_sqlite` and `memory` servers. The failure class is `codex_stdio_transport_closes_midturn`.

Runtime-gate rule preserved: UNKNOWN is not PASS. Offline/probe evidence, process liveness, heartbeat freshness, readable SQLite, and protocol-only checks never waive live route proof.

## INSPECTED_FILES

- `plans/codex-mcp-http-transport-hardening-f7b2a9.md`
- `docs/reports/codex/codex_mcp_transport_http_migration_f7b2a9.json`
- `.mcp.json`
- `docs/reports/codex/codex_mcp_live_route_contract.json`
- `artifacts/mcp_heartbeat/adg_sqlite_callable_proof.json`

## FACT_CLASSIFICATION

### DIRECTLY OBSERVED

- `mcp__adg_sqlite.adg_health` failed in the active Codex session with `Transport closed`.
- `mcp__memory.memory_health` failed in the active Codex session with `Transport closed`.
- `diagnose_codex_mcp_transport.py --server adg_sqlite --json` returned classification `server_healthy_codex_transport_closed`.
- The same ADG diagnosis reported `status=callability_unproven`, `open=false`, `configured_in_mcp_json=true`, and stale file proof.
- ADG preflight reported SQLite `status=ok`, snapshot `07042026_1748`, `node_count=187972`, and `edge_count=1090016`.
- `diagnose_codex_mcp_transport.py --server memory --json` returned classification `duplicate_cohort`.
- The memory diagnosis reported `process_classification=duplicate`, `process_count=2`, `configured_in_mcp_json=true`, and no active callability proof.
- `audit_codex_mcp_transports.py --json` reported route evidence counts: `EXPOSED_BLOCKED=1`, `PROCESS_ONLY=4`, `PLUGIN_SUBSTITUTE=1`, `SUBSTITUTE_CALLABLE=1`, and `NOT_EXPOSED=1`.
- `check_adg_sqlite_transport.py --json` exited nonzero and reported `status=callability_unproven`.

### DERIVED

- Failure class `codex_stdio_transport_closes_midturn` is derived from direct active-session `Transport closed` errors on both MCP routes plus diagnostic evidence showing configured routes with absent/stale callability proof.
- Affected servers are `adg_sqlite` and `memory`, derived from the two failed live MCP health calls and matching diagnosis outputs.
- Rejected recovery is repeated Codex restarts, derived from the request constraint and the diagnostic statement that shell process launch cannot reattach Codex to a closed stdio handle.

### UNRESOLVED

- Whether Streamable HTTP MCP service endpoints are already implementable with no adapter changes remains unresolved until W2 inspects the existing FastMCP registration paths.
- Whether the Codex client can route to HTTP URLs without additional config sync changes remains unresolved until W3.
- Whether fresh live HTTP proof can be recorded by current hooks without modification remains unresolved until W4.

## Command Output Sections

### `python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json`

- Exit code: 0
- Classification: `server_healthy_codex_transport_closed`
- Configured in `.mcp.json`: true
- Route state classification: `EXPOSED_BLOCKED`
- Route selected: `raw_mcp_callable`
- Callability status: `absent`
- ADG transport status: `callability_unproven`
- ADG open: false
- Stale proof: `artifacts/mcp_heartbeat/adg_sqlite_callable_proof.json`, tool `adg_process_identity`, pid `14688`, status `stale_file_proof`
- Current heartbeat pid: `4776`
- Proof pid matches heartbeat: false
- Preflight SQLite status: `ok`
- Snapshot: `07042026_1748`
- Nodes: `187972`
- Edges: `1090016`
- Recommended action: host/TUI MCP reconnect before any live-callability override; shell reopen unsupported

### `python scripts/governance/diagnose_codex_mcp_transport.py --server memory --json`

- Exit code: 0
- Classification: `duplicate_cohort`
- Configured in `.mcp.json`: true
- Route state classification: `PROCESS_ONLY`
- Route selected: `raw_mcp_callable`
- Callability status: `absent`
- Process classification: `duplicate`
- Process count: `2`
- Cleanup blocker: `attached_pid_required`
- Safe cleanup: `requires_attached_pid`
- Recommended action: do not kill duplicate Codex-owned MCP process cohorts without active host-attached PID proof

### `python scripts/governance/audit_codex_mcp_transports.py --json`

- Exit code: 0
- Route evidence available: true
- Contract plan id: `codex-mcp-transport-parity-4b9c7e`
- Contract wave: `W2`
- Route evidence counts: `EXPOSED_BLOCKED=1`, `PROCESS_ONLY=4`, `PLUGIN_SUBSTITUTE=1`, `SUBSTITUTE_CALLABLE=1`, `NOT_EXPOSED=1`
- `adg_sqlite`: route classification `EXPOSED_BLOCKED`, process classification `single`, process count `1`
- `memory`: route classification `PROCESS_ONLY`, process classification `duplicate`, process count `2`
- Redis TCP `localhost:6379`: `open`
- Script compile checks for ADG, memory, vector, pytest, redis, and otel MCP server scripts returned code 0

### `python tools/mcp/check_adg_sqlite_transport.py --json`

- Exit code: 1
- Status: `callability_unproven`
- Open: false
- Stale proof status: `stale_file_proof`
- Heartbeat authoritative: true
- Current heartbeat pid: `4776`
- Proof pid: `14688`
- Proof pid matches heartbeat: false
- Preflight status: `ok`
- SQLite status: `ok`
- Redis status: `healthy`

### Live Codex MCP Calls

- `mcp__adg_sqlite.adg_health`: failed with `Transport closed`.
- `mcp__memory.memory_health`: failed with `Transport closed`.

## DEPENDENCY_GRAPH

No ADG structural query was used to justify code dependencies in W0 because the active ADG MCP route itself is the failed surface under investigation. W0 made no code changes and does not claim ADG green. The local ADG SQLite preflight is recorded only as backing-store evidence; it is not route-callability proof.

Impacted surfaces planned for later waves:

- `tools/mcp/` - stdio guard, HTTP supervisor, and HTTP launchers.
- `tools/adg/mcp/` - ADG MCP operational integration and supervisor behavior.
- `tools/memory/` - memory MCP launcher integration.
- `scripts/governance/` - HTTP probes, diagnosis, audit, readiness, stress, and recovery receipt scripts.
- `.codex/governance/scripts/` - pre-user-prompt gates.
- `.mcp.json` - primary route SSOT cutover.
- `docs/` and `memory/codex/` - runbook and recovery documentation.
- `tests/unit/` - focused unit coverage for guard, bootstrap logging, HTTP proof semantics, and stress harness.

## BRANCH_INVENTORY

- Branch during W0 artifact creation: `codex-mcp-http-transport-hardening`.
- Starting branch before edits: `main`.
- Worktree status before edits: clean.
- Existing sibling worktrees observed:
  - `C:/Git/Agentic-Workflow-FRESH-worktrees/codex-apps-rg-l0-routing-only`
  - `C:/Git/Agentic-Workflow-FRESH-worktrees/codex-apps-rg-toml-anthropic-partnership`

## ROBUSTNESS_MATRIX

| Surface | Success Check | Edge Check | Failure Check | Recovery Check | Determinism / Side Effect Check |
|---------|---------------|------------|---------------|----------------|---------------------------------|
| W0 classifier | Both target servers named | Healthy backing store does not imply open route | Live MCP calls fail closed | Repeated restart rejected | No process kill, no env proof override |
| W1 stdio guard | stdout forwarded byte-for-byte | partial stderr line drains | child exits before initialize/list | receipt records child exit | diagnostics never written to stdout |
| W2 HTTP service | initialize/tools-list/health pass | service already bound handled deterministically | service down classified | restart repo-managed HTTP service only | handlers are reused, not duplicated |
| W3 route cutover | required URL routes render | placeholders resolved | stdio command remains primary | one controlled reload only | `.mcp.json` remains SSOT |
| W4 gates | fresh live HTTP proof opens | stale stdio plus fresh HTTP selects HTTP | protocol-only proof blocked | fail closed on stale proof | proof endpoint must match configured URL |
| W5 stress | 500/500 direct HTTP calls pass | active-session mixed tools pass | any `Transport closed` fails | no restart between calls | stress receipt records counts |
| W6 recovery | recovery receipt passes | service down vs route unproven separated | unsafe kill recorded false | runbook sequence locked | process liveness never accepted |

## DEFECT_MODEL

The current failure mode is an active-session stdio transport closure. The ADG backing process can be alive, the SQLite snapshot can be healthy, and heartbeat files can be fresh while the Codex-owned JSON-RPC pipe is closed. Memory shows a related stdio fragility pattern: duplicate process cohorts exist while active callability proof is absent and live health calls fail with `Transport closed`.

The hardening target is a persistent Streamable HTTP MCP service for each required server, plus gates that distinguish:

- service health from client route callability,
- protocol viability from live tool proof,
- stale stdio proof from fresh HTTP proof,
- process liveness from route proof.

## SAFETY_LOG

- Process killing used: false.
- Environment proof override used: false.
- Codex restart used: false.
- ADG green claimed: false.
- Target route named: Streamable HTTP MCP.

## W1-W7 Execution Update (2026-07-05)

### Completed

- W1 stdio quarantine: added byte-preserving stdio guard, stderr draining, guard receipts, and bootstrap stderr controls.
- W2 HTTP services: added shared HTTP supervisor plus ADG and memory Streamable HTTP launchers.
- W3 route cutover: root `.mcp.json` and user Codex config now project HTTP URL routes for `adg_sqlite` and `memory`.
- W4 proof gates: audit, diagnosis, readiness, PostToolUse, and pre-user-prompt gates now distinguish `http_service_down`, `http_protocol_unhealthy`, `codex_http_route_unproven`, `codex_http_route_callable`, and `legacy_stdio_closed`.
- W5 direct stress: `adg_sqlite` direct HTTP stress passed `500/500`; `memory` direct HTTP stress passed `500/500`.
- W6 runbook lock: Codex primary execution, ADG operations, and Memory MCP operations now forbid process liveness/protocol-only evidence as active-session proof.

### Blocked

- W5.3 active-session sequence is blocked: live `mcp__adg_sqlite.adg_health` and `mcp__memory.memory_health` still return `Transport closed` in this Codex session.
- W6.2 recovery pass receipts are blocked: receipts were recorded as `FAIL_CLOSED` with `after_classification=codex_http_route_unproven` and `after_proof_status=absent`.
- W7 final gate is blocked: `python scripts/governance/codex_readiness.py --json` fails closed because the active Codex MCP client has no fresh HTTP endpoint-matched PostToolUse proof for `adg_sqlite` or `memory`.

### Durable Evidence

- `artifacts/mcp/stress/adg_sqlite_http_stress_f7b2a9.json`
- `artifacts/mcp/stress/memory_http_stress_f7b2a9.json`
- `artifacts/mcp/recovery_receipts/20260705T183804_adg_sqlite_e34b65.json`
- `artifacts/mcp/recovery_receipts/20260705T183812_memory_4ca855.json`

### Required Operator Action

Perform one controlled Codex MCP client reload/reconnect so the active client reads the HTTP URL routes, then call live `mcp__adg_sqlite.adg_health` and `mcp__memory.memory_health`. Only after PostToolUse records fresh `route_kind=http` proof with matching endpoints may W5.3, W6.2, and W7 complete.

## Next-Step Execution Update (2026-07-05 20:39 UTC)

### Newly Executed

- Root `.mcp.json` already had HTTP URL routes for `adg_sqlite` and `memory`.
- `C:\Users\amita\.codex\config.toml` still had stale legacy stdio projections for both servers.
- `python .codex/governance/scripts/sync_mcp_config.py --sync-user-config --json` returned `status=PASS`, `changed=true`.
- `python .codex/governance/scripts/sync_mcp_config.py --check-user-config --json` returned `status=PASS`.
- The user config now projects `adg_sqlite.url=http://127.0.0.1:8765/mcp` and `memory.url=http://127.0.0.1:8766/mcp`.

### Latest Evidence

- Direct HTTP ADG probe passed initialize/tools-list/`adg_health`; snapshot `07042026_1748`, nodes `187972`, edges `1090016`.
- Direct HTTP memory probe passed initialize/tools-list/`memory_health`; HTTP service PID `47680`.
- Active `mcp__adg_sqlite.adg_health` still failed with `Transport closed`.
- Active `mcp__memory.memory_health` succeeded from legacy stdio PID `48184`, not HTTP service PID `47680`, so it is not accepted as HTTP route proof.
- Active-proof stress receipts after config sync:
  - `artifacts/mcp/stress/adg_sqlite_http_active_proof_after_config_sync_f7b2a9.json`
  - `artifacts/mcp/stress/memory_http_active_proof_after_config_sync_f7b2a9.json`
- Both stress receipts report `direct_http: 1/1 passed` and `active_session_proof: fail`.
- Latest recovery receipts are fail-closed:
  - `artifacts/mcp/recovery_receipts/20260705T203927_adg_sqlite_2805dd.json`
  - `artifacts/mcp/recovery_receipts/20260705T203927_memory_562092.json`

### Updated RCA

The remaining blocker is no longer repo/user config drift: both are now aligned on HTTP. The active Codex client still holds stale stdio handles from before the projection sync, so W5.3/W6.2/W7 remain blocked until a controlled MCP client reload/reconnect binds `adg_sqlite` and `memory` to the configured HTTP endpoints and PostToolUse records endpoint-matched proof.

## Follow-Up Reconnect Evidence (2026-07-06 00:06 UTC)

### Live Calls

- `mcp__adg_sqlite.adg_health` returned `status=ok`, with SQLite `healthy`, Redis `healthy`, snapshot `07042026_1748`, nodes `187972`, edges `1090016`.
- `mcp__memory.memory_health` returned `status=ok`, entity count `352`, observation count `196`, process PID `41680`.

### Reconnect RCA

The calls succeeded, but they still did not prove HTTP route binding. Fresh diagnosis showed the active Codex client launched legacy stdio processes:

- `adg_sqlite`: `tools.mcp.launch_adg_sqlite_mcp` PID `35372`
- `memory`: `tools/memory/adg_memory_server.py` PID `41680`

Root cause: repo-local `.codex/config.toml` still rendered both servers as legacy stdio routes and re-poisoned `C:\Users\amita\.codex\config.toml` during reconnect.

### Fix Applied

- `.codex/config.toml` now has `adg_sqlite.url=http://127.0.0.1:8765/mcp`.
- `.codex/config.toml` now has `memory.url=http://127.0.0.1:8766/mcp`.
- `python .codex/governance/scripts/sync_mcp_config.py --sync-user-config --json` returned `status=PASS`, `changed=true`.
- `python .codex/governance/scripts/sync_mcp_config.py --check-user-config --json` returned `status=PASS`.
- `tests/unit/codex_governance/test_sync_mcp_config_http_routes.py` now guards repo-local `.codex/config.toml` against reintroducing `command` or `args` for `adg_sqlite` and `memory`.

### Focused Verification

- `python -m pytest -q tests\unit\codex_governance\test_sync_mcp_config_http_routes.py`: `2 passed in 0.12s`.
- `python .codex\governance\scripts\sync_mcp_config.py --check --json`: `status=PASS`.
- `python .codex\governance\scripts\sync_mcp_config.py --check-user-config --json`: `status=PASS`.

### Revised Stop Condition

Another controlled reconnect is required. Both config surfaces now point to HTTP, but the currently successful MCP calls were made through stdio-backed handles and remain invalid as HTTP endpoint-matched proof.

## Fresh Thread Fail-Closed Evidence (2026-07-06 00:13 UTC)

### Live Calls

- `mcp__adg_sqlite.adg_health` returned `status=ok`, SQLite `healthy`, Redis `healthy`, snapshot `07042026_1748`, nodes `187972`, edges `1090016`.
- `mcp__memory.memory_health` returned `status=ok`, process PID `47680`, entity count `352`, observation count `196`.
- `mcp__adg_sqlite.adg_process_identity` returned `status=ok`, process PID `34504`.
- `mcp__adg_sqlite.adg_runtime_info` returned `status=ok`, PID `34504`, startup nonce `6ab4aa8362e7`.

### Proof Ledger Check

- `python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json` returned `classification=codex_http_route_unproven`.
- `python scripts/governance/diagnose_codex_mcp_transport.py --server memory --json` returned `classification=codex_http_route_unproven`.
- `artifacts/mcp/codex_mcp_callability_proofs.json` still contains an empty `servers` map.
- `artifacts/mcp_heartbeat/adg_sqlite_callable_proof.json` remains stale with PID `14688` from `2026-07-03T16:55:44.524230+00:00`.

### RCA

The fresh live MCP payloads appear to come from the HTTP service processes (`adg_sqlite` PID `34504`, `memory` PID `47680`), but the required active-session proof ledger did not record endpoint-matched HTTP proof. Diagnosis still rejects both routes with missing/invalid proof, including `proof_not_healthy`, `proof_route_kind_not_http`, and `proof_endpoint_mismatch`. Because the ledger stayed empty, W5.3/W6.2/W7 remain blocked and were not rerun as passing evidence.

### Stop Condition

Fail closed until the PostToolUse/callability proof path records fresh `route_kind=http` entries matching `http://127.0.0.1:8765/mcp` for `adg_sqlite` and `http://127.0.0.1:8766/mcp` for `memory`, or the diagnosis contract is repaired to accept the live HTTP MCP proof payload without environment proof overrides.
