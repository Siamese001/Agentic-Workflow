# Wave 6 — HITL Gates for Deletions, Ambiguous Classifications, and Archive Decisions

## Scope
Add HITL gates at all high-leverage mutation decision points:
- File archiving/deletion in LocationHealerAgent via hitl_approval_fn injection
- Ambiguous classification flag (top-2 delta < 0.15) in FileClassificationAgent
- HITL archive gate wired in execute_ssot.py before heal_violations()
- New hitl_decision_logger.py for structured, auditable HITL decision records

## CODE_COMMIT
898da48ac6c96449cbb021d10490cd55bd5dd82b

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L5_safety/reasoning/FileClassificationAgent.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
system_learning/engines/hitl_decision_logger.py
tests/agentic_core/test_wave6_hitl_gates.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/wave6_evidence.md

## INSPECTED_FILES
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/reasoning/FileClassificationAgent.py
agentic_core/L0_routing/scripts/execute_ssot.py
system_learning/engines/hitl_decision_logger.py
tests/agentic_core/test_wave6_hitl_gates.py

## HITL Trigger Points Implemented
1. FILE_DELETION: LocationHealerAgent._heal_via_archiving() -- hitl_approval_fn kwarg
   + self._hitl_approval_fn instance fallback injected by execute_ssot.py
2. AMBIGUOUS_CLASSIFICATION: FileClassificationAgent.classify_file_with_confidence()
   -- HITL_FLAGGED annotation when top-2 confidence delta < 0.15
3. ARCHIVE_GATE: execute_ssot.py _w6_hitl_archive_gate() wired onto
   location_validator._hitl_approval_fn before heal_violations() call
4. DECISION_LOG: system_learning/engines/hitl_decision_logger.log_hitl_decision()
   -- ASCII-only, thread-safe, appends to docs/reports/evidence/wave6_evidence.md

## pytest wave6
$ python -m pytest -q --color=no tests/agentic_core/test_wave6_hitl_gates.py
collected 8 items

tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exists PASSED [ 12%]
tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exports_log_fn PASSED [ 25%]
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_hitl_approval_fn_param PASSED [ 37%]
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_reads_instance_hitl_fn PASSED [ 50%]
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_flagged_delta PASSED [ 62%]
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_logs_decision PASSED [ 75%]
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_wires_hitl_approval_fn PASSED [ 87%]
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_hitl_gate_before_heal_violations PASSED [100%]

8 passed in 0.17s
