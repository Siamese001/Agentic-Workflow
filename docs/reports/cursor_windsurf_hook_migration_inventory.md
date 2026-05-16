# Cursor ↔ Windsurf hook harness — migration inventory

**Phase closeout:** Operator **CLOSE_PHASE_PASS** at **W1.4** (2026-05-16). Fort Knox and pre_write parity deferred to separate plans; no further migration scope in `cursor-windsurf-hook-migration-e7c1a4` unless regression.

**Generated:** 2026-05-16  
**Scope:** Inventory and classification only (no migrations in this pass).  
**Exclusions:** `agentic_core`; Author-Gate re-open only on regression (none found).

---

## Executive summary

| Surface | Windsurf | Cursor (repo) | Notes |
|---------|----------|---------------|--------|
| Hook JSON events | Rich `pre_*` / `post_*` / `post_cascade_response` (61+ hook entries in `.windsurf/hooks.json`) | Minimal: `beforeSubmitPrompt`, `afterAgentResponse`, `beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`, `afterFileEdit`, `stop` | **Cursor cannot 1:1 map** Windsurf `pre_write_code` / `post_write_code` / `pre_read_code`; behavior must be **reimplemented** on nearest Cursor event or **delegated** from thin wrappers. |
| Post-agent audits | Full chain under `post_cascade_response` | **Partial:** `after_agent_adg_audits.py`, Notion audit, **`after_agent_author_gate_audits.py`** (AG suite + **W1.3** MCP hygiene + **W1.4** long–command audit last) | Remaining gap: plan lifecycle, wave lifecycle, deferred scope, writeback, resource budget, Fort Knox (correct seam), etc. |
| Pre-prompt | Long `pre_user_prompt` chain | `before_submit_prompt.py` + grep warning (subprocess) + `pre_user_prompt_author_gate_reminder.py` | **Missing:** classifier, deferred-scope recovery, hook health, ledger staleness check, plan registration/dup surfaces, `pre_ask_user_question_gate`, AG queue surface, weekly report, etc. |
| Pre-write / pre-run | Blocking gates on write/run | **No Cursor hook equivalent** for `pre_write_gate`, `pre_author_gate`, Fort Knox, plan scope — *scripts exist under `.cursor/scripts` for several* but **not invoked** from `.cursor/hooks.json` | **HIGH risk** for governance parity. |
| Rules | 55× `.md` under `.windsurf/rules` | 61× `.mdc` under `.cursor/rules` | Largely **duplicated doctrine**; maintenance is **MERGE/documentation** (single SSOT story), not porting hooks. |
| Skills | 34 `SKILL.md` under `.windsurf/skills` | 34 under `.cursor/skills` | **Parity** by count; paths differ — **KEEP_LEGACY** `.windsurf` for Windsurf IDE only. |
| Workflows | 25 under `.windsurf/workflows` | 25 under `.cursor/workflows` | `refresh-windsurf-docs` → `refresh-cursor-docs` already forked; rest largely mirrored. |
| State | `.windsurf/state/**` (markers, session, refactor_decisions copy) | `.cursor/state/**` | Author-Gate ledger **SSOT = `.cursor/state/refactor_decisions`**; Windsurf ledger **KEEP_LEGACY** / optional mirror only. |

---

## Verification (this inventory)

| Command | Result |
|---------|--------|
| `python ops_scripts/ci/check_ag_hook_wiring.py` | PASS — `AG_HOOK_WIRING: all invariants satisfied (AG-WIRE-1 through AG-WIRE-4)` |
| `python tools/cursor/verify_cursor_author_gate_wiring.py` | PASS — `[verify] PASS: lookup path, capture path, lookup run, prepare_ask, marker capture` |
| `python -m pytest tests/unit/ops_scripts/ci/test_check_ag_hook_wiring.py -q -o addopts=` | **23 passed** |
| `python -m pytest tests/unit/ops_scripts/hooks/windsurf/ -q -o addopts=` | **726 passed, 1 skipped** (2026-05-16) — harness normalized to `.cursor/scripts` + current module APIs |
| `python -m pytest tests/unit/ops_scripts/hooks/windsurf/test_post_cursor_agent_cleanup.py -q -o addopts=` | **29 passed** |
| `python -m pytest tests/unit/ops_scripts/ci/test_check_windsurf_config_schema.py tests/unit/ops_scripts/hooks/windsurf/test_enforcement_gaps.py -q -o addopts=` | **54 passed** (targeted hook-adjacent subset) |
| `python -m pytest tests/unit/ops_scripts/hooks/cursor/ -q -o addopts=` | **34 passed** (2026-05-16) — W1.1–W1.4 Cursor hook chain |

Machine-readable rows: **`artifacts/cursor/hook_migration_inventory.json`**.  
Phased execution: **`.cursor/plans/cursor-windsurf-hook-migration-e7c1a4.md`** (same content as requested wave plan).

---

## Event-model gap (Windsurf → Cursor)

| Windsurf stage | Approximate Cursor mapping | Coverage today |
|----------------|---------------------------|--------------|
| `pre_read_code` | **None** (`beforeReadFile` is read-only warn, not ADG read gate) | **Gap** |
| `pre_run_command` | `beforeShellExecution` + manual CI | **Partial** (receipt guard / `pre_run_gate` not in Cursor hooks) |
| `pre_write_code` | **None** (closest: policy in rules; `afterFileEdit` is post-hoc) | **Major gap** |
| `pre_mcp_tool_use` | `beforeMCPExecution` | **Improved (W1.1–W1.2)** — `pre_mcp_gate` → plan auditor → **`mcp_before_hygiene`** (`tool_input` bound + legacy scan + JSON sanity); post-agent hygiene/Fort Knox/long-command scripts **not** ported to this event (see plan DEFERRED) |
| `pre_user_prompt` | `beforeSubmitPrompt` | **Sparse** |
| `post_write_code` | `afterFileEdit` | **Partial** (only if thin hook chains write-audit scripts) |
| `post_run_command` / `post_mcp_tool_use` | **None** in `.cursor/hooks.json` | **Gap** |
| `post_cascade_response` | `afterAgentResponse` | **Sparse** (3 chains vs 25+ Windsurf) |

---

## Migration matrix (hook-wired capabilities)

Columns match `artifacts/cursor/hook_migration_inventory.json`.  
**Author-Gate / AG consolidated audit:** treat as **DONE** in Cursor (`after_agent_author_gate_audits.py`); Windsurf `post_cascade_author_gate_audit` → **KEEP_LEGACY** for Cascade only.

### Pre / write / run (Windsurf-primary)

| name | source | trigger | Cursor equivalent | valuable? | rec | risk | complexity |
|------|--------|---------|-------------------|-----------|-----|------|------------|
| pre_read_gate | `.windsurf/scripts/pre_read_gate.py` | pre_read_code | **NONE wired** | yes | MIGRATE | HIGH | M |
| receipt_required_guard | `tools/governance/receipt_required_guard.py` | pre_run_command | **NONE** in Cursor hooks | yes | REIMPLEMENT | HIGH | S |
| pre_run_gate | `.windsurf/scripts/pre_run_gate.py` | pre_run_command | `.cursor/scripts/pre_run_gate.py` exists; **not in hooks** | yes | MIGRATE | HIGH | S |
| core_write_guard | `tools/governance/core_write_guard.py` | pre_write_code | **NONE** | yes | REIMPLEMENT | HIGH | S |
| pre_author_gate | `.windsurf/scripts/pre_author_gate.py` | pre_write_code | `.cursor/scripts/pre_author_gate.py` — **NOT in Cursor hooks** | yes | MIGRATE | HIGH | M |
| pre_write_gate | `.windsurf/scripts/pre_write_gate.py` | pre_write_code | `.cursor/scripts/pre_write_gate.py` **unwired** | yes | MIGRATE | HIGH | M |
| pre_write_plan_scope_gate | `.windsurf/scripts/pre_write_plan_scope_gate.py` | pre_write_code | check **parity** with `.cursor/scripts` | yes | MIGRATE | MEDIUM | M |
| pre_write_fortknox_guard | `.windsurf/scripts/pre_write_fortknox_guard.py` | pre_write_code | `.cursor/scripts/pre_write_fortknox_guard.py` **unwired** | yes | MIGRATE | MEDIUM | S |
| unified_plan_creation_auditor pre_flight | `.windsurf/scripts/unified_plan_creation_auditor.py` | pre_mcp | `.cursor/scripts/unified_plan_creation_auditor.py` | yes | MERGE | HIGH | M |
| pre_mcp_gate | `.windsurf/scripts/pre_mcp_gate.py` | pre_mcp | `.cursor/scripts/pre_mcp_gate.py` / `before_mcp_execution` pattern | yes | MIGRATE | HIGH | M |

### pre_user_prompt chain (subset)

| name | source | trigger | Cursor equivalent | valuable? | rec | risk | complexity |
|------|--------|---------|-------------------|-----------|-----|------|------------|
| pre_prompt_classifier | `.windsurf/scripts/pre_prompt_classifier.py` | pre_user_prompt | **NONE** | yes | REIMPLEMENT | MEDIUM | L |
| pre_user_prompt_reminder_check | `.windsurf/scripts/pre_user_prompt_reminder_check.py` | pre_user_prompt | `.cursor/scripts/pre_user_prompt_reminder_check.py` **unwired** | maybe | DEFER | LOW | S |
| deferred_scope_recovery | `.windsurf/scripts/pre_user_prompt_deferred_scope_recovery.py` | pre_user_prompt | `.cursor/scripts/...` may exist — verify | yes | MIGRATE | MEDIUM | M |
| hook_health_check | `.windsurf/scripts/pre_user_prompt_hook_health_check.py` | pre_user_prompt | `.cursor/scripts/pre_user_prompt_hook_health_check.py` | yes | MIGRATE | MEDIUM | S |
| ledger_staleness_check | `tools/capture/ledger_staleness_check.py` | pre_user_prompt | **advisory** | yes | MIGRATE | MEDIUM | S |
| grep_for_deps_warning | `.windsurf/scripts/pre_user_prompt_grep_for_deps_warning.py` | pre_user_prompt | invoked from **`before_submit_prompt`** | yes | **DONE** | LOW | S |
| weekly_report | `.windsurf/scripts/pre_user_prompt_weekly_report.py` | pre_user_prompt | **NONE** | optional | DEFER | LOW | S |
| author_gate_reminder | `.windsurf/scripts/...` | pre_user_prompt | **`beforeSubmitPrompt`** second hook | yes | **DONE** | LOW | S |
| ag_queue_surface | `.windsurf/scripts/pre_user_prompt_ag_queue_surface.py` | pre_user_prompt | **NONE** | maybe | DEFER | LOW | S |
| deferred_plan_gate | `.windsurf/scripts/pre_user_prompt_deferred_plan_gate.py` | pre_user_prompt | `.cursor/scripts/...` exists | yes | MIGRATE | MEDIUM | M |
| plan_registration_surface / refresh | `.windsurf/scripts/pre_user_prompt_plan_registration_*.py` | pre_user_prompt | scripts in `.cursor/scripts` | yes | MIGRATE | MEDIUM | M |
| plans_dup_surface | `.windsurf/scripts/pre_user_prompt_plans_dup_surface.py` | pre_user_prompt | **NONE wired** | yes | MIGRATE | MEDIUM | M |
| pre_ask_user_question_gate | `.windsurf/scripts/pre_ask_user_question_gate.py` | pre_user_prompt | `.cursor/scripts/pre_ask_user_question_gate.py` **unwired** | yes | MIGRATE | HIGH | M |

### post_write / post_command

| name | source | trigger | Cursor equivalent | valuable? | rec | risk | complexity |
|------|--------|---------|-------------------|-----------|-----|------|------------|
| post_write_audit | `.windsurf/scripts/post_write_audit.py` | post_write_code | `.cursor/scripts/post_write_audit.py` — wire to `afterFileEdit`? | yes | REIMPLEMENT | MEDIUM | M |
| core_leakage_scan | `tools/governance/core_leakage_scan.py` | post_write | **NONE** | yes | DEFER / CI | MEDIUM | S |
| post_write_mcp_config_sync | `.windsurf/scripts/post_write_mcp_config_sync.py` | post_write | `.cursor/scripts/post_write_mcp_config_sync.py` | yes | MIGRATE | MEDIUM | S |
| post_write_plan_reconcile | `.windsurf/scripts/post_write_plan_reconcile.py` | post_write | check `.cursor` twin | yes | MIGRATE | MEDIUM | M |
| post_write_cert_stage | `.windsurf/scripts/post_write_cert_stage.py` | post_write | verify existence | maybe | DEFER | LOW | M |
| post_run_audit | `.windsurf/scripts/post_run_audit.py` | post_run_command | `.cursor/scripts/post_run_audit.py` **unwired** | yes | MIGRATE | MEDIUM | M |
| post_mcp_audit | `.windsurf/scripts/post_mcp_audit.py` | post_mcp | `.cursor/scripts/post_mcp_audit.py` **unwired** | yes | MIGRATE | MEDIUM | M |

### post_cascade_response (Windsurf) vs post_cursor_agent_* (exists, mostly unwired)

For each script below: **twin** in `.cursor/scripts/post_cursor_agent_<name>.py` unless noted. **Recommendation:** extend `after_agent_author_gate_audits`-style **batched chains** (or `stop` hook) to avoid 30 sequential subprocesses.

| Windsurf script | Valuable in Cursor? | Notes |
|-----------------|---------------------|--------|
| post_cascade_heartbeat | yes | observability → **MIGRATE** (artifacts/cursor) |
| app_runtime_package_scan | yes | governance → **CI or beforeShell** |
| post_cascade_cleanup | yes | **MIGRATE** (stop or end of response) |
| post_cascade_author_gate_audit suite | **DONE** | replaced by `after_agent_author_gate_audits.py` |
| post_cascade_adg_audit | yes | **PARTIAL** — `after_agent_adg_audit` exists |
| post_cascade_resource_budget_audit (grep/read/token) | yes | twins exist; **unwired** |
| post_cascade_read_budget_audit | yes | **MIGRATE** W4 |
| post_cascade_token_telemetry | yes | **MIGRATE** W5 |
| post_cascade_scope_drift_detector | yes | **MIGRATE** W3 |
| post_cascade_writeback_audit | yes | **MIGRATE** W2 |
| post_cascade_deferred_scope_capture | yes | durable capture → **MIGRATE** W2 |
| post_cascade_next_step_capture / miss_detector | yes | **MIGRATE** W3 |
| post_cascade_adr_registry_capture | yes | **MIGRATE** W2 |
| post_cascade_mcp_hygiene_audit suite | yes | **PARTIAL** — W1.3: `post_cursor_agent_mcp_hygiene_audit.py agent_response` wired last in **`after_agent_author_gate_audits`**; serialization advisory + Cursor `artifacts/cursor/*.jsonl`; **orphan reap not auto** from `run_all` / post-agent |
| post_cascade_mcp_preflight_audit | yes | **MIGRATE** W1 |
| post_cascade_long_command_audit | yes | **MIGRATE** W1 |
| post_cascade_plan_lifecycle_audit (suite) | yes | **LARGE** — **MIGRATE** W3 |
| post_cascade_fortknox_integrity_audit | yes | **MIGRATE** W1 |
| unified_notion_status_auditor | yes | **PARTIAL** — `after_agent_notion_status_audit` |
| unified_plan_creation_auditor post_flight | yes | **MERGE** with MCP/post hooks |
| post_cascade_plans_dup_audit | yes | **MIGRATE** W3 |
| post_cascade_wave_lifecycle_capture | yes | twin exists; **unwired** |
| post_cascade_wave_lifecycle_audit | yes | **NO `post_cursor_agent_wave_lifecycle_audit.py`** — **REIMPLEMENT or wrap** Windsurf script with cursor paths |
| post_cascade_plan_scope_audit / plan_complete / wave_completion | yes | twins **post_cursor_agent_*** exist; **unwired** |
| post_setup_worktree | maybe | **DEFER** (setup-only) |

---

## Rules / skills / workflows

- **Rules:** Prefer **`.cursor/rules/*.mdc`** as SSOT for Cursor; `.windsurf/rules/*.md` = **KEEP_LEGACY** for Windsurf. **MERGE** only when drift is detected (diff audits).  
- **Skills / workflows:** Same logical content; **RETIRE** nothing without comparing file hashes; **windsurf-only** naming (`refresh-windsurf-docs`) already forked in Cursor.

---

## CI / tests

- **Hook / parity:** `ops_scripts/ci/check_ag_hook_wiring.py`, `check_hook_consolidation.py`, `check_windsurf_config_schema.py`, `check_mcp_editor_parity.py`, contract gates in `run_contract_gates.py`.  
- **Tests:** `tests/unit/ops_scripts/hooks/windsurf/*`, `test_check_ag_hook_wiring.py`, Author-Gate / wave / plan tests — use as **regression** when wiring expands.

---

## TOP migration candidates (priority)

1. **`pre_write_*` + `pre_author_gate` + `core_write_guard` → Cursor pre-write story** — **HIGH**, **LARGE** (no native hook; needs design: `beforeFileEdit` extension or `preToolUse`-style if Cursor adds it).  
2. **`post_cascade_plan_lifecycle_audit` / wave / plan markers** → wire **`post_cursor_agent_*`** + implement **wave_lifecycle_audit** twin — **HIGH**, **LARGE**.  
3. **`pre_mcp_gate` + plan auditor + pre-MCP hygiene** on **`beforeMCPExecution`** — **W1.1–W1.2 done**; **W1.3:** post-agent **`post_cursor_agent_mcp_hygiene_audit agent_response`** on **`afterAgentResponse`** (AG chain). Remaining: long-command / Fort Knox on correct seams, `post_mcp_audit` wiring.  
4. **Resource budget suite** (read/grep/token) — **MEDIUM**, **MEDIUM**.  
5. **`post_write_audit` / `post_run_audit` / `post_mcp_audit`** — **MEDIUM**, **SMALL–MEDIUM**.

## DEFER / RETIRE

- **Windsurf-only UI noise:** `post_cascade_dispatch` if Cascade-specific — **RETIRE** in Cursor.  
- **Duplicate calibration report hooks:** run on schedule / CI, not every prompt — **DEFER**.  
- **`post_setup_worktree`:** manual / one-shot — **DEFER**.

## OPEN RISKS

- **UNKNOWN** parity between `pre_write_gate` and Cursor `afterFileEdit`-only enforcement → **never treat as PASS** until bounded writes are gated.  
- **Batching:** naive port of 25+ subprocess hooks → latency; use **consolidated chains** + `AG_SUITE_BYPASS` patterns.

---

## W1.3 notes (2026-05-16)

- **Seam:** `afterAgentResponse` → `after_agent_author_gate_audits.py` runs MCP hygiene **after** all Author-Gate scripts on the **same** stdin payload.
- **Subcommand:** `agent_response` only from the chain (extra argv in `_SCRIPT_EXTRA_ARGS`); advisory only (exit 0 always).
- **Logs:** `artifacts/cursor/mcp_post_agent_hygiene.jsonl`, `artifacts/cursor/mcp_serialization_violations.jsonl`.
- **`run_all`:** preflight stub only; `orphan_reap` requires explicit CLI invocation.
- **hooks.json:** No duplicate `afterAgentResponse` row for hygiene (avoid double stdin).

---

## W1.4 notes (2026-05-16)

- **Seam:** Same `after_agent_author_gate_audits.py` chain, **after** MCP hygiene (last step: `post_cursor_agent_long_command_audit.py agent_response`).
- **Input:** Agent response JSON/text (`response` / `text` / `content` / nested `tool_info` / `result` — shared extract pattern as W1.3).
- **NOT_APPLICABLE:** No `<invoke name="run_command">` surface, empty stdin, TTY, bypass (`LONG_COMMAND_AUDIT_BYPASS=1`), or empty extracted text.
- **ALLOW:** `run_command` surface present and no long-running commands without timeout guards.
- **Violations:** `LONG_COMMAND_NO_TIMEOUT` — advisory stderr + `artifacts/cursor/long_command_violations.jsonl`; audit trail `artifacts/cursor/long_command_post_agent_audit.jsonl`.
- **Legacy:** Dispatcher / bare `main()` (no subcommand) uses uncapped stdin read + same detection; logs only under `artifacts/cursor/` (no Windsurf path).

---

## W1.2 notes (2026-05-16)

- **Chain order:** legacy token scan → `pre_mcp_gate` → `unified_plan_creation_auditor mcp_before` → **`run_mcp_before_hygiene_stage`** → allow + receipt.
- **Log:** `artifacts/cursor/mcp_before_hygiene.jsonl` — append-only; replays duplicate rows.
- **Bypass:** `MCP_BEFORE_HYGIENE_BYPASS=1` logs `NOT_APPLICABLE` and allows.
- **Not wired (DEFER):** `post_cursor_agent_fortknox_integrity_audit` on correct prose seam (legacy log path migration TBD). **W1.3–W1.4** now cover MCP hygiene + long-command on `afterAgentResponse` chain.

---

## W1.1 notes (2026-05-16)

- **Ordering:** `before_mcp_execution.py` runs `pre_mcp_gate.py` first; on exit 0, runs `unified_plan_creation_auditor.py mcp_before`; on exit 0, runs **`run_mcp_before_hygiene_stage`** (W1.2).
- **Outputs:** Hook receipts remain under `artifacts/cursor/hooks/`. Plan auditor **pre-flight** adds no new durable log files; **post-flight** JSONL paths are repo-root anchored in `.cursor/scripts/unified_plan_creation_auditor.py`.
- **Not applicable:** Non-Notion MCP calls print `[PLAN_AUDITOR] NOT_APPLICABLE reason=...` and do not validate content.
- **Pre-write parity:** Out of scope for this change (inventory row on `pre_write_code` remains a major gap).

---

> W1 design only: propose the smallest Cursor-native way to restore **pre-write governance** (`pre_author_gate`, `pre_write_gate`, `core_write_guard`) without weakening rules—evaluate `preToolUse`/file-edit events available in project `hooks.json`, document bypass/env parity with Windsurf, and add one **opt-in** chain behind `CURSOR_PRE_WRITE_CHAIN=1` before default-on.
