---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\execute_ssot_refactor_plan.md'
original_relative_path: 'execute_ssot_refactor_plan.md'
source_sha256: b65c7fbcca7beddc2ae115bc9ee14fa7f973cb4c4aec4a7f3835532b9b23b251
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-13'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# execute_ssot.py Refactoring Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Goal
Split the 7,271-line monolith `agentic_core/L0_routing/scripts/execute_ssot.py` into
focused submodules, keeping `execute_ssot.py` as a thin orchestrator that re-exports
everything for backward compatibility.

## Target Module Layout
All new files live alongside execute_ssot.py in `agentic_core/L0_routing/scripts/`:

| New file | Line range (approx) | Responsibility |
|---|---|---|
| `_ssot_types.py` | 824-1163 | Dataclasses, enums: `ConfidenceScore`, `FailureType`, `RoutingTier`, `RoutingInputs`, `RoutingDecision`, `ReconciliationViolation`, `ReconciliationManifest`, `ASTCodeQualityValidator`, `HealContext` |
| `_ssot_routing.py` | 957-2131 | `compute_routing_decision`, `SovereignDecisionEngine` (+ aliases) |
| `_ssot_meta_learning.py` | 128-474 | `_fire_meta_learning_intake` |
| `_ssot_validation_artifacts.py` | 1165-1411 | `_normalize_finding_id`, `_write_pre_validation_json`, `_write_post_validation_json`, `_write_run_manifest_json`, `_write_decision_summary_json`, `_write_artifact_integrity_json`, `_record_healing_action` |
| `_ssot_phases.py` | 2274-3689 | `execute_phase1..7`, `_run_gravity_repair_global`, `discover_agents_from_registry`, `RuntimeStateManager` |
| `_ssot_reporting.py` | 3689-6083 | `save_comprehensive_reports`, `save_aggregate_report`, `try_summon_orchestrator`, `EXECUTION_PLAN`, `_print_*`, `_collect_*`, `_build_*`, `_write_mandatory_json_output`, `_write_heal_run_complete`, `_write_failure_forensics`, `_print_executive_summary` |
| `_ssot_pipeline.py` | 6083-6290 | `run_pipeline`, `print_execution_plan`, `resolve_agent_subset`, `list_available_agents`, `_emit_adg_pre_run_artifact` |

`execute_ssot.py` retains:
- All module-level imports and lazy loaders
- Bootstrap stubs, constants (`REPO_ROOT`)
- `_fire_meta_learning_intake` re-export
- CLI helpers (`_configure_logging`, `_maybe_force_utf8_*`, `_v15_*`)
- `run_fence_self_check`, `resolve_repo_root`
- `PreFlightValidator`, `NonInteractiveGuard`, `with_retry`
- `_get_l5_agent_roster`, `_preflight_import_check`, `_optional_runtime_guard`
- `_legacy_main`, `main`, `GracefulExitHandler`, `load_agents`
- Re-exports of all symbols from submodules for backward compat

## Execution Steps
1. Create `_ssot_types.py`
2. Create `_ssot_routing.py`
3. Create `_ssot_meta_learning.py`
4. Create `_ssot_validation_artifacts.py`
5. Create `_ssot_phases.py`
6. Create `_ssot_reporting.py`
7. Create `_ssot_pipeline.py`
8. Replace body of `execute_ssot.py` with thin orchestrator + re-exports
9. Run `python -c "import agentic_core.L0_routing.scripts.execute_ssot"` to verify import

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

