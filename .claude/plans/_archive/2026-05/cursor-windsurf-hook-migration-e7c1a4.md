---
plan_id: cursor-windsurf-hook-migration-e7c1a4
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Cursor — Windsurf hook migration (phased)

**SSOT inventory:** `docs/reports/cursor_windsurf_hook_migration_inventory.md`  
**Machine inventory:** `artifacts/cursor/hook_migration_inventory.json`  
**Notion Plans row:** `36227693-f55c-817a-b261-f1d0e3b88985` (Status=Not Started at creation)  
**Author-Gate:** Already Cursor-native — **do not reopen** unless regression.

---

## Phase closeout (operator)

**W1.4_ACCEPTED_PASS.** Migration phase **complete** through validated Cursor-native hook seams. **Stop point: W1.4.** No further work in this plan unless a **regression** appears.

```text
STATUS: CLOSE_PHASE_PASS
SCOPE: Windsurf-to-Cursor value-added hook migration
STOP_POINT: W1.4
DO_NOT_CONTINUE: Fort Knox, unless opened as a separate targeted plan
```

**Proven (this phase):** Author-Gate ledger/capture; hook harness normalized; `beforeMCPExecution` plan auditor + MCP hygiene; post-agent MCP hygiene + long-command audit; full Windsurf hook tests **726 passed, 1 skipped**; Cursor hook tests **34 passed**; AG gates green; `agentic_core` untouched; pre_write parity **not** falsely claimed.

**Deferred (non-blockers for this closeout):** Fort Knox audit → **separate plan**; pre_write parity → **UNKNOWN**, not migrated; legacy `main()` uncapped stdin on some scripts → optional cleanup; test folder rename windsurf → cursor_scripts → optional; `artifacts/cursor/hook_migration_inventory.json` refresh → optional.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: **CLOSED** — W1.4_ACCEPTED_PASS (migration phase through W1.4; Fort Knox / pre_write / W2+ out of scope here)  
CURRENT_WAVE: _phase closed — reopen only on regression or new plan_  
STOP_POINT: **W1.4**  
LAST_COMPLETED_WAVE: W1.4-post_agent_long_command_afterAgentResponse  
LAST_UPDATED: 2026-05-16  
W0_1_NOTE: (unchanged) See W0.1 section.  
HOOK_TESTS: `pytest tests/unit/ops_scripts/hooks/windsurf/` → **726 passed, 1 skipped** (2026-05-16); `pytest tests/unit/ops_scripts/hooks/cursor/` → **34 passed** (2026-05-16).

---

## Wave Structure

| Wave | Focus | Status | Success Criteria |
|------|-------|--------|------------------|
| W0 | Inventory + classification | ✅ DONE | Deliverables on disk + Notion row |
| W0.1 | Hook test import debt | ✅ DONE | `test_post_cursor_agent_cleanup` collects; cleanup file 29 tests PASS |
| W1 | High-risk Cursor seams (scoped) | ✅ **DONE (closeout W1.4)** | `beforeMCPExecution` chain + AG `afterAgentResponse` chain: MCP hygiene + long-command (`agent_response`) last. **Fort Knox not in this plan.** |
| W2 | Durable capture / receipts | 🔲 TODO | Deferred scope + writeback + ADR capture wired or explicitly deferred with receipt |
| W3 | Wave + plan lifecycle | 🔲 TODO | WAVE_* capture + audit parity; Notion/plan hooks aligned |
| W4 | Read budget / context hygiene | 🔲 TODO | Read/grep budget audits write under `artifacts/cursor/` |
| W5 | Observability / advisory | 🔲 TODO | Heartbeat, token telemetry, post_run/mcp audit wired or CI-only |
| W6 | Retire / legacy compatibility | 🔲 TODO | Windsurf-only hooks documented RETIRE; no accidental `.windsurf/state` writes from Cursor path |
| W7 | Tests + CI closure | ✅ harness done | `pytest tests/unit/ops_scripts/hooks/windsurf/` green (726 passed); production hooks unchanged |

---

## W0 — Inventory and classification

**Objective:** Baseline Windsurf vs Cursor; no behavior change.

**Files likely touched:**  
`docs/reports/cursor_windsurf_hook_migration_inventory.md`, `artifacts/cursor/hook_migration_inventory.json`, `.cursor/plans/cursor-windsurf-hook-migration-e7c1a4.md`

**Commands:**
```bash
python ops_scripts/ci/check_ag_hook_wiring.py
python tools/cursor/verify_cursor_author_gate_wiring.py
python -m pytest tests/unit/ops_scripts/ci/test_check_ag_hook_wiring.py -q -o addopts=
python -m pytest tests/unit/ops_scripts/hooks/windsurf/ -q -o addopts=
```

**Tests/gates:** `check_ag_hook_wiring`; Author-Gate verify script; pytest subset above.

**Rollback:** Delete report artifacts / revert plan file.

**PASS:** All three outputs exist; verification commands run with evidence; UNKNOWN items explicitly listed.  
**PARTIAL:** Report exists but some commands skipped or failing pre-existing tests (document).  
**FAIL:** Missing deliverables.

---

## W0.1 — `post_cursor_agent_cleanup` import / patch debt

**Root cause:** Test inserted `repo/.windsurf/scripts` on `sys.path`, but `post_cursor_agent_cleanup.py` lives only under `.cursor/scripts`. Patches referenced stale names `WINDSURF_DIR` / `SESSION_SUMMARY`; module exposes `windsurf_dir` / `session_summary`.

**Fix (minimal):** `sys.path` → `.cursor/scripts`; patches → `windsurf_dir`, `session_summary`.

**Proof:** `pytest tests/unit/ops_scripts/hooks/windsurf/test_post_cursor_agent_cleanup.py` → **29 passed**.

**Full package follow-up (W7-adjacent, not W0.1):**  
`pytest tests/unit/ops_scripts/hooks/windsurf/ -q -o addopts=` → **602 passed, 124 failed, 1 skipped** (2026-05-16). Dominant classes:
- Subprocess tests invoke scripts under `.windsurf/scripts/*.py` that **no longer exist** (errno 2) — **stale test paths / Cursor migration gap**.
- `post_mcp_audit` tests patch `AUDIT_LOG` on module loaded from **`.windsurf/scripts`** — **stale test vs `.cursor` implementation drift**.
- Similar path/API skew for `post_run_audit`, `post_write_audit`, `pre_prompt_classifier`, `task_manager_lifecycle`.

**W0.1 acceptance:** Collection/import unblock for cleanup tests **met**. Full-package green = **W7** scope.

---

## W1 design — high-risk hooks only (no implementation in this pass)

| Capability | Windsurf event | Cursor 1:1? | Nearest substitute | Pre vs post | Notes |
|------------|----------------|---------------|---------------------|-------------|-------|
| pre_write_gate | `pre_write_code` (stdin: file_path + edits; exit 2 block) | **No** in `.cursor/hooks.json` | (A) future native pre-edit hook if Cursor exposes; (B) `afterFileEdit` audit (post-hoc); (C) CI on diff; (D) rules-only | Ideal **pre**; pragmatic **post** + CI | **HIGH** risk if post-only: file already written. PASS requires documented contract + reason codes. **NOT_APPLICABLE** for strict pre-block if no edit stdin — must state reason. **UNKNOWN** Cursor pre-write availability ≠ PASS. |
| pre_mcp_gate + plan auditor pre-flight | `pre_mcp_tool_use` | **`beforeMCPExecution`** | **DONE (W1.1):** `before_mcp_execution.py` → `pre_mcp_gate.py` → subprocess `unified_plan_creation_auditor.py mcp_before` (ordered). No extra `hooks.json` entry. | **Pre** (MCP wrapper) | Post-flight JSONL under `artifacts/cursor/` remains **append-only** (replays duplicate lines — same as W2.P1). **Pre-stage adds no durable writes.** `API-patch-page` → NOT_APPLICABLE (defer). Missing/malformed `tool_input` on applicable POST → **BLOCK** with `[PLAN_AUDITOR_BLOCK]`. |
| pre_author_gate | `pre_write_code` | **No** | **Accepted:** `after_agent_author_gate_audits` + `.cursor` ledger (do not weaken). Optional future pre-edit if Cursor adds parity | Current: **post** capture + prompt reminders | Post-only gap vs Windsurf pre-write block — mitigated by miss detectors + violations. |
| pre_ask_user_question_gate | `pre_user_prompt` | Partial | **`beforeSubmitPrompt`** hook (unwired today for this script) | **Pre** prompt send | Must verify Cursor honors exit 2 / stderr for this event; else document **NOT_APPLICABLE** with reason. |

**Cross-cutting:** Any durable write = backup/idempotency/replay + reason codes. Any blocking hook = visible stderr/JSON. **UNKNOWN** ≠ **PASS**.

---

## W1 — High-risk safety / governance

### W1.1 — `beforeMCPExecution` chain (`pre_mcp_gate` → unified plan auditor) — **DONE (2026-05-16)**

**Objective:** After `pre_mcp_gate` allows an MCP call, run **`unified_plan_creation_auditor.py mcp_before`** on the same normalized payload subset Cursor provides (`tool_input`, `tool_info`, `command`).

**Production files:** `.cursor/hooks/before_mcp_execution.py`, `.cursor/hooks/lib/cursor_hook_common.py` (MCP stdin helpers), `.cursor/scripts/unified_plan_creation_auditor.py` (`run_mcp_plan_auditor_stage`, `mcp_before` CLI).

**Tests:** `tests/unit/ops_scripts/hooks/cursor/test_before_mcp_plan_auditor_chain.py`

**Behavior (short):**

| MCP call | Auditor |
|----------|---------|
| Not `notion` server | `NOT_APPLICABLE` (stderr), allow |
| `notion` but not `API-post-page` (after stripping `mcpN_`) | `NOT_APPLICABLE`, allow |
| `API-post-page` but parent not Plans DB / data source | `NOT_APPLICABLE`, allow |
| `API-patch-page` | `NOT_APPLICABLE` (`notion_plan_patch_deferred_w1`), allow |
| Applicable POST + malformed / missing `tool_input` | **BLOCK** exit 2, `[PLAN_AUDITOR_BLOCK] code=...` |
| Applicable POST + invalid plan properties | **BLOCK** exit 2, `[PLAN_CREATION_BLOCK] ...` |

**Idempotency:** Pre-flight stage performs **no** append to `*.jsonl`. Post-flight correction/alert logs remain **append-only** (duplicate lines possible on replay).

**Open risk:** If a future Cursor build omits `tool_input` on `beforeMCPExecution`, applicable Notion `API-post-page` calls **block** until payload is fixed or `NOTION_PLAN_CREATION_GATE_BYPASS=1` (logged). Server identity uses `tool_info.mcp_server_name` or `command` when it matches an `mcp.json` key.

**Explicit non-goals (this wave):** No `pre_write` parity; no `agentic_core` edits; Author-Gate wiring unchanged.

---

### W1.2 — `mcp_before_hygiene` on `beforeMCPExecution` — **DONE (2026-05-16)**

**Objective:** After the plan auditor, run **payload-only** MCP hygiene on the normalized hook payload (no new policy engine).

**Production files:** `.cursor/hooks/lib/mcp_before_hygiene.py`, `.cursor/hooks/before_mcp_execution.py` (stage ordering).

**Tests:** `tests/unit/ops_scripts/hooks/cursor/test_mcp_before_hygiene.py`

**Checks:**

| Condition | Result |
|-----------|--------|
| `MCP_BEFORE_HYGIENE_BYPASS=1` | `NOT_APPLICABLE`, allow |
| No `tool_input` key | `NOT_APPLICABLE`, allow |
| `tool_input` string > 512 KiB (UTF-8) | **BLOCK** `[MCP_HYGIENE_BLOCK] code=TOOL_INPUT_OVERSIZED` |
| Non-empty JSON string but invalid JSON | **BLOCK** `code=TOOL_INPUT_JSON_INVALID` |
| `tool_input` not `str`/`dict` | **BLOCK** `code=TOOL_INPUT_TYPE` |
| Legacy tokens inside serialized `tool_input` (same set as top-level hook guard) | **BLOCK** `code=LEGACY_SURFACE_IN_TOOL_INPUT` |
| Else | `APPLICABLE ALLOW` |

**Durable artifact:** Append-only `artifacts/cursor/mcp_before_hygiene.jsonl` (replays append duplicate rows). No `.windsurf` paths.

**DEFERRED (not this seam):** `preflight` subcommand remains a stub for manual CLI; **`orphan_reap` not invoked** from `run_all` or post-agent path (W1.3); `post_cursor_agent_fortknox_integrity_audit.py` remains prose-oriented — none forced into `beforeMCPExecution`. **W1.4** covers `post_cursor_agent_long_command_audit.py` on `afterAgentResponse` (see below).

---

### W1.3 — Post-agent MCP hygiene (`agent_response`) — **DONE (2026-05-16)**

**Seam:** Cursor **`afterAgentResponse`**, via **existing** `after_agent_author_gate_audits.py` chain (last step), so Author-Gate scripts still run first on the same stdin payload.

**Invocation:** `python .cursor/scripts/post_cursor_agent_mcp_hygiene_audit.py agent_response` (extra argv wired in `after_agent_author_gate_audits.py`).

**Input:** Same JSON/text stdin as other `post_cursor_agent_*` hooks (agent response envelope). Extracts text via `_extract_agent_response_text` (response / text / content / nested keys).

**Behavior (advisory — always exit 0):**

| Case | Stderr / log |
|------|----------------|
| bypass env | `NOT_APPLICABLE` |
| TTY / empty stdin | `NOT_APPLICABLE` |
| No MCP surface in text | `NOT_APPLICABLE` + `mcp_post_agent_hygiene.jsonl` row |
| MCP surface + serialization dup (legacy `notion_` / `tavily_` / … count > 1) | `[MCP_HYGIENE_VIOLATION] code=SERIALIZATION_REMOTE_DUP` + `mcp_serialization_violations.jsonl` |
| MCP surface + clean | `APPLICABLE outcome=ALLOW` |

**Artifacts (Cursor-native):** `artifacts/cursor/mcp_post_agent_hygiene.jsonl`, `artifacts/cursor/mcp_serialization_violations.jsonl`. **No** new writes under `artifacts/windsurf` from this script path.

**Safety:** `run_all` runs **preflight only**; **`orphan_reap` is explicit subcommand only** (not called from post-agent audit).

**Tests:** `tests/unit/ops_scripts/hooks/cursor/test_post_agent_mcp_hygiene_audit.py`

**`.cursor/hooks.json`:** Unchanged — hygiene is chained, not a duplicate `afterAgentResponse` entry (avoids double-consuming stdin).

---

### W1.4 — Post-agent long-command (`agent_response`) — **DONE (2026-05-16)**

**Seam:** Cursor **`afterAgentResponse`**, via **`after_agent_author_gate_audits.py`** — **last** step after MCP hygiene, same stdin payload as W1.3.

**Invocation:** `python .cursor/scripts/post_cursor_agent_long_command_audit.py agent_response` (extra argv in `_SCRIPT_EXTRA_ARGS`).

**Input:** Same JSON/text stdin as other post-agent hooks; `_extract_agent_response_text` aligns with W1.3 (top-level + `tool_info` + nested `result`/`data`/`body`).

**Behavior (advisory — always exit 0; does not block run_command):**

| Case | Stderr / logs |
|------|----------------|
| bypass / TTY / empty stdin / no extracted text | `[LONG_CMD_POST] NOT_APPLICABLE …` + optional `long_command_post_agent_audit.jsonl` |
| No `<invoke name="run_command">` in extracted text | `NOT_APPLICABLE reason=no_run_command_surface` |
| `run_command` present + long pattern without timeout | `[LONG_CMD_VIOLATION] code=LONG_COMMAND_NO_TIMEOUT … (advisory — does not block already-emitted run_command)` + `artifacts/cursor/long_command_violations.jsonl` |
| `run_command` present + all clear | `[LONG_CMD_POST] APPLICABLE outcome=ALLOW …` |

**Artifacts (Cursor-native):** `artifacts/cursor/long_command_violations.jsonl`, `artifacts/cursor/long_command_post_agent_audit.jsonl`. **No** `artifacts/windsurf` writes from this script.

**Legacy:** No subcommand → stdin contract preserved for `post_cursor_agent_dispatch.py` shadow mode; violations log path is **`artifacts/cursor/`** only.

**Tests:** `tests/unit/ops_scripts/hooks/cursor/test_post_agent_long_command_audit.py`

---

**Objective:** Restore **MCP + certification + long-command** governance on Cursor paths comparable to Windsurf.

**Files likely touched:**  
`.cursor/hooks.json`, `.cursor/hooks/before_mcp_execution.py`, `.cursor/scripts/pre_mcp_gate.py`, `post_cursor_agent_mcp_hygiene_audit.py`, `post_cursor_agent_long_command_audit.py`, `post_cursor_agent_fortknox_integrity_audit.py`, thin orchestrators under `.cursor/hooks/`

**Commands:**
```bash
python ops_scripts/ci/check_ag_hook_wiring.py
python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_pre_mcp_gate.py -q -o addopts= 2>/dev/null || true
python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py -q -o addopts=
```

**Tests/gates:** pre_mcp deep tests; MCP hygiene unit tests if present.

**Rollback:** Revert hooks.json; feature flag env to disable new chain.

**PASS:** New hooks documented; blocking hooks show visible reason codes; no `agentic_core` edits.  
**PARTIAL:** Design-only doc merged; no default-on chain.  
**FAIL:** Bypass env widened or silent failure.

---

## W2 — Durable capture / receipt / ledger

**Objective:** Wire **deferred scope**, **writeback audit**, **ADR capture** to `afterAgentResponse` or `stop`; outputs under **`artifacts/cursor/`** and **`.cursor/state/`** only.

**Files likely touched:**  
`post_cursor_agent_deferred_scope_capture.py`, `post_cursor_agent_writeback_audit.py`, `post_cursor_agent_adr_registry_capture.py`, `.cursor/hooks/*`

**Commands:**
```bash
python tools/cursor/verify_cursor_author_gate_wiring.py
python ops_scripts/ci/check_decision_ledger_sqlite_freshness.py
```

**Tests/gates:** Existing post_cursor_agent capture tests; ledger freshness advisory.

**Rollback:** Remove hook entries; artifacts append-only — no delete required.

**PASS:** At least one durable marker path verified in smoke; Windsurf sqlite not written by Cursor hooks.  
**PARTIAL:** Wired but manual invoke only.  
**FAIL:** Duplicate conflicting writers to same ledger without idempotency.

---

## W3 — Wave lifecycle / plan freshness

**Objective:** **Wave capture + plan lifecycle suite** parity; add **`post_cursor_agent_wave_lifecycle_audit`** or wrap Windsurf script with cursor artifact paths.

**Files likely touched:**  
`post_cursor_agent_wave_lifecycle_capture.py`, new or wrapped `wave_lifecycle_audit`, `post_cursor_agent_plan_lifecycle_audit.py`, plan hook utilities

**Commands:**
```bash
python ops_scripts/ci/check_wave_marker_emission.py
python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_post_cursor_agent_plan_evidence_gate.py -q -o addopts=
```

**Tests/gates:** Wave marker CI; plan evidence tests.

**Rollback:** Disable wave chain via env.

**PASS:** WAVE_COMPLETE capture updates plan table in smoke; audit logs under `artifacts/cursor/`.  
**PARTIAL:** Capture only, audit deferred with ticket id in JSON inventory.  
**FAIL:** Plan edits without idempotent marker handling.

---

## W4 — Read budget / context hygiene

**Objective:** Wire **read_budget**, **grep_budget**, **resource_budget** audits; normalize paths to **`artifacts/cursor/`**.

**Files likely touched:**  
`post_cursor_agent_read_budget_audit.py`, `post_cursor_agent_grep_budget_audit.py`, `post_cursor_agent_resource_budget_audit.py`

**Commands:**
```bash
python -m pytest tests/unit/ops_scripts/hooks/windsurf/ -k read_budget -q -o addopts=
```

**Tests/gates:** Budget-related tests; grep budget gate if any.

**Rollback:** Remove from afterAgent chain.

**PASS:** Violations jsonl under cursor namespace; no duplicate windsurf paths in new writes.  
**PARTIAL:** Advisory-only mode.  
**FAIL:** Blocking without visible reason.

---

## W5 — Observability and advisory reports

**Objective:** **Heartbeat**, **token telemetry**, **post_run_audit**, **post_mcp_audit** — schedule on `stop` or end-of-response batch to limit latency.

**Files likely touched:**  
`post_cursor_agent_heartbeat.py`, `post_cursor_agent_token_telemetry.py`, `post_run_audit.py`, `post_mcp_audit.py`, `.cursor/hooks/stop_task_audit.py`

**Commands:**
```bash
python ops_scripts/ci/hook_latency_calibration.py
```

**Tests/gates:** If latency gate exists; otherwise manual 10-turn latency sampling doc.

**Rollback:** Feature flag off.

**PASS:** Observable receipts; P95 latency documented.  
**PARTIAL:** CI-only execution.  
**FAIL:** Unbounded subprocess fan-out per turn.

---

## W6 — Cleanup / retire / legacy compatibility

**Objective:** Mark **RETIRE** for Cascade-only dispatch; document **KEEP_LEGACY** for `.windsurf/**`; ensure CI does not **require** Windsurf paths for Cursor-only dev.

**Files likely touched:**  
`ops_scripts/ci/*`, `.cursor/windsurf_compat/*`, docs

**Commands:**
```bash
python ops_scripts/ci/check_mcp_editor_parity.py
python ops_scripts/ci/check_windsurf_config_schema.py
```

**Tests/gates:** Editor parity; Windsurf schema (compat).

**Rollback:** Revert doc-only commits.

**PASS:** Inventory `migration_recommendation` updated; obsolete hooks not wired by mistake.  
**PARTIAL:** Draft retirement list only.

---

## W7 — Tests and CI closure

**Status (2026-05-16):** Harness migration **PASS** — no production hook behavior changed.

### Before / after

| Metric | Before | After |
|--------|--------:|------:|
| `pytest tests/unit/ops_scripts/hooks/windsurf/` | 124 failed, 602 passed | **0 failed, 726 passed**, 1 skipped |

### Failure classification (original 124 — all addressed as test harness drift)

| Category | Count (approx.) | Treatment |
|----------|-----------------|-----------|
| stale_windsurf_script_path | ~55+ | `sys.path` + subprocess `HOOK` → `.cursor/scripts`; subprocess targets that pointed at missing `post_cursor_agent_*` under Windsurf |
| stale_module_api | ~45+ | Patches updated: `AUDIT_LOG`→`audit_log`, `PROCESS_LOG`→`process_log`, `SESSION_STATE`→`session_state`, `REPO_ROOT`→`repo_root` |
| cursor_migration_gap | ~15+ | Tests updated for Cursor SSOT filenames (e.g. `mcp.json` suffix vs `mcp_config.json`), `.cursor/plans`, SSOT folder rules (`runner.py` → dummy under `tests/...`) |
| windsurf_legacy_only | 0 quarantined | `test_enforcement_gaps` still references `.windsurf/hooks.json` existence for Windsurf config parity — intentional read-only check |
| real_regression | 0 | None found in production hooks |
| duplicate_coverage | 0 | n/a |
| quarantine_candidate | 0 | none required |

### Commands (evidence)

```bash
python ops_scripts/ci/check_ag_hook_wiring.py   # PASS
python tools/cursor/verify_cursor_author_gate_wiring.py  # PASS
python -m pytest tests/unit/ops_scripts/ci/test_check_ag_hook_wiring.py -q -o addopts=  # 23 passed
python -m pytest tests/unit/ops_scripts/hooks/windsurf/ -q -o addopts=  # 726 passed, 1 skipped
python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_hooks_deep_edge_cases.py -q -o addopts=  # 130 passed
```

### W1 readiness

**Yes** — hook test harness now tracks **Cursor-native** script paths and module globals; remaining risk is product behavior (e.g. plan evidence gate still references `.windsurf/plans` in production — treat as **cursor_migration_gap** when scoping W1 implementation, not harness).

**Objective (retained):** Keep this package green under CI; optional `run_contract_gates.py` subset when touching hooks.

**Rollback:** Revert test-only commits.

---

## Definition of Done (plan-level)

| # | Criterion |
|---|------------|
| 1 | Inventory markdown + JSON committed paths above |
| 2 | Each wave has objective, files, commands, rollback, PASS criteria |
| 3 | No Author-Gate regression without new evidence |
| 4 | No `agentic_core` edits in this plan’s waves unless separate authorized plan |
| 5 | Cursor-native durable outputs use `.cursor/state` or `artifacts/cursor` |

---

## NEXT_CURSOR_PROMPT

Start **W1 implementation** per §W1 design: extend `before_mcp_execution` with `unified_plan_creation_auditor` pre-flight; evaluate `beforeSubmitPrompt` for `pre_ask_user_question_gate` after confirming Cursor block semantics. Address production **cursor_migration_gap** items (e.g. plan paths in `post_cursor_agent_plan_evidence_gate.py`) only inside W1 scope with receipts. Do **not** weaken **after_agent_author_gate_audits**.
