# ADR-022: MCP Pre-Gate Hang Hardening and Session-State Unification

**Date:** 2026-04-19
**Status:** Accepted
**Deciders:** Engineering + Codex pair session
**Supersedes:** None (extends ADR-021)
**Impact Layers:** L_TOOLS, L_OPS, L_SHARED
**Filename:** ADR-022-mcp-gate-hang-hardening.md

## Summary

Eliminate all catastrophic hang paths in `pre_mcp_gate.py` and unify `session_state` derivation across the three hook scripts to stop the memory-first gate from re-firing after `mem_recall_session_start`.

## Context

MCP productivity was being killed by three interacting issues:

1. **5-minute synchronous hang risk**: `check_adg_gate` and `check_memory_gate` called `_auto_generate_adg(repo_root)`, which spawned `python tools/generate_full_adg.py` with `timeout=300`. Any ADG tool call when `artifacts/adg/adg_indexed_*.sqlite` was missing would block Codex for up to 5 minutes inside a pre-hook.
2. **Session-state drift**: Each of the three hook scripts (`pre_mcp_gate`, `post_mcp_audit`, `pre_prompt_classifier`) derived `_session_id` differently. `pre_mcp_gate` fell back to `"default"`; the other two fell back to `os.getppid()`. When `VSCODE_PID` was inherited inconsistently by hook subprocesses on Windows, the three hooks read/wrote different `session_state_*.json` files. Result: the memory-first gate re-blocked every turn because `post_mcp_audit` wrote `memory_recalled=True` to one file and `pre_mcp_gate` read `False` from another.
3. **Gate ceremony friction**: Every non-recovery tool call ran through the memory-first gate plus the pytest sequencing gate (TTL 300s) plus per-server health probes. Even pure read-only tools (`adg_find_node`, `redis_keys`, `API-query-data-source`) were blocked until `mem_recall_session_start` ran first.

The compound effect was user-visible as MCP hangs and cancelled tool calls.

## Decision

Implement a six-part hardening to eliminate hang risk and restore gate consistency.

### 1. Neutralize `_auto_generate_adg`

`@c:\Git\Agentic-Workflow\.windsurf\scripts\pre_mcp_gate.py:509-528` — `_auto_generate_adg` is now a no-op that returns `False` immediately with a clear stderr message. Callers (`check_adg_gate`, `check_memory_gate`) fall through to `_exit_block` with an actionable "run `python tools/generate_full_adg.py` manually" error.

**Principle:** pre-hooks MUST NEVER perform long-running (>5s) synchronous work. Bootstrap is a user operation, not a gate operation.

### 2. Shared session-id helper

`@c:\Git\Agentic-Workflow\.windsurf\scripts\_session_id_shared.py:1-48` — new canonical derivation. All three hook scripts import `derive_session_id(repo_root)`.

Derivation priority:
1. `WINDSURF_SESSION_ID`
2. `CASCADE_SESSION_ID`
3. `VSCODE_PID`
4. **`repo-<sha1(repo_root)[:12]>`** — deterministic fallback (replaces the non-deterministic `"default"` and `os.getppid()` fallbacks)

Call sites updated in:
- `@c:\Git\Agentic-Workflow\.windsurf\scripts\pre_mcp_gate.py:130-142`
- `@c:\Git\Agentic-Workflow\.windsurf\scripts\post_mcp_audit.py:30-36`
- `@c:\Git\Agentic-Workflow\.windsurf\scripts\pre_prompt_classifier.py:33-39`

### 3. Read-only tool exemption from memory-first gate

`@c:\Git\Agentic-Workflow\.windsurf\scripts\pre_mcp_gate.py:309-401` — new `_memory_gate_readonly_tools` set unions 60+ read-only tools across `adg_sqlite`, `memory`, `redis`, `notion`, `otel_mcp`, `vector_db`, `deepwiki`, `GitKraken`, `enhanced_http`, `pytest_mcp`. These bypass the memory-first gate because they are pure observations that do not depend on session context.

### 4. Resilient session-state read

`@c:\Git\Agentic-Workflow\.windsurf\scripts\pre_mcp_gate.py:248-278` — `_read_session_state` now falls back to the newest non-smoke `session_state_*.json` if the primary resolved file is absent. Protects against residual session_id drift.

### 5. Emergency bypass + stale-file cleanup

`@c:\Git\Agentic-Workflow\.windsurf\scripts\pre_mcp_gate.py:1360-1392`:

- `MCP_EMERGENCY_BYPASS=1` → `main()` returns 0 immediately, bypassing ALL probes. Escape hatch for triage.
- `_purge_stale_pytest_results()` removes `.pytest_results_*.xml` >1h old on every gate invocation.
- `_purge_stale_session_states()` extended to aggressively clean `*_smoke.json` (>1h cutoff vs. 24h for standard files).

### 6. Pytest serial collection + response cleanup

`@c:\Git\Agentic-Workflow\tools\mcp\pytest_support\services.py:54-59` — `discover_tests` now passes `-n 0` to override `pytest.ini addopts -n 24`. 24 xdist workers importing the full conftest chain for a simple probe caused stdio contention that presented as an MCP hang.

`@c:\Git\Agentic-Workflow\tools\mcp\pytest_support\services.py:142-151` — strip tqdm progress-bar lines (`"Processing: Nitem [00:00, ?item/s]"`) from `run_tests` stderr to clean up MCP responses.

### 7. Extended pytest probe TTL

`@c:\Git\Agentic-Workflow\.windsurf\scripts\pre_mcp_gate.py:172-176` — `pytest_probe_ttl_seconds` from 300 → 1800 to reduce ceremony friction on multi-test sessions.

## Consequences

### Positive

- Zero synchronous subprocess hangs >5s in any pre-hook path.
- Memory-first gate no longer re-fires on every turn after the first `mem_recall_session_start`.
- Read-only diagnostic queries (`adg_find_node`, `redis_keys`, `API-query-data-source`, etc.) complete without gate ceremony.
- `discover_tests` response time reduced from stdio-contention-risk to deterministic ~2s.
- Orphan artifact accumulation (`.pytest_results_*.xml`, `session_state_*_smoke.json`) auto-cleaned.
- `MCP_EMERGENCY_BYPASS` provides a user-visible escape hatch for future gate issues.

### Negative

- ADG SQLite bootstrap is now a user action, not automatic. Users who wipe `artifacts/adg/` must manually run `python tools/generate_full_adg.py` before any ADG MCP call. Traded off automatic bootstrap for reliable latency.
- Read-only tool exemption list is maintained by hand. New read-only MCP tools must be added to `_memory_gate_readonly_tools` or they'll re-trigger the gate.

### Sync Gates (existing, no new script)

Two pre-existing gates validate AGENTS.md ↔ `.mcp.json` consistency, both now wired into `.pre-commit-config.yaml`:

- `@c:\Git\Agentic-Workflow\ops_scripts\ci\check_mcp_sync_integrity.py` — strict content comparison (hook id `mcp-sync-integrity` / T6b)
- `@c:\Git\Agentic-Workflow\ops_scripts\ci\check_agents_mcp_coverage.py` — coverage check (hook id `agents-mcp-coverage` / T6c, added this session)

### Neutral

- Test `test_falls_back_to_stable_default_when_no_markers` updated to `test_falls_back_to_repo_root_hash_when_no_markers` reflecting the new deterministic fallback.

## Validation

- All 5 modified hook/service files pass `py_compile`.
- `_check_emergency_bypass` verified to return 0 with stderr message when `MCP_EMERGENCY_BYPASS=1`.
- Shared derivation produces stable `repo-648bfb4a27f8` across invocations when `VSCODE_PID` absent.
- 8 originally failing pytest tests now pass (separate AP-18 content drift fix, same session).
- Direct pytest collection with `-n 0`: 2.0s, exit 0.

## References

- ADR-021 — legacy editor hooks cannot auto-recover red MCP servers (supersedes in spirit the auto-generation fallback idea)
- `.claude/governance/scripts/_session_id_shared.py` — canonical session_id derivation
- `artifacts/windsurf/mcp_health/20260419_1126.json` — pre-hardening MCP sweep evidence
- `docs/reports/plans/mcp-gate-hang-hardening-2026-04-19.md` — full RCA and implementation log
- Memory MCP entities: `DebugSession:2026-04-19-MCPHooksAndPytest`, `ProceduralPattern:legacy editorHookSessionIdConsistency`, `ProceduralPattern:PytestMCPDiscoveryServialCollection`

## Operational Knobs

```bash
# Panic button — disables ALL pre_mcp_gate checks for this shell's MCP calls
set MCP_EMERGENCY_BYPASS=1

# Re-enable (unset)
set MCP_EMERGENCY_BYPASS=
```
