---
slug: legacy-windsurf-tree-decommission-9f2c47
plan_type: platform_core_change
status: In Progress
created: 2026-06-07
owner: Claude Code
supersedes: []
relates_to:
  - cursor-windsurf-codeium-decommission-dec0de     # parent decommission; this is its W5 live-wiring tail
  - cursor-naming-rename-w5-b4f1a9                   # finished the surface rename; deferred the legacy-tree to here
---

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-08

# Legacy `_legacy_windsurf` / `_legacy_cursor` Tree Decommission

> **L1 COMPLETE 2026-06-08 (IDE_archive).** Rollback tag
> `pre-legacy-tree-decommission-9f2c47` exists, and the frozen inventory lives at
> [legacy_tree_classification_9f2c47.md](../docs/reports/decommission/legacy_tree_classification_9f2c47.md)
> with machine-readable detail in
> [legacy_tree_classification_9f2c47.json](../docs/reports/decommission/legacy_tree_classification_9f2c47.json).
> Actual clean-PR tree size is 167 `_legacy_windsurf` files and 13 `_legacy_cursor` files.
> Classification result: 42 LIVE_HELPER, 138 DEAD_ARCHIVE.
> No legacy-tree files were moved or deleted in L1. Lifecycle start required the documented
> `PLAN_REGISTRATION_BYPASS=1` because `tools/plan_lifecycle/wave_execution_state.py` still imports
> the stale `_legacy_windsurf/_plan_registration.py`, which reads `.windsurf/state` instead of
> `.claude/state`; fixing that importer is L2 work.

> Created 2026-06-07 as the **deferred tail** of the decommission. The naming-rename plan
> [cursor-naming-rename-w5-b4f1a9](cursor-naming-rename-w5-b4f1a9.md) de-branded the live surface
> (`post_agent_*`, `artifacts/governance`, `.claude/state` ledger, `tools/plan_lifecycle`) and
> **explicitly deferred** the two frozen legacy trees because they still contain **live-imported
> helper modules**. This plan migrates those helpers to neutral homes, then deletes the dead bulk.
>
> ⛔ **DO NOT bulk-delete `_legacy_windsurf/` or `_legacy_cursor/`.** They are NOT pure dead code —
> live hooks, ledger capture, and Notion tooling import shared helpers from inside them. Deleting
> first = breaking the governance chain + CI gates.

## Context (SCQA)

- **Situation.** Two frozen trees remain after the surface rename:
  `.claude/governance/scripts/_legacy_windsurf/` (**331 files**) and
  `.claude/governance/scripts/_legacy_cursor/` (**25 files**). They were retained because removing
  them would break live consumers.
- **Complication.** Each tree is a **mix**:
  1. **Live-helper subset** — shared modules imported at runtime by current (post-rename) code:
     `_plan_registration.py`, `_plan_scope_expansion_check.py`, `_wave_execution_state.py`,
     `_notion_constants.py`, `_notion_plans_status_check.py`, and the Author-Gate ledger helpers
     (`generate_calibration_report.py`, `promote_author_gate_patterns.py`, `pre_author_gate.py`,
     `post_commit_outcome_binder.py`, `apply_ledger_schema.py`, `audit_ledger_coverage.py`,
     `pre_mcp_gate.py`). Live importers found (non-exhaustive — W1 finalizes):
     - `post_agent_plan_registration_capture.py:33` → `_legacy_windsurf/_plan_registration.py`
     - `post_agent_plan_scope_audit.py:27` → `_legacy_windsurf/_plan_scope_expansion_check.py`
     - `tools/plan_lifecycle/wave_execution_state.py:50` → sys.path `_legacy_windsurf` (`_wave_execution_state`, `_plan_registration`)
     - `tools/capture/queue_to_ledger.py:33` → `_legacy_windsurf` hook dir
     - `tools/notion/wave_lifecycle_writer.py:45`, `_plan_registration_helpers.py:49`,
       `apply_plan_derived_status.py:34`, `triage_plans_duplicates.py:38` → sys.path `_legacy_windsurf`
     - `_legacy_cursor`: `tools/cursor/governance_dedup_e2e_verify.py:40`, a heartbeat-latency test.
  2. **Dead-archive bulk** — `post_cascade_*.py` (+ `.active_archive_1.py`) duplicates of the
     already-renamed live chain; pure legacy copies with no live importer.
- **Also coupled:** the **boundary constant** `agentic_core/L0_routing/config/path_constants.py
  WINDSURF_SCRIPTS_DIR = ".cursor/scripts/_legacy_windsurf"` is live-consumed by
  `static_scanner.py` (3×), `check_hardcoded_exclusions.py`, `check_terminal_cleanup.py`. The
  `.pre-commit-config.yaml` `T6a no-active-windsurf-authoring` gate guards the tree. The
  `_legacy_windsurf/_notion_plans_status_check.py` carries a **known dead-path import bug** (loads a
  non-existent `.claude/governance/.cursor/scripts/_notion_plans_status_check.py`, fail-open) — fix
  on migration.
- **Question.** How to delete both legacy trees without breaking the live governance chain, ledger
  capture, Notion tooling, ADG static scanner, or CI gates?
- **Answer.** Classify → promote the live-helper subset to a neutral canonical home → rewrite
  importers atomically → verify chain + gates fire → only then delete the dead bulk, de-brand the
  boundary constant, retire `T6a`, and hand the empty `.cursor/` dir back to dec0de for final removal.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1/L1 | P1.1–P1.3 | Inventory + classify (live-helper vs dead-archive) + rollback tag | ~10k | Actual tree differs from stale plan estimate | ✅ Done (2026-06-08) | Frozen manifest written; rollback tag set; no legacy-tree move/delete |
| W2/L2 | P2.1–P2.3 | Promote live-helper subset → neutral home + rewrite importers | ~18k | Neutral active helper copies already exist at `.claude/governance/scripts/` | ✅ Done (2026-06-08) | W1 direct-importer paths retargeted to `.claude/governance/scripts/`; lifecycle and Notion import smoke green; no legacy-tree move/delete |
| W3/L3 | P3.1 | Verify chain + tooling + gates fire post-move | ~6k | — | ✅ Done (2026-06-08) | Live dispatch fires; heartbeat fresh; wired payload gate scans 17 active hooks; lifecycle/ledger/import smokes green |
| W4/L4 | P4.1–P4.2 | De-brand boundary constant + scanner/gate consumers | ~8k | `WINDSURF_SCRIPTS_DIR` re-pointable to neutral home | ⬜ Not Started | `path_constants` constant renamed/repointed (Author-Gate + receipt); static_scanner + 2 gates updated; ADG scan parity |
| W5/L5 | P5.1–P5.3 | Delete dead-archive bulk + `_legacy_cursor`; retire `T6a`; guard cleanup | ~8k | L2–L4 green; no remaining importer | ⬜ Not Started | `_legacy_windsurf`/`_legacy_cursor` deleted; `T6a` retired or repointed; shell-guard legacy tokens pruned |
| W6/L6 | P6.1 | Zero-brand verify + hand `.cursor/` to dec0de + close | ~5k | All prior waves green | ⬜ Not Started | Repo scan: only intentional history remains; dec0de notified for `.cursor/` removal; plan closed |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Rollback tag | git tag | — | ~1k | ✅ Done: `pre-legacy-tree-decommission-9f2c47` |
| P1.2 | Classify `_legacy_windsurf` (167 on disk) | manifest | Distinguish live-helper from dead `post_cascade_*` archive; trace every importer | ~6k | ✅ Done: 42 LIVE_HELPER / 125 DEAD_ARCHIVE |
| P1.3 | Classify `_legacy_cursor` (13 on disk) | manifest | heartbeat-latency test + dedup-verify consumer | ~3k | ✅ Done: 0 LIVE_HELPER / 13 DEAD_ARCHIVE |
| P2.1 | Canonicalize neutral helper home | Active copies under `.claude/governance/scripts/` | Older `_helpers/` wording was stale; root helper copies are newer than legacy tree copies | ~8k | ✅ Done: no duplicate `_helpers/` package created |
| P2.2 | Rewrite hook importers | `post_agent_plan_registration_capture.py`, `post_agent_plan_scope_audit.py`, `_post_handlers/*` | HELPER_PATH / W2_MODULE_PATH literals | ~5k | ✅ Done |
| P2.3 | Rewrite tools importers | `tools/plan_lifecycle/wave_execution_state.py`, `tools/capture/queue_to_ledger.py`, `tools/notion/{wave_lifecycle_writer,_plan_registration_helpers,apply_plan_derived_status,triage_plans_duplicates}.py` | sys.path inserts | ~5k | ✅ Done |
| P3.1 | Verify | dispatch + gates | Hook support library was missing from clean tree; payload gate still scanned frozen legacy dir | ~6k | ✅ Done: live hook lib restored, dispatch/payload/heartbeat checks green |
| P4.1 | Boundary constant | `agentic_core/L0_routing/config/path_constants.py` (`WINDSURF_SCRIPTS_DIR`) | Author-Gate + migration receipt; rename vs value-repoint | ~4k | ⬜ |
| P4.2 | Scanner/gate consumers | `static_scanner.py`, `check_hardcoded_exclusions.py`, `check_terminal_cleanup.py` | ADG scan parity (exclusion semantics) | ~4k | ⬜ |
| P5.1 | Delete dead-archive bulk | `_legacy_windsurf/post_cascade_*` etc. | Confirm zero importer post-L2 | ~3k | ⬜ |
| P5.2 | Delete `_legacy_cursor` | `_legacy_cursor/**` + consumers | migrate test + dedup-verify first | ~3k | ⬜ |
| P5.3 | Retire `T6a` + guard cleanup | `.pre-commit-config.yaml`, `before_shell_execution`/`claude_hook_common` | guard tokens (`.windsurf`/`Windsurf`) once trees gone | ~2k | ⬜ |
| P6.1 | Zero-brand verify + close | whole repo, Notion | hand `.cursor/` dir to dec0de | ~5k | ⬜ |

## Wave Detail

### L1 — Inventory + classify
- **P1.1** `git tag pre-legacy-tree-decommission-9f2c47`.
- **P1.2/P1.3** Walk both trees; for each file record `classification` (LIVE_HELPER if any non-frozen
  importer exists, else DEAD_ARCHIVE) + the importer paths. Trace transitive imports between helpers
  (a moved helper may import a sibling). Write frozen manifest to `docs/reports/decommission/`.
- **Completed 2026-06-08:** see
  `docs/reports/decommission/legacy_tree_classification_9f2c47.{md,json}`. Direct ADG SQLite
  snapshot was consulted before deterministic text/AST fallback. The manifest records directory-level
  wildcard anchors separately from file-level importer evidence.

### L2 — Promote live-helper subset
- **P2.1** Reconciled stale `_helpers/` wording with the clean-PR tree: the neutral active helper
  home already exists at `.claude/governance/scripts/`, and those copies are newer/correcter than
  the frozen `_legacy_windsurf` copies (for example `_plan_registration.py` reads `.claude/state`
  and repo-root `plans/`, while the legacy copy still reads `.windsurf/state`). No duplicate
  `_helpers/` package was created.
- **P2.2/P2.3** Rewrote every W1 direct importer to the neutral root path (HELPER_PATH literals +
  `sys.path.insert` targets). `tools/plan_lifecycle/wave_execution_state.py` now imports the active
  `_plan_registration.py`, resolving the L1 stale `.windsurf/state` bug.
- **Gate result:** W1 direct-importer paths have no remaining legacy imports. Two intentional
  non-import legacy markers remain inside direct-importer files: a historical docstring pointer in
  `pre_ask_user_question_recommendation_gate.py` and legacy skip tokens in
  `ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py`; both are W5 cleanup material, not
  runtime helper imports. Repo-wide `_legacy_*` path literals remain by design for L4/L5.
- **Completed 2026-06-08:** focused verification green:
  `tests/unit/tools_notion/test_wave_lifecycle_writer.py`,
  `tests/unit/tools_notion/test_plan_registration_helpers.py`,
  `tests/unit/tools_notion/test_plan_registration_helpers_ds2_ds4.py` (108 passed);
  `tests/unit/windsurf_scripts/{test_plan_registration.py,test_plan_scope_expansion_check.py,test_notion_constants_url_extract.py,test_notion_plans_status_check.py,test_wave_execution_state.py}`
  (205 passed);
  `tests/unit/windsurf_scripts/{test_ssot_folder_check.py,test_pre_write_gate_core_guard.py,test_read_budget.py,test_token_telemetry.py}`
  (90 passed); `python -m tools.plan_lifecycle.wave_execution_state status`,
  `python ops_scripts/ci/check_ssot_folder_routing.py`, and
  `python ops_scripts/ci/check_apps_test_surface_parity.py` all exited 0.

### L3 — Verify
- **P3.1** Run the after-agent dispatch (audit rows + heartbeat written); run `queue_to_ledger`
  smoke; import `tools.notion.wave_lifecycle_writer`; run `check_post_agent_alive` / `check_post_agent_payload`;
  run plan-lifecycle CLI. All green.
- **Completed 2026-06-08:** W3 found and fixed two live-chain defects before closing:
  `.claude/hooks/after_agent_governance_dispatch.py` and sibling hooks imported a missing
  `lib.claude_hook_common` support package, and `check_post_agent_payload.py` still scanned the
  frozen `_legacy_windsurf` tree. W3 restored the live hook support library under
  `.claude/hooks/lib/`, repointed hook tests to `.claude/hooks`, made the payload gate scan the wired
  active chain (17 hooks), and converted active payload readers to `_post_agent_payload`.
  Verification passed: 34 hook tests; `check_post_agent_payload.py --verbose`; dispatch smoke via
  `.claude/hooks/after_agent_governance_dispatch.py`; `check_post_agent_alive.py`; `queue_to_ledger.py
  --dry-run`; `tools.plan_lifecycle.wave_execution_state status`; and import smoke for
  `tools.notion.wave_lifecycle_writer`, `tools.capture.queue_to_ledger`, and the dispatch hook.
  Dispatch still surfaces a non-blocking ADG audit warning (`tool_routing append failed: no such
  table: events`), but the dispatcher exits 0 and heartbeat freshness passes.

### L4 — De-brand boundary constant + consumers
- **P4.1** Author-Gate (`platform_core_change`) + migration receipt; rename/repoint
  `WINDSURF_SCRIPTS_DIR` to the neutral `_helpers/` path (or remove if the tree is gone by sequencing).
- **P4.2** Update `static_scanner.py` (3×), `check_hardcoded_exclusions.py`, `check_terminal_cleanup.py`.
  Re-run ADG static scan; confirm exclusion-set parity (no new/missing nodes).

### L5 — Delete dead bulk + retire gate
- **P5.1** `git rm` the DEAD_ARCHIVE files (confirm zero importer). **P5.2** Migrate `_legacy_cursor`
  consumers (test + `governance_dedup_e2e_verify.py`), then `git rm` `_legacy_cursor/`. **P5.3** Retire
  `T6a no-active-windsurf-authoring` (no tree left to guard) or repoint; prune now-dead guard tokens
  from `claude_hook_common.LEGACY_EXECUTION_TOKENS` once `.windsurf`/legacy refs are gone.

### L6 — Verify + close
- **P6.1** Repo-wide scan; remaining `windsurf`/`cursor` hits must be intentional history. Hand the now-
  empty `.cursor/` dir to dec0de (its W6 owns the physical `.cursor/` removal + `before_shell_execution`
  `.cursor` delete-guard). Emit `PLAN_COMPLETE:`; flip Notion row to Completed.

## Definition of Done

| # | Criterion | Verify / Defer |
|---|-----------|----------------|
| 1 | Rollback tag `pre-legacy-tree-decommission-9f2c47` exists before any change | Verify: `git tag` |
| 2 | Frozen classification manifest (every `_legacy_*` file tagged + importers traced) | Verify: manifest in `docs/reports/decommission/` |
| 3 | Zero `_legacy_windsurf`/`_legacy_cursor` imports remain in non-frozen code | Verify: Grep == 0 |
| 4 | After-agent governance chain still fires (audit rows + heartbeat) post-move | Verify: run dispatch, inspect `artifacts/governance/` |
| 5 | Smoke run: `python -m tools.plan_lifecycle.wave_execution_state status` exits 0; `queue_to_ledger` + `wave_lifecycle_writer` import OK | Verify: exit codes |
| 6 | `WINDSURF_SCRIPTS_DIR` boundary edit carries Author-Gate + migration receipt; ADG scan parity | Verify: receipt + scan diff |
| 7 | `_legacy_windsurf/` and `_legacy_cursor/` deleted; `T6a` retired/repointed | Verify: `git status` + pre-commit run |
| 8 | `python ops_scripts/ci/run_contract_gates.py` exits 0 | Verify: command output |
| 9 | Repo scan finds only intentional historical mentions; dec0de handed `.cursor/` removal | Verify: Grep w/ allowlist + dec0de note |

**Verification vs Deferral:** L1–L3 (classify + promote + verify) are the committed core and unblock
everything. L4 (boundary constant) and L5 (deletion) are each independently deferral-eligible — if L1
shows a live helper with deep transitive coupling, isolate it and stop after L3 (the tree stays but is
import-clean). The physical `.cursor/` dir removal stays owned by dec0de (do not duplicate).

## Risk / blast-radius notes
- **Highest risk:** L2 helper promotion — `sys.path.insert` consumers resolve bare module names
  (`import _wave_execution_state`); moving requires updating the inserted path AND ensuring no name
  collision at the new location.
- **Boundary edit:** L4 touches `agentic_core/path_constants.py` → Author-Gate + receipt; ADG static
  scanner consumes the constant, so re-run the scan and diff node/edge counts.
- **Self-referential guard:** `before_shell_execution`/`claude_hook_common` still block `.windsurf`/
  `Windsurf` tokens — neutralize for delete waves, prune tokens in L5/P5.3 only after the trees are gone.
- **Concurrency:** a separate agent has been active in this repo (branch switches, `apps_rg` edits) —
  do each wave as commit+push cycles on an isolated branch; merge (not destructive squash) if main diverges.
- **Known bug to fix in transit:** `_legacy_windsurf/_notion_plans_status_check.py` dead `.cursor/scripts`
  import path.

WAVE_COMPLETE: YES
WAVE_COMPLETE_NOTE: plan=legacy-windsurf-tree-decommission-9f2c47 wave=W3/L3 date=2026-06-08 artifacts=docs/reports/decommission/legacy_tree_classification_9f2c47.md,docs/reports/decommission/legacy_tree_classification_9f2c47.json note="live dispatch, heartbeat, payload gate, queue dry-run, lifecycle/import smokes verified; hook support lib restored"
