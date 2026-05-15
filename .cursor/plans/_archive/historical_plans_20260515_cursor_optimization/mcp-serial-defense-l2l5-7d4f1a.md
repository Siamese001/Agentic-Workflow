# Plan — MCP Serialization Defense, Layers 2–5

**ID**: `mcp-serial-defense-l2l5-7d4f1a`
**Status**: Draft (not implemented)
**Owner**: Cascade harness team
**Created**: 2026-04-25
**Tier**: T2 — multi-file, single concern (instrumentation), no cross-layer architectural change
**Related**: Layer 1 already shipped (`_serialization_sentinel.py` + 4 pre-* gates, see Notion MCP Registry entry `34d27693-f55c-816d-84d7-ccd9a62b78dc`)
**Sunset**: All five layers retire together when upstream `anthropics/claude-agent-sdk-typescript#41` ships in Windsurf

---

## Why These Layers Are Optional Reinforcement

Layer 1 (deterministic, dispatch-time block) covers the high-probability cases: any MCP↔`run_command`/`read_file`/`edit`/`write_to_file`/`multi_edit` pair. Windsurf has no pre-hook for native tools `todo_list`, `grep_search`, `find_by_name`, `list_dir`, `ask_user_question`, `skill`, so those cannot be detected from their side at dispatch time. Layers 2–5 close that gap through behavior shaping and post-hoc damage control.

**This plan does not refactor existing code paths** — it adds instrumentation and reminder surfaces. The constitutional §22 `ADG_GRAPH_LAYER_EVIDENCE` requirement applies to refactoring plans; this is an additive-instrumentation plan. ADG queries are still performed during execution to confirm fan-in for affected files (recorded in W1 P0).

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | L2.1 | Layer 2 — SR_MANDATE injection (pre-prompt) | ~3000 | `pre_prompt_classifier.py` MCP-intent detector already exists | Todo | Cascade emits `MCP_SERIAL_MANDATE:` in SR block when MCP intent present; unit test passes |
| **W2** | L3.1, L3.2 | Layer 3 — MCP response reminder wrapper | ~9000 | All 12 MCP servers use FastMCP `@mcp.tool()` decorators | Todo | Every MCP tool result begins with `[MCP_SERIAL_REMINDER]`; integration smoke pass; <20-token overhead per response |
| **W3** | L4.1 | Layer 4 — Hang auto-recovery watchdog | ~4000 | `mcp_invocation_ledger.sqlite` has p99 latency per server (ADR-050) | Todo | Watchdog injects `MCP_HANG_SUSPECTED:` marker in next pre-prompt when prior turn exceeded p99×3 |
| **W4** | L5.1 | Layer 5 — Session-start violations surfacer | ~2000 | `mcp_serialization_violations.jsonl` already maintained by Layer 0 audit | Todo | Banner appears in pre-prompt when ≥1 violation in last 24h; suppressed when zero |
| **W5** | V1, V2 | Verification — end-to-end + retirement readiness | ~3000 | All four layers shipped | Todo | All layers no-op when `mcp_serialization_ttl.json` `retired_after` is past; combined unit + integration suite ≥95% pass |

**Total**: ~21,000 tokens

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **L2.1** | Inject `MCP_SERIAL_MANDATE` into SR-block on MCP intent | `.windsurf/scripts/pre_prompt_classifier.py` (modify; ~30 LOC) + `tests/unit/ops_scripts/hooks/windsurf/test_pre_prompt_classifier.py` (extend) | Existing classifier already complex; injection point must not collide with ADG-first mandate or other SR-step-0 directives | 3000 | Todo |
| **L3.1** | Build shared `_response_reminder.py` decorator | `tools/mcp/_response_reminder.py` (NEW; ~80 LOC) + `tests/unit/tools/mcp/test_response_reminder.py` (NEW; ~10 tests) | FastMCP return-type semantics (str vs dict); decorator must preserve type contract; bypass via env var | 4000 | Todo |
| **L3.2** | Apply decorator to all 12 MCP server entry points | `tools/mcp/{adg_sqlite,memory,vector_db,redis,otel,pytest_mcp,task_manager,enhanced_http,deepwiki,filesystem_launcher}_server.py` + GitKraken + Notion wrappers (each: ~2-line import + 1 decoration) | Some servers wrap responses in TextContent objects; some use json.dumps; need per-server smoke test | 5000 | Todo |
| **L4.1** | Watchdog + pre-prompt marker injection | `.windsurf/scripts/mcp_hang_watchdog.py` (NEW; ~120 LOC) + extend `pre_prompt_classifier.py` (~10 LOC) + tests | Requires reading the existing `artifacts/ledgers/mcp_invocation.sqlite` p99 column; must fail-open if ledger missing | 4000 | Todo |
| **L5.1** | Session-start violations banner | `.windsurf/scripts/pre_user_prompt_hook_health_check.py` (modify; ~25 LOC) + tests | Banner must not exceed 5 lines; must be suppressed when count is zero to avoid noise | 2000 | Todo |
| **V1** | Combined unit + integration suite | All test files from W1–W4 | Layer interactions: e.g. Layer 5 banner shouldn't fire when Layer 4 marker is also fresh — define precedence | 1500 | Todo |
| **V2** | Sunset proof — TTL flag flips all layers off | `.windsurf/config/mcp_serialization_ttl.json` (test fixture only) + smoke run | Each layer must independently honor `_is_retired()`; centralize the check in `_serialization_sentinel.py` (already exported) | 1500 | Todo |

---

## Per-Phase Detail

### L2.1 — SR_MANDATE Injection

**What**: When `pre_prompt_classifier.py` detects MCP intent (existing `_detect_notion_intent`, `_detect_memory_intent`, ADG signals), inject one extra mandate line into the SR-block:

```
MCP_SERIAL_MANDATE: every mcp*_ call MUST be alone in its <function_calls> block — no sibling tools of any kind, including read_file/edit/todo_list/grep_search. Constitutional §25.
```

**Why**: Maximum-recency placement (per OpenDev §3.2 finding that system-prompt rules decay after 15+ tool calls). The graph-analysis skill solved a similar prompt-drift problem with the same pattern (memory `3064a042`).

**Files**:
- `@c:/Git/Agentic-Workflow/.windsurf/scripts/pre_prompt_classifier.py` — add `_MCP_SERIAL_MANDATE` constant, inject inside the SR-step-0 block when any MCP intent flag is true
- `@c:/Git/Agentic-Workflow/tests/unit/ops_scripts/hooks/windsurf/test_pre_prompt_classifier.py` — assert mandate appears for MCP-intent prompts and is absent for non-MCP prompts

**Success Criteria**:
1. Mandate text appears verbatim in classifier output when prompt contains any MCP-intent signal
2. Mandate is absent for pure-coding prompts (no MCP signal)
3. Existing classifier tests still pass

---

### L3.1 — Shared Response Reminder Decorator

**What**: A FastMCP-compatible decorator that prepends a one-line reminder to every MCP tool result:

```
[MCP_SERIAL_REMINDER] next mcp*_ call must be alone in its <function_calls> block (constitutional §25).
```

**Files**:
- `@c:/Git/Agentic-Workflow/tools/mcp/_response_reminder.py` (NEW)
  - `serial_reminder(fn)` decorator
  - Honors `MCP_SERIAL_BYPASS=1` and the `mcp_serialization_ttl.json` sunset
  - Type-aware: handles `str`, `dict`, FastMCP `TextContent`, JSON-serializable
- `@c:/Git/Agentic-Workflow/tests/unit/tools/mcp/test_response_reminder.py` (NEW; ~10 tests)
  - Each return type wrapped correctly
  - Bypass env var skips wrapping
  - Sunset TTL skips wrapping
  - Decorator preserves signature for FastMCP introspection

**Success Criteria**:
1. Each return type passes through with reminder prepended
2. Bypass and sunset both no-op the decorator
3. Decorator does not break FastMCP `@mcp.tool()` introspection (verified via `inspect.signature`)

---

### L3.2 — Apply Decorator to All 12 MCP Servers

**What**: Stack `@serial_reminder` on every `@mcp.tool()` in 12 server files.

**Files** (each: import line + `@serial_reminder` on N tool functions):
- `@c:/Git/Agentic-Workflow/tools/mcp/adg_sqlite_server.py` (13 tools)
- `@c:/Git/Agentic-Workflow/tools/mcp/memory_server.py` (13 tools)
- `@c:/Git/Agentic-Workflow/tools/mcp/vector_db_server.py` (10 tools)
- `@c:/Git/Agentic-Workflow/tools/mcp/redis_server.py` (10 tools)
- `@c:/Git/Agentic-Workflow/tools/otel/otel_mcp_server.py` (9 tools)
- `@c:/Git/Agentic-Workflow/tools/mcp/pytest_mcp_server.py` (5 tools)
- `@c:/Git/Agentic-Workflow/tools/mcp/enhanced_http_server.py` (7 tools)
- `@c:/Git/Agentic-Workflow/tools/mcp/deepwiki_wrapper.py` (3 tools, third-party — wrapper layer only)
- `@c:/Git/Agentic-Workflow/tools/mcp/filesystem_mcp_launcher.js` — N/A (third-party Node; document opt-out in plan)
- `@c:/Git/Agentic-Workflow/tools/mcp/task_manager_wrapper.py` (4 tools, third-party wrapper layer)
- `@c:/Git/Agentic-Workflow/tools/mcp/gitkraken_wrapper.py` (23 tools, third-party wrapper layer)
- `@c:/Git/Agentic-Workflow/tools/mcp/notion_wrapper.py` (8 tools, third-party wrapper layer)

**Pain Point**: Some MCPs are third-party (filesystem, task_manager, gitkraken, notion). For these, decorate the wrapper layer only — never modify upstream code. If no wrapper exists yet, the wrapper creation is a sub-task of L3.2.

**Success Criteria**:
1. Smoke test per MCP: spawn server, call one tool, confirm response begins with `[MCP_SERIAL_REMINDER]`
2. JSON-RPC handshake still <2s on every server (no perf regression)
3. ADG regeneration after decoration produces zero new SC/AP violations

---

### L4.1 — Hang Auto-Recovery Watchdog

**What**: A pre-prompt-time check that reads `artifacts/ledgers/mcp_invocation.sqlite` (per ADR-050 ledger family). If the most recent MCP invocation latency exceeded the rolling p99 × 3 (configurable), the watchdog injects this marker into the next pre-prompt:

```
MCP_HANG_SUSPECTED: previous MCP turn exceeded p99×3 latency for server=<name>. The serialization race may have fired. Verify session state before continuing; if next call hangs, retry as serialized.
```

**Files**:
- `@c:/Git/Agentic-Workflow/.windsurf/scripts/mcp_hang_watchdog.py` (NEW)
  - Reads ledger; computes p99 from the last 50 invocations per server
  - Returns marker text or empty string
- `@c:/Git/Agentic-Workflow/.windsurf/scripts/pre_prompt_classifier.py` — call watchdog, inject marker
- `@c:/Git/Agentic-Workflow/tests/unit/ops_scripts/hooks/windsurf/test_mcp_hang_watchdog.py` (NEW)

**Pain Point**: Requires the `mcp_invocation` ledger to be populated. Per ADR-050 it should be live, but check on-disk before assuming.

**Success Criteria**:
1. Watchdog returns marker when synthetic ledger row shows latency > p99×3
2. Returns empty when latencies are normal
3. Fails open (returns empty) when ledger file is missing or corrupt
4. Marker injected into pre-prompt classifier output

---

### L5.1 — Session-Start Violations Banner

**What**: Extend `pre_user_prompt_hook_health_check.py` to read `artifacts/windsurf/mcp_serialization_violations.jsonl`, count last-24h entries, and emit a banner when count ≥ 1:

```
[MCP_SERIAL_RECENT] N serialization violation(s) recorded in the last 24h.
Review .windsurf/rules/mcp-serialization.md before next MCP call.
Most recent: <timestamp> — <violation_type>
```

**Files**:
- `@c:/Git/Agentic-Workflow/.windsurf/scripts/pre_user_prompt_hook_health_check.py` — add violations counter
- `@c:/Git/Agentic-Workflow/tests/unit/ops_scripts/hooks/windsurf/test_pre_user_prompt_hook_health_check.py` — extend

**Success Criteria**:
1. Banner appears at session start when violations exist
2. Banner suppressed when violations.jsonl missing, empty, or all entries >24h old
3. Banner format ≤5 lines; fits in pre-prompt budget

---

### V1 — Combined Unit + Integration Suite

**Scope**: Run all new test files in one pytest invocation. Add cross-layer integration tests:
1. Pre-prompt with MCP intent → SR_MANDATE injected (L2) AND if violations exist also banner (L5)
2. Tool call → reminder appears (L3) AND watchdog state recorded (L4)
3. TTL flag set → all four layers no-op simultaneously (V2 setup)

**Success Criteria**: ≥95% test pass rate on first run; zero regressions in `test_pre_mcp_gate.py` (245 tests) and `test_serialization_sentinel.py` (18 tests).

---

### V2 — Sunset Proof

**Scope**: Confirm every layer reads `_is_retired()` from the shared sentinel module. Drop a fixture `mcp_serialization_ttl.json` with `retired_after` in the past and rerun the V1 suite. Every layer must observably no-op:
- L1 sentinel: `record_and_check` returns `(False, None)` regardless of siblings
- L2 mandate: not injected
- L3 reminder: not prepended
- L4 watchdog: returns empty
- L5 banner: not emitted

**Success Criteria**: All five layers gated through one `_is_retired()` call. Adding the TTL file flips all behaviors off in <1s without code changes. Documented in the MCP Registry entry's retirement procedure.

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Layer 3 decorator breaks FastMCP introspection on some servers | Per-server smoke test in L3.2; rollback plan per-file |
| Layer 3 perf overhead on hot tools (e.g., `adg_node`) | Reminder prepend is a string op (~12 tokens); benchmark before/after; reject if >5% latency |
| Layer 4 false positives during cold-start (first 50 invocations have no p99) | Watchdog requires ≥50 samples per server before activating |
| Reminder fatigue — Cascade ignores `[MCP_SERIAL_REMINDER]` after seeing it 100×/session | Layer 1 dispatch block remains the deterministic floor; reminders are reinforcement only |
| Adding TTL file unsafely retires layers while race still exists | Operator gate in retirement procedure (Step 1: verify upstream changelog); 7-day soak before file deletion |

---

## Out of Scope

- Modifying upstream MCP server code (filesystem MCP launcher, GitKraken upstream, Notion upstream, task_manager upstream — wrappers only)
- Changing the Layer 1 sentinel module (it is the SSOT for `_is_retired()`)
- Auto-promotion to constitutional §26+ — no new constitutional rule needed; §25 already covers it

---

## Retirement Linkage

When `anthropics/claude-agent-sdk-typescript#41` ships in Windsurf, ALL FIVE layers retire together via the procedure documented in MCP Registry entry `34d27693-f55c-816d-84d7-ccd9a62b78dc` (page: _serialization_sentinel — Layer 1). Steps 3–6 of that procedure expand to cover Layer 2–5 file removal:

- L2: revert `pre_prompt_classifier.py` mandate-injection block
- L3.1+L3.2: delete `tools/mcp/_response_reminder.py`; remove decorator from 12 server files
- L4: delete `mcp_hang_watchdog.py`; revert classifier integration
- L5: revert violations counter from `pre_user_prompt_hook_health_check.py`

All test files from this plan are deleted in the same retirement PR.
