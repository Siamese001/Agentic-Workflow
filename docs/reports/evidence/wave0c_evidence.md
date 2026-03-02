# Wave 0C: Wire Meta-Learning Pipeline into execute_ssot.py

## Scope

Wire HealingOutcomeIntakeAdapter and MetaLearningPipeline into execute_ssot.py
via a lazy-import helper _fire_meta_learning_intake() called before finish_mission().
Both imports are guarded - safe no-op until Wave 0B restores archived modules.

## CODE_COMMIT

d5fc36da3934bbd7192317de33ccd8a07129d9ef

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py

## FILES_CHANGED_EVIDENCE

PENDING

## INSPECTED_FILES

agentic_core/L0_routing/scripts/execute_ssot.py
system_learning/engines/healing_outcome_intake_adapter.py
system_learning/engines/healing_outcome_aggregator.py
system_learning/engines/in_memory_healing_outcome_intake_store.py
system_learning/types/healing_outcome_types.py
system_learning/pipelines/meta_learning_pipeline.py

## pytest -q --color=no (Wave 0C invariant tests)

```
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_defined_in_execute_ssot PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_called_before_finish_mission PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_persists_records_with_healing_actions PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_intake_adapter_no_persist_when_empty PASSED
tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py::test_fire_meta_learning_intake_noop_on_import_error PASSED
5 passed in 0.15s
```
