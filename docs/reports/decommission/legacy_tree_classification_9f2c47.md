# Legacy Tree Classification Manifest (legacy-windsurf-tree-decommission-9f2c47)

Generated UTC: `2026-06-08T19:22:56.432464+00:00`
Worktree: `C:\Git\IDE_archive-clean-pr`
Branch: `codex/ide-archive-decommission-plans`
HEAD: `02ddd60717dfb4703fd8f1b51f7cb5cbfc0ed204`
Rollback tag: `pre-legacy-tree-decommission-9f2c47` -> `f39dfe63bb0ba995916138e0da5db9882291beff`

## Scope

L1 inventory/classification only. No files under `_legacy_windsurf` or `_legacy_cursor` were moved or deleted.

## Actual Tree Counts

| Tree | Files | LIVE_HELPER | DEAD_ARCHIVE |
|---|---:|---:|---:|
| `.claude/governance/scripts/_legacy_windsurf` | 167 | 42 | 125 |
| `.claude/governance/scripts/_legacy_cursor` | 13 | 0 | 13 |
| **Total** | **180** | **42** | **138** |

## Method

- Used direct ADG SQLite snapshot first: `C:\Git\IDE_archive\artifacts\adg\adg_indexed_06082026_1423.sqlite`.
- Scanned active non-frozen code/config/test surfaces for exact legacy paths and sys.path/import patterns.
- Parsed intra-legacy Python imports and promoted dependencies of directly referenced files to `LIVE_HELPER`.
- Directory-level wildcard anchors are recorded in JSON but do not classify every file as live without file-level evidence.

## Important Findings

- `tools/plan_lifecycle/wave_execution_state.py` still imports `_legacy_windsurf/_plan_registration.py`, whose constants point at `.windsurf/state` and `.windsurf/plans`; this explains the wave-start registration cache miss in L1.
- `_legacy_cursor` has active directory-level references, but no file-level importer for any file that currently exists there; the heartbeat latency test points at `_legacy_cursor/post_agent_heartbeat.py`, while the tree contains `post_cursor_agent_heartbeat.py`.
- The plan prose estimates 331 `_legacy_windsurf` files and 25 `_legacy_cursor` files; this clean PR worktree currently contains 167 and 13 respectively.
- JSON detail: `docs/reports/decommission/legacy_tree_classification_9f2c47.json`.

## File Classification

| Path | Classification | Reason | Direct Importers | Transitive From |
|---|---|---|---:|---:|
| `.claude/governance/scripts/_legacy_cursor/README.md` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_adr_registry_capture.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_author_gate_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_author_gate_suite.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_cleanup.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_grep_budget_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_heartbeat.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_notion_plans_status_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_plan_complete_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_plan_creation_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_plans_dup_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_read_budget_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_cursor/post_cursor_agent_token_telemetry.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_apps_test_surface_check.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,test | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_author_gate_pipeline_check.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_author_gate_queue.py` | `LIVE_HELPER` | direct_active_reference:test | 4 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_bypass_boilerplate.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_deferred_scope_plan_scaffold.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_notion_canonical.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_notion_constants.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,test,tooling | 32 | 3 |
| `.claude/governance/scripts/_legacy_windsurf/_notion_plans_status_check.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,test,tooling | 7 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_plan_lifecycle.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_plan_registration.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,governance_runtime,test,tooling | 6 | 1 |
| `.claude/governance/scripts/_legacy_windsurf/_plan_scope_expansion_check.py` | `LIVE_HELPER` | direct_active_reference:governance_runtime,test | 5 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_plans_dup_detector.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,test | 4 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_cascade_payload.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_cascade_payload.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_handlers/__init__.py` | `LIVE_HELPER` | direct_active_reference:test | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_handlers/cleanup.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_handlers/grep_budget.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_handlers/heartbeat.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_handlers/read_budget.py` | `LIVE_HELPER` | direct_active_reference:test | 4 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_post_handlers/token_telemetry.py` | `LIVE_HELPER` | direct_active_reference:test | 4 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_progress_reporter.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_secret_patterns.py` | `LIVE_HELPER` | transitive_dependency_of_live_helper | 0 | 1 |
| `.claude/governance/scripts/_legacy_windsurf/_serialization_sentinel.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_session_id_shared.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/_ssot_folder_check.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,test | 4 | 1 |
| `.claude/governance/scripts/_legacy_windsurf/_wave_execution_state.py` | `LIVE_HELPER` | direct_active_reference:test,tooling | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/apply_append_only_triggers.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,tooling | 3 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/apply_ledger_schema.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/audit_ledger_coverage.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/author_gate_ledger_integrity.py` | `LIVE_HELPER` | direct_active_reference:test | 3 | 1 |
| `.claude/governance/scripts/_legacy_windsurf/author_gate_marker_validator.py` | `LIVE_HELPER` | transitive_dependency_of_live_helper | 0 | 1 |
| `.claude/governance/scripts/_legacy_windsurf/backfill_cat4_decisions.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/capture_author_gate.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/defer.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/filesystem_mcp_launcher.js` | `LIVE_HELPER` | direct_active_reference:test | 6 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/generate_calibration_report.py` | `LIVE_HELPER` | direct_active_reference:tooling | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/generate_rules_index.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/install_git_hooks.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/install_post_commit_phase_closer.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/manual_post_cascade_replay.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/manual_post_cascade_replay.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/mcp_fleet_health.py` | `LIVE_HELPER` | direct_active_reference:tooling | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/mcp_python_heartbeat.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/mcp_python_supervisor.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/plan_driven_closer.py` | `LIVE_HELPER` | direct_active_reference:test,tooling | 6 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_adg_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_adg_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_adr_registry_capture.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_adr_registry_capture.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_ag_queue_drain_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_ag_queue_drain_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_ag_queue_seed_capture.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_ag_queue_seed_capture.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_ask_user_question_packet_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_ask_user_question_packet_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_capture.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_capture.py` | `LIVE_HELPER` | direct_active_reference:tooling | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_miss_detector.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_miss_detector.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_pipeline_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_pipeline_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_schema_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_schema_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_suite.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_suite.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_ui_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_author_gate_ui_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_cleanup.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_cleanup.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_deferred_scope_capture.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_deferred_scope_capture.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_dispatch.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_dispatch.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_fortknox_integrity_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_fortknox_integrity_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_grep_budget_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_grep_budget_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_heartbeat.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_heartbeat.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_long_command_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_long_command_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_hygiene_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_hygiene_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_orphan_reap.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_orphan_reap.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_preflight_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_preflight_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_serialization_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_mcp_serialization_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_next_step_capture.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_next_step_capture.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_next_step_miss_detector.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_next_step_miss_detector.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_notion_plan_identity_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_notion_plan_identity_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_notion_plans_status_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_notion_plans_status_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_complete_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_complete_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_creation_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_creation_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_evidence_gate.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_evidence_gate.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_lifecycle_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_lifecycle_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_registration_capture.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_registration_capture.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_scope_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plan_scope_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plans_dup_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_plans_dup_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_read_budget_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_read_budget_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_resource_budget_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_resource_budget_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_router_decision_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_router_decision_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_scope_drift_detector.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_scope_drift_detector.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_token_telemetry.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_token_telemetry.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_wave_completion_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_wave_completion_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_wave_lifecycle_capture.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_wave_lifecycle_capture.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_writeback_audit.active_archive_1.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_cascade_writeback_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_commit_outcome_binder.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_commit_phase_closer.py` | `LIVE_HELPER` | direct_active_reference:tooling | 4 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_mcp_audit.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_run_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_setup_worktree.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_write_audit.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_write_cert_stage.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_write_mcp_config_sync.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/post_write_plan_reconcile.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_ask_user_question_gate.py` | `LIVE_HELPER` | direct_active_reference:governance_runtime,test | 5 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_author_gate.py` | `LIVE_HELPER` | direct_active_reference:test | 3 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_mcp_gate.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,test,tooling | 7 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_notion_plan_creation_gate.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_notion_plan_write_gate.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_prompt_classifier.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_read_gate.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_run_gate.py` | `LIVE_HELPER` | direct_active_reference:configuration,test | 10 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_ag_queue_surface.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_author_gate_reminder.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_deferred_plan_gate.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_deferred_scope_recovery.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_grep_for_deps_warning.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_hook_health_check.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_plan_registration_refresh.py` | `LIVE_HELPER` | direct_active_reference:test | 3 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_plan_registration_surface.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_plans_dup_surface.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_reminder_check.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_user_prompt_weekly_report.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_write_fortknox_guard.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_write_gate.py` | `LIVE_HELPER` | direct_active_reference:test | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/pre_write_plan_scope_gate.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/promote_author_gate_patterns.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/refresh-windsurf-docs.active_archive_1.ps1` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/refresh-windsurf-docs.ps1` | `LIVE_HELPER` | direct_active_reference:governance_runtime | 1 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/rollback_bad_patches.py` | `LIVE_HELPER` | direct_active_reference:tooling | 4 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/sync_mcp_config.py` | `LIVE_HELPER` | direct_active_reference:ci_or_maintenance,tooling | 4 | 1 |
| `.claude/governance/scripts/_legacy_windsurf/unified_notion_status_auditor.py` | `LIVE_HELPER` | direct_active_reference:tooling | 2 | 0 |
| `.claude/governance/scripts/_legacy_windsurf/unified_plan_creation_auditor.py` | `DEAD_ARCHIVE` | no active non-frozen importer or transitive live dependency found | 0 | 0 |
