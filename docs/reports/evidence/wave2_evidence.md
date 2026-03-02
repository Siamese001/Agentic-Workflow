# Wave 2 — GravityLeakRepairAgent scripts/ Exclusion + privileged_mutation_context

## Scope
Add `excluded_paths` field to `StructureConfig` and wire it into
`GravityLeakRepairAgent.heal_repository()` to skip `ops_scripts/` and `scripts/`
directories. Add `privileged_mutation_context` kwarg to `apply_fix()` to bypass
L0 circuit breaker for those paths.

## CODE_COMMIT
535dcccd1d6c4c3ff816a2362f36528c8962f137

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/wave2_evidence.md

## INSPECTED_FILES
agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py

## pytest wave2
$ python -m pytest -q --color=no tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py
collected 4 items

tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_structure_config_has_excluded_paths PASSED [ 25%]
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_apply_fix_has_privileged_mutation_context_param PASSED [ 50%]
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_heal_repository_excludes_ops_scripts PASSED [ 75%]
tests/agentic_core/L5_safety/test_wave2_gravity_exclusion.py::test_heal_repository_excludes_scripts PASSED [100%]

4 passed in 0.16s
