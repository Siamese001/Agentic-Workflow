# Pre-commit Bypass Evidence — Write-Gateway Residuals Commit

## Changeset (8 files)

- `agentic_core/L2_execution/tools/write_gateway.py`
- `agentic_core/L3_orchestration/engines/autonomous_execution_engine.py`
- `agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py`
- `agentic_core/L4_state/enforcement/mission_historian.py`
- `agentic_core/L4_state/enforcement/mission_historian_enforcer.py`
- `agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py`
- `tests/governance/test_cross_layer_import_freeze.py`
- `tests/governance/test_intent_emission_no_mutation.py`

## Failing Hook

- **Hook ID:** `check-anti-patterns`
- **Behavior:** Scans entire repo (`PROJECT_ROOT.rglob("*.py")`), not just staged files.
- **Result:** Reports ~200+ `[FAIL]` entries across files NOT in the changeset.

## Unrelated Paths Reported (sample)

- `agentic_core/L5_safety/types/safety_types.py` — path_fragility, silent_swallower
- `agentic_core/L5_safety/utils/cognitive_batch_processor_util.py` — silent_swallower, magic_configuration
- `agentic_core/L5_safety/utils/tiered_batch_util.py` — silent_swallower, magic_configuration
- `agentic_core/L5_safety/validators/dependencygraph_validator.py` — silent_swallower, path_fragility
- `agentic_core/L6_observability/dashboards/dashboard_generator.py` — silent_swallower
- `agentic_core/L6_observability/enforcement/reasoning_streamer.py` — silent_swallower
- `agentic_core/L6_observability/enforcement/reasoning_streamer_enforcer.py` — silent_swallower

None of these files are in the changeset.

## Remediation

The `check_anti_patterns.py` hook needs its baseline updated to reflect
the current repo state. This is tracked as existing tech debt and is
outside the scope of the write-gateway residuals refactoring.
