# Wave 0B: Restore Deleted system_learning/engines Sub-Packages

## Scope

Restore 16 deleted source files across system_learning/engines sub-packages
(arbitration, confidence, correlation, fingerprinting, l4_state_writer,
l4_audit_reader, l4_version_store, l0_threshold_tuner) and 11 shim files
under agentic_core/system_learning/. These were deleted in commit dd5b5b836
(refactor: resolve all unrecognized agentic_core subfolders) causing
ImportError in meta_learning_pipeline.py and Wave 0C wiring.

Also fixes Wave 0C pipeline wiring: MetaLearningPipeline class does not
exist - corrected to use module-level run_pipeline() function.

## CODE_COMMIT

f019e2c7d250f99dab5d7547bcbe482a7b7a92cb

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/system_learning/arbitration/__init__.py
agentic_core/system_learning/arbitration/engine.py
agentic_core/system_learning/arbitration/types.py
agentic_core/system_learning/confidence/__init__.py
agentic_core/system_learning/confidence/engine.py
agentic_core/system_learning/confidence/types.py
agentic_core/system_learning/correlation/__init__.py
agentic_core/system_learning/correlation/engine.py
agentic_core/system_learning/fingerprinting/__init__.py
agentic_core/system_learning/fingerprinting/engine.py
agentic_core/system_learning/fingerprinting/types.py
system_learning/engines/arbitration/engine.py
system_learning/engines/arbitration/types.py
system_learning/engines/confidence/engine.py
system_learning/engines/confidence/types.py
system_learning/engines/correlation/engine.py
system_learning/engines/fingerprinting/engine.py
system_learning/engines/fingerprinting/types.py
system_learning/engines/l0_threshold_tuner.py
system_learning/engines/l4_audit_reader.py
system_learning/engines/l4_state_writer.py
system_learning/engines/l4_version_store.py
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py

## FILES_CHANGED_EVIDENCE

PENDING

## INSPECTED_FILES

system_learning/engines/healing_outcome_aggregator.py
system_learning/types/healing_outcome_types.py
system_learning/pipelines/meta_learning_pipeline.py
agentic_core/system_learning/arbitration/engine.py

## pytest -q --color=no (Wave 0C invariant tests after Wave 0B restore)

```
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_defined_in_execute_ssot PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_called_before_finish_mission PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_persists_records_with_healing_actions PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_no_persist_when_empty PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_noop_on_import_error PASSED
5 passed in 0.14s
```
