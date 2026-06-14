> STATUS: COMPLETED — landed on main (commit ac17d564c0, 2026-06-14). Durable decision record: ADR-104.
> Executed as 6 waves (W1–W6, PR #362) plus a W7 follow-up: removed the AUDIT-3 + NP-IDSSOT Notion-ID
> enforcement gates and post_agent_writeback_audit + the memory_recall ledger, while KEEPING the
> load-bearing _notion_constants.py + config/notion_databases.yaml (read by sync_mcp_config /
> check_agents_md_sync / recover_deferred_scope_pendings / agentic_core notion_approval_adapter).
> Retrospective record in the disk-only plans/ SSOT — not Notion (that enforcement was removed by this change).

# Remove windsurf/cursor-era Notion + wave/phase/plan-status enforcement

## Context

This repo accreted a large body of windsurf/cursor-era enforcement machinery around **Notion
updates, Notion status, and "updating SSOT plan phases/waves."** In practice **none of it worked**:
the Notion gates are advisory + token-gated (silently no-op offline), they target several Notion
databases that were archived months ago, and they enforce a marker scheme (`PLAN_CREATED`,
`WAVE_COMPLETE`, `PHASE_COMPLETE`, `PLAN_COMPLETE`, `AUTHORIZATION_DECISION`) that native
`AskUserQuestion`/`spawn_task` already superseded. The operating-model review (145 plans / 0 shipped)
is the symptom.

A sibling session already merged **PR#348 / ADR-100 ("enforcement-surface-consolidation")** to
`origin/main` today, which removed Author-Gate, the S4 deferred-scope/next-step capture pipeline, 18
redirect rule stubs, and dead orphan gates — but it **explicitly KEPT** the Notion-status /
wave-lifecycle / §36 plan-registration cluster as "load-bearing governance." This change **reverses
that keep decision** for the Notion-coupled layer.

**Scope decision (user-approved, Option 1):** remove 100% of the Notion-coupled + wave/phase
plan-status enforcement; **KEEP** the disk-side plan-markdown lint (`check_plan_format_compliance`,
`check_plan_wave_summary_top`, `check_plan_definition_of_done`, `plan-location.md`,
`pre_write_plan_mint_gate`) — it works, never touches Notion, and only validates plan file shape.

**Baseline:** branch `feat/notion-wave-enforcement-removal`, cut from `origin/main` @ `acf506f9f8`
(worktree `C:\Git\.chat-worktrees\feat-notion-wave-enforcement-removal`). All paths/wiring below were
verified against this commit.

## Out of scope (already done on origin/main — do not redo)
Author-Gate teardown, S4 capture removal, redirect-stub deletion, dead orphan CI gates (PR#348/W7).

---

## Removal manifest

### Wave 1 — Unwire the live hooks (stop it firing) — do this FIRST
Surgical edits to **kept** files; delete nothing yet.

- **`.claude/settings.json`** — remove the `PostToolUse` entry calling
  `.claude/governance/scripts/post_write_plan_reconcile.py`.
- **`.claude/governance/scripts/post_agent_dispatch.py`** — drop these from `LEGACY_SCRIPTS`:
  `post_agent_wave_lifecycle_capture.py`, `post_agent_wave_completion_audit.py`,
  `post_agent_plan_registration_capture.py`, `post_agent_plan_supersession_retire.py`,
  `post_agent_writeback_audit.py`. (Keep `post_agent_scope_drift_detector`, `mcp_preflight`,
  `plan_evidence_gate`, `plan_wave_summary_audit`*, `fortknox_integrity`.)
  *`post_agent_plan_wave_summary_audit.py` is disk-side → KEEP, but fix its dead `.cursor/plans` regex
  to `plans/` (it currently never matches).
- **`.claude/hooks/after_agent_governance_dispatch.py`** — remove the `NOTION_AUDITOR`
  (`tools/notion/unified_notion_status_auditor.py`) invocation block + `NOTION_STATUS_VIOLATIONS_VENDOR`
  env line.
- **`.claude/hooks/after_file_edit.py`** — remove the Notion re-sync block
  (`plan_creation_helper.patch_plan_notion_properties`), the `_plan_registration` enqueue, and the
  `wave_execution_state` import. **KEEP** the plan-format validation + `check_plan_wave_summary_top`
  call (disk-side).
- **`.claude/hooks/before_mcp_execution.py`** — remove the `unified_plan_creation_auditor.py`
  dispatch. Keep the `pre_mcp_gate.py` call.
- **`.claude/governance/scripts/pre_mcp_gate.py`** — remove `check_notion_wave_deferral`,
  `check_notion_classification_gate`, `check_notion_gate` (defs + their dispatch + the
  `_wave_execution_state`/`_notion_constants` imports). Keep ADG-SSOT, quote-hazard, pager checks.

**Verify W1:** `python .claude/governance/scripts/post_agent_dispatch.py < /dev/null` and
`before_mcp_execution.py` / `after_file_edit.py` import-and-run clean; `python -m json.tool
.claude/settings.json` passes.

### Wave 2 — Delete the post-agent + pre-flight scripts (now unwired)
Delete from `.claude/governance/scripts/`:
- Live-cluster (just unwired): `post_agent_wave_lifecycle_capture.py`,
  `post_agent_wave_completion_audit.py`, `post_agent_plan_registration_capture.py`,
  `post_agent_plan_supersession_retire.py`, `post_agent_writeback_audit.py`,
  `post_write_plan_reconcile.py`, `plan_driven_closer.py`, `unified_plan_creation_auditor.py`,
  `post_commit_phase_closer.py`.
- Orphans (zero live callers, verified): `post_agent_plan_scope_audit.py`,
  `post_agent_plan_lifecycle_audit.py`, `post_agent_notion_plan_identity_audit.py`,
  `pre_notion_plan_creation_gate.py`, `pre_notion_plan_write_gate.py`,
  `pre_user_prompt_plan_registration_surface.py`, `pre_user_prompt_plan_registration_refresh.py`,
  `pre_user_prompt_deferred_plan_gate.py`, `pre_write_plan_scope_gate.py`, `_plan_lifecycle.py`,
  `_plan_scope_expansion_check.py`, `_plans_dup_detector.py`, `pre_user_prompt_plans_dup_surface.py`.
- Helpers (only cluster importers remain after deletes above): `_notion_canonical.py`,
  `_wave_execution_state.py`, `_plan_supersession.py`, `_plan_registration.py`.
- **`_notion_constants.py` / `_notion_plans_status_check.py`** — deleted **only after** Wave 4
  resolves the two surviving cross-refs (`ops_scripts/ci/check_external_service_literal_ssot.py`,
  `governance_w3_hook_audit_matrix.py`).

### Wave 3 — Delete tools/ Notion + wave-state subsystems
- `tools/notion/`: `unified_notion_status_auditor.py`, `plan_creation_helper.py`,
  `wave_lifecycle_writer.py`, `snapshot_renderer.py`, `sync_decision_ledger.py`, and the ~90 run-by-hand
  Notion-status migration scripts (`plan_notion_sync_*.py`, `repair_notion_*.py`,
  `restore_plan_statuses_*.py`, `backfill_*.py`, `apply_plan_derived_status.py`, `bulk_flip_*.py`,
  `_audit_retired_*.py`). Keep `notion_bearer_token.py` only if a kept caller needs it (else delete).
- `tools/plan_lifecycle/`: `wave_execution_state.py`, `plan_lifecycle_manager.py`.
- `ops_scripts/calibration/plan_registration_weekly_report.py`.
- Representative-pattern delete — enumerate `tools/notion/*.py` and delete the Notion-status/sync set;
  spot-check each isn't imported by a kept module before removing.

### Wave 4 — CI gates: deregister + delete
- **`ops_scripts/ci/run_contract_gates.py`** — remove the registry entries (verified line refs):
  NP1–NP18 set (`check_notion_plans_ai_summary`, `check_notion_plans_status_drift`,
  `check_notion_backlog_plan_linkage`, `check_plan_notion_wave_freshness`,
  `check_notion_plans_no_duplicates`, `check_notion_backlog_no_duplicates`,
  `check_notion_telemetry_log_size`, `check_notion_plan_status_anomalies`,
  `check_notion_plans_new_status`, `check_notion_plans_waiting_for`,
  `check_notion_backlog_waiting_for`, `check_plan_complete_marker_freshness`,
  `check_notion_plan_status_initial`, `check_notion_schema_preflight`, `check_notion_plan_file_drift`,
  `check_notion_decision_parity`, `check_notion_schema_mece`, `check_notion_plans_status_canonical`,
  `check_notion_id_ssot_parity`, `check_plan_done_notion_status`, `check_wave_marker_emission`,
  `check_plan_registration_freshness`), plus `check_notion_plan_lifecycle_guard` (NP-GUARD),
  `check_plan_supersession_consistency` (PLAN-SUPERSEDE). KEEP `check_plan_format_compliance`,
  `check_plan_wave_summary_top`, `check_plan_definition_of_done`.
- Delete those gate files from `ops_scripts/ci/`.
- **`check_plan_freshness.py`** — surgically drop the `MISSING_AUTHORIZATION_DECISION` reason-code (or
  delete if that's its sole purpose — confirm during exec).
- **Cross-refs (surgical, kept files):**
  - `ops_scripts/ci/check_external_service_literal_ssot.py` imports `_notion_plans_status_check` — inline
    the canonical 5-status set as a literal (or drop the Notion-status portion of that gate).
  - `ops_scripts/ci/governance_w3_hook_audit_matrix.py` references the deleted auditors — prune those rows.
- Then `_notion_constants.py` / `_notion_plans_status_check.py` can be deleted (Wave 2 tail).

### Wave 5 — Rules, skills, constitutional, CLAUDE.md (doctrine)
- **Delete rules** (`.claude/rules/`): `notion-plans-taxonomy.md`, `notion-plan-wave-deferral.md`,
  `plan-update-enforcement.md`, `notion-archived-databases.md`, `memory-notion-writeback.md`,
  `plan-lifecycle-procedures.md`, and the already-deprecated stubs `notion-backlog-plan-linkage.md`,
  `notion-plan-identity-verification.md`, `plan-registration-enforcement.md`,
  `wave-completion-discipline.md`.
- **Edit `plan-location.md`** — keep the SSOT-location rule; strip the "Notion registration ordering"
  / Notion-status-discipline sections.
- **`.claude/rules/constitutional.md`** — mark **§36** RETIRED (keep the slot number per the repo's
  stable-numbering convention; body → one-line "retired, native plan mode + disk lint only"); strip the
  §17 Notion-writeback half (keep file-memory recall); drop the NP-series enumerations from §-doctrine
  text. Update the "Extended Doctrine" pointer list.
- **`.claude/rules/work-item-classification.md`** — remove the `PLAN_MULTI_WAVE → Notion Plans DB
  (§36)` routing rows; plans become disk-only.
- **`.claude/rules/apps-rg-execution-bias.md`** — drop the "check Notion `In Progress`" WIP line.
- **Skills** (`.claude/skills/`): delete `plan-governance/` and `notion/`; strip the Notion plan/wave/
  phase status-write content from `writeback-discipline/SKILL.md` and `mcp-integration/sections/07-notion.md`
  (leave generic "how to call the notion MCP" if any consumer wants manual use — enforcement only is removed).
- **`CLAUDE.md`** — remove the "Plans & memory" Notion-registration lines, the rules-index rows for the
  deleted rules, the apps_rg "check Notion In Progress" standing order, and update the MCP-table `notion`
  row to drop the plan/wave/phase-status framing.
- **`AGENTS.md`** — update the Notion Workspace Map / NOTION-MAP table to reflect removal.

### Wave 6 — Tests + dangling-reference sweep
- Delete/adjust tests asserting the removed enforcement, e.g.
  `tests/unit/windsurf_scripts/test_notion_status_ssot_consistency.py`, NP-gate tests, wave-lifecycle
  tests, plan-registration tests (find via `grep -rl` for the deleted module names under `tests/`).
- Final sweep: `grep -rIn` across `.claude/ ops_scripts/ tools/ tests/` for any surviving reference to
  a deleted module, deleted gate, `§36`, `PLAN_CREATED`/`WAVE_COMPLETE`/`PHASE_COMPLETE`/`PLAN_COMPLETE`/
  `AUTHORIZATION_DECISION`, or `NP\d` — resolve each (delete dead ref or update).

---

## Verification (end-to-end)
1. `python -m json.tool .claude/settings.json` — valid.
2. Each kept live hook imports + runs on empty/synthetic stdin without error:
   `post_agent_dispatch.py`, `after_agent_governance_dispatch.py`, `after_file_edit.py`,
   `before_mcp_execution.py`, `pre_mcp_gate.py`.
3. `python ops_scripts/ci/run_contract_gates.py` — loads with no dangling gate-file references
   (and the kept disk-side plan gates still register/run).
4. Targeted pytest on the surviving plan-format tests (e.g. `tests/unit/.../test_plan_format*` /
   `test_plan_wave_summary*` / `test_plan_definition_of_done*`).
5. Dangling-reference grep sweep returns clean (Wave 6).
6. `python tools/generate_full_adg.py` not required; but run a Python `compileall` over the edited
   `.claude/governance/scripts` + `ops_scripts/ci` dirs to catch syntax breakage from surgical edits.

## Delivery
Commit in waves on `feat/notion-wave-enforcement-removal`; push `feat/notion-wave-enforcement-removal`
and open a PR to `main`. No Notion plan row, no disk plan file (this very change removes that ceremony;
`pre_write_plan_mint_gate` would block one anyway). Memory writeback: record the ADR-100 keep-decision
reversal.

## Risk notes
- **Reverses ADR-100's explicit keep.** Will add a short ADR superseding ADR-100's §"kept Notion
  cluster" so the decision is traceable.
- Surgical edits to **kept** hooks (`after_file_edit`, `pre_mcp_gate`, `before_mcp_execution`,
  `post_agent_dispatch`, `after_agent_governance_dispatch`) are the highest-risk step — each is verified
  by re-running the hook after edit (Verification #2).
- `~90 tools/notion/*` one-shot scripts are the bulk of the file count but lowest risk (no live caller);
  each spot-checked before delete.
