---
slug: legacy-windsurf-tree-decommission-9f2c47
plan_type: platform_core_change
status: Completed
created: 2026-06-07
owner: Claude Code
supersedes: []
relates_to:
  - cursor-windsurf-codeium-decommission-dec0de     # parent decommission; this is its W5 live-wiring tail
  - cursor-naming-rename-w5-b4f1a9                   # finished the surface rename; deferred the legacy-tree to here
---

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W6
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
> `.codex/state`; fixing that importer is L2 work.

> **PLAN COMPLETE 2026-06-08 (IDE_archive).** W6 verified that the deleted legacy trees and `.cursor/`
> directory are absent on disk and from tracked files. Active stale hook-name references were repointed
> to `post_agent_*`; the only active targeted residual is the compatibility CLI alias
> `--max-post-cursor-agent` in `check_hook_consolidation.py`. Evidence:
> [legacy_tree_w6_zero_brand_9f2c47.md](../docs/reports/decommission/legacy_tree_w6_zero_brand_9f2c47.md).

> Created 2026-06-07 as the **deferred tail** of the decommission. The naming-rename plan
> [cursor-naming-rename-w5-b4f1a9](cursor-naming-rename-w5-b4f1a9.md) de-branded the live surface
> (`post_agent_*`, `artifacts/governance`, `.codex/state` ledger, `tools/plan_lifecycle`) and
> **explicitly deferred** the two frozen legacy trees because they still contain **live-imported
> helper modules**. This plan migrates those helpers to neutral homes, then deletes the dead bulk.
>
> ⛔ **DO NOT bulk-delete `_legacy_windsurf/` or `_legacy_cursor/`.** They are NOT pure dead code —
> live hooks, ledger capture, and Notion tooling import shared helpers from inside them. Deleting
> first = breaking the governance chain + CI gates.

## Context (SCQA)

- **Situation.** Two frozen trees remain after the surface rename:
  `.codex/governance/scripts/_legacy_windsurf/` (**331 files**) and
  `.codex/governance/scripts/_legacy_cursor/` (**25 files**). They were retained because removing
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
  non-existent `.codex/governance/.cursor/scripts/_notion_plans_status_check.py`, fail-open) — fix
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
| W2/L2 | P2.1–P2.3 | Promote live-helper subset → neutral home + rewrite importers | ~18k | Neutral active helper copies already exist at `.codex/governance/scripts/` | ✅ Done (2026-06-08) | W1 direct-importer paths retargeted to `.codex/governance/scripts/`; lifecycle and Notion import smoke green; no legacy-tree move/delete |
| W3/L3 | P3.1 | Verify chain + tooling + gates fire post-move | ~6k | — | ✅ Done (2026-06-08) | Live dispatch fires; heartbeat fresh; wired payload gate scans 17 active hooks; lifecycle/ledger/import smokes green |
| W4/L4 | P4.1–P4.2 | De-brand boundary constant + scanner/gate consumers | ~8k | Neutral `.codex/governance/scripts` SSOT already exists | ✅ Done (2026-06-08) | `GOVERNANCE_SCRIPTS_DIR` added; deprecated alias repointed; static_scanner + 2 gates updated; ADG scan-root parity green |
| W5/L5 | P5.1–P5.3 | Delete dead-archive bulk + `_legacy_cursor`; retire `T6a`; guard cleanup | ~8k | L2–L4 green; no remaining importer | ✅ Done (2026-06-08) | `_legacy_windsurf`/`_legacy_cursor` deleted; active tests/consumers repointed; shell-guard legacy tokens pruned |
| W6/L6 | P6.1 | Zero-brand verify + hand `.cursor/` to dec0de + close | ~5k | All prior waves green | ✅ Done (2026-06-08) | Repo scan allowlisted; `.cursor/` absent on disk/tracked files; plan closed |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Rollback tag | git tag | — | ~1k | ✅ Done: `pre-legacy-tree-decommission-9f2c47` |
| P1.2 | Classify `_legacy_windsurf` (167 on disk) | manifest | Distinguish live-helper from dead `post_cascade_*` archive; trace every importer | ~6k | ✅ Done: 42 LIVE_HELPER / 125 DEAD_ARCHIVE |
| P1.3 | Classify `_legacy_cursor` (13 on disk) | manifest | heartbeat-latency test + dedup-verify consumer | ~3k | ✅ Done: 0 LIVE_HELPER / 13 DEAD_ARCHIVE |
| P2.1 | Canonicalize neutral helper home | Active copies under `.codex/governance/scripts/` | Older `_helpers/` wording was stale; root helper copies are newer than legacy tree copies | ~8k | ✅ Done: no duplicate `_helpers/` package created |
| P2.2 | Rewrite hook importers | `post_agent_plan_registration_capture.py`, `post_agent_plan_scope_audit.py`, `_post_handlers/*` | HELPER_PATH / W2_MODULE_PATH literals | ~5k | ✅ Done |
| P2.3 | Rewrite tools importers | `tools/plan_lifecycle/wave_execution_state.py`, `tools/capture/queue_to_ledger.py`, `tools/notion/{wave_lifecycle_writer,_plan_registration_helpers,apply_plan_derived_status,triage_plans_duplicates}.py` | sys.path inserts | ~5k | ✅ Done |
| P3.1 | Verify | dispatch + gates | Hook support library was missing from clean tree; payload gate still scanned frozen legacy dir | ~6k | ✅ Done: live hook lib restored, dispatch/payload/heartbeat checks green |
| P4.1 | Boundary constant | `agentic_core/L0_routing/config/path_constants.py` (`WINDSURF_SCRIPTS_DIR`) | Author-Gate + migration receipt; rename vs value-repoint | ~4k | ✅ Done: neutral `GOVERNANCE_SCRIPTS_DIR` added; branded alias repointed for compatibility |
| P4.2 | Scanner/gate consumers | `static_scanner.py`, `check_hardcoded_exclusions.py`, `check_terminal_cleanup.py` | ADG scan parity (exclusion semantics) | ~4k | ✅ Done: live consumers import neutral constant |
| P5.1 | Delete dead-archive bulk | `_legacy_windsurf/post_cascade_*` etc. | Confirm zero importer post-L2 | ~3k | ✅ Done |
| P5.2 | Delete `_legacy_cursor` | `_legacy_cursor/**` + consumers | migrate test + dedup-verify first | ~3k | ✅ Done |
| P5.3 | Retire `T6a` + guard cleanup | `.pre-commit-config.yaml`, `before_shell_execution`/`codex_hook_common` | guard tokens (`.windsurf`/`Windsurf`) once trees gone | ~2k | ✅ Done |
| P6.1 | Zero-brand verify + close | whole repo, Notion | hand `.cursor/` dir to dec0de | ~5k | ✅ Done |

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
  home already exists at `.codex/governance/scripts/`, and those copies are newer/correcter than
  the frozen `_legacy_windsurf` copies (for example `_plan_registration.py` reads `.codex/state`
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
  `.codex/hooks/after_agent_governance_dispatch.py` and sibling hooks imported a missing
  `lib.codex_hook_common` support package, and `check_post_agent_payload.py` still scanned the
  frozen `_legacy_windsurf` tree. W3 restored the live hook support library under
  `.codex/hooks/lib/`, repointed hook tests to `.codex/hooks`, made the payload gate scan the wired
  active chain (17 hooks), and converted active payload readers to `_post_agent_payload`.
  Verification passed: 34 hook tests; `check_post_agent_payload.py --verbose`; dispatch smoke via
  `.codex/hooks/after_agent_governance_dispatch.py`; `check_post_agent_alive.py`; `queue_to_ledger.py
  --dry-run`; `tools.plan_lifecycle.wave_execution_state status`; and import smoke for
  `tools.notion.wave_lifecycle_writer`, `tools.capture.queue_to_ledger`, and the dispatch hook.
  Dispatch still surfaces a non-blocking ADG audit warning (`tool_routing append failed: no such
  table: events`), but the dispatcher exits 0 and heartbeat freshness passes.

### L4 — De-brand boundary constant + consumers
- **P4.1** Author-Gate (`platform_core_change`) + migration receipt; rename/repoint
  `WINDSURF_SCRIPTS_DIR` to the neutral `_helpers/` path (or remove if the tree is gone by sequencing).
- **P4.2** Update `static_scanner.py` (3×), `check_hardcoded_exclusions.py`, `check_terminal_cleanup.py`.
  Re-run ADG static scan; confirm exclusion-set parity (no new/missing nodes).
- **Completed 2026-06-08:** The clean tree already had the neutral
  `.codex/governance/scripts` root, so L4 added `GOVERNANCE_SCRIPTS_DIR` as the active exported
  SSOT and repointed the deprecated `WINDSURF_SCRIPTS_DIR` alias to it for compatibility. The ADG
  static scanner, `check_hardcoded_exclusions.py`, and `check_terminal_cleanup.py` now consume the
  neutral symbol. The two CI gates also bootstrap their own repo root before importing constants so
  direct script execution cannot resolve a sibling worktree's `agentic_core`. Core-boundary receipt:
  `docs/reports/decommission/legacy_tree_decommission_w4_core_addition_receipt.json`.
- **Verification passed:** focused path/scanner tests (29 passed), direct hardcoded-exclusion and
  terminal-cleanup gates on touched files, static scanner root parity smoke, `py_compile`,
  live-consumer token scan, `git diff --check`, and strict plan-format compliance. A broader
  `test_path_constants.py` run still has pre-existing unrelated failures in healing routing SSOT
  checks (`HEALING_CONFIDENCE_X` exposure and missing `routing_thresholds_ssot` module).

### L5 — Delete dead bulk + retire gate
- **P5.1** `git rm` the DEAD_ARCHIVE files (confirm zero importer). **P5.2** Migrate `_legacy_cursor`
  consumers (test + `governance_dedup_e2e_verify.py`), then `git rm` `_legacy_cursor/`. **P5.3** Retire
  `T6a no-active-windsurf-authoring` (no tree left to guard) or repoint; prune now-dead guard tokens
  from `codex_hook_common.LEGACY_EXECUTION_TOKENS` once `.windsurf`/legacy refs are gone.
- **Completed 2026-06-08:** Removed all tracked files under
  `.codex/governance/scripts/_legacy_windsurf/` and
  `.codex/governance/scripts/_legacy_cursor/`, then verified both directories are absent and
  `git ls-files` returns no entries for either path. Obsolete legacy-layout tests were moved under
  `tests/_archived_obsolete/legacy_tree/`; active tests and tool snapshots were repointed to
  `.codex/governance/scripts/`, `.codex/templates/`, root `plans/`, or `.codex/plans/` according
  to each live consumer's current SSOT.
- **P5.3 note:** `T6a no-active-windsurf-authoring` was already absent in the clean PR branch before
  this wave, so W5 verified the absence rather than editing `.pre-commit-config.yaml`. W5 pruned
  bare `_legacy_windsurf` / `_legacy_cursor` execution tokens from `codex_hook_common` while
  retaining broader compatibility/history guards that still apply outside this physical tree.
- **Verification passed:** legacy directories absent; tracked legacy paths absent; active deleted-path
  scan found no `_legacy_windsurf` / `_legacy_cursor` script-tree references outside archived/doc/plan
  artifacts; changed-Python `py_compile` (59 files) passed; focused hook/Notion/path tests passed
  (130 passed); broad W5 governance family passed
  (`tests/unit/windsurf_scripts`, `tests/unit/windsurf`, `tests/windsurf/scripts`,
  `test_check_plan_notion_wave_freshness.py`, `test_check_graph_reach_archival.py`: 1035 passed,
  7 skipped). `check_terminal_cleanup.py --changed-files-only --base-ref origin/main` and bounded
  changed-file `check_hardcoded_exclusions.py` passed; the full repo hardcoded-exclusion scan still
  reports pre-existing global shadow-exclusion sets outside W5 scope. Dispatch smoke exited 0;
  `check_post_agent_alive.py`, `check_post_agent_payload.py`,
  `tools.plan_lifecycle.wave_execution_state status`, `queue_to_ledger.py --dry-run`, and
  `check_refactor_decision_ledger_ssot.py` all passed. Dispatch still emits the known non-blocking
  ADG ledger warning (`tool_routing append failed: no such table: events`).

### L6 — Verify + close
- **P6.1** Repo-wide scan; remaining `windsurf`/`cursor` hits must be intentional history. Hand the now-
  empty `.cursor/` dir to dec0de (its W6 owns the physical `.cursor/` removal + `before_shell_execution`
  `.cursor` delete-guard). Emit `PLAN_COMPLETE:`; flip Notion row to Completed.
- **Completed 2026-06-08:** W6 evidence is recorded in
  `docs/reports/decommission/legacy_tree_w6_zero_brand_9f2c47.md`. `git ls-files` returned no entries
  for `.cursor`, `.windsurf`, `_legacy_windsurf`, or `_legacy_cursor`, and all four paths are absent on
  disk in this worktree. Active stale hook-name references in `.codex/templates`, `.codex/skills`,
  `.codex/rules`, root `AGENTS.md`, active CI helpers, config, and debug utilities were repointed to
  `post_agent_*` / post-agent wording. The only active targeted residual is
  `check_hook_consolidation.py` retaining `--max-post-cursor-agent` as a compatibility alias for the
  new `--max-post-agent`; broader residuals are historical docs/ADRs, explicit migration tools, or
  compatibility tests. `check_no_cursor_refs.py` and `check_windsurf_deletion_readiness.py` are green.
  Broad `run_contract_gates.py` was attempted and is blocked by a pre-existing unrelated
  `apps_lic/engines/x1d_claude_judge_adapter.py:277` direct `anthropic` import that is not in this
  wave's diff.

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
- **Self-referential guard:** `before_shell_execution`/`codex_hook_common` still block `.windsurf`/
  `Windsurf` tokens — neutralize for delete waves, prune tokens in L5/P5.3 only after the trees are gone.
- **Concurrency:** a separate agent has been active in this repo (branch switches, `apps_rg` edits) —
  do each wave as commit+push cycles on an isolated branch; merge (not destructive squash) if main diverges.
- **Known bug to fix in transit:** `_legacy_windsurf/_notion_plans_status_check.py` dead `.cursor/scripts`
  import path.

WAVE_COMPLETE: YES
WAVE_COMPLETE_NOTE: plan=legacy-windsurf-tree-decommission-9f2c47 wave=W6/L6 date=2026-06-08 artifacts=docs/reports/decommission/legacy_tree_w6_zero_brand_9f2c47.md note="verified .cursor/.windsurf/_legacy_* absence; repointed active stale hook-name references; no-cursor and windsurf-deletion readiness gates green; residuals are historical docs, migration tooling, compatibility tests, or a backwards-compatible CLI alias"
PLAN_COMPLETE: plan=legacy-windsurf-tree-decommission-9f2c47 note="Legacy _legacy_windsurf/_legacy_cursor tree decommission completed in IDE_archive; active helper importers promoted, dead trees deleted, W6 zero-brand verification recorded."
