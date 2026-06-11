---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\healing_waves_0C_0B_6_evidence.md'
original_relative_path: 'healing_waves_0C_0B_6_evidence.md'
source_sha256: b762404b9c4fe0f177776837b902a30478024e5eb02778c97f537ba32c966c22
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Healing Waves: Wave0C ExperienceRecord, Wave0B Restore Script, Wave6 HITL Gates, Test Markers

## Scope

Wave 0C Gap 3: Rename `class Experience` to `ExperienceRecord` in `MetaLearningAgent.py` so
the healing system does not flag its own meta-learning agent for a NAMING violation.

Wave 0B: Create `ops_scripts/general/restore_from_healing_backup.py` — categorized restore
script (test_*.py -> _quarantine/restored_tests, PascalCase*Agent.py -> reasoning/,
snake_case -> _quarantine/restored_snake_case, __init__.py -> original package paths,
naming_violations/* -> HOLD).

Wave 6 (Tier escalation HITL): Add interactive HITL gate before QWEN/GEMINI routing in
`execute_ssot.py::SovereignDecisionEngine._decide_with_routing`. Options: Approve / Skip /
Force LOCAL_AGENT. Auto-approves in non-interactive environments.

Wave 6 (SSOT conflict HITL): Add HITL gate in `LocationHealerAgent.heal_violations` when a
dict violation provides a `canonical_path`/`suggested_path` field. Options: Use validator
path / Let healer decide / Skip.

Test markers: Add `@pytest.mark.unit_min_deps` to all test functions in
`test_wave4_v15_agent_id.py`, `test_wave5_longpaths_guard.py`, `test_wave6_hitl_gates.py`
so they execute under the default pytest suite.

## CODE_COMMIT

0a2b3d810ec34ee1e367392467334b3d0f210702

## EVIDENCE_COMMIT

aabfe42e210255fb0f528995544498b478afdb72

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
ops_scripts/general/restore_from_healing_backup.py
tests/agentic_core/test_wave4_v15_agent_id.py
tests/agentic_core/test_wave5_longpaths_guard.py
tests/agentic_core/test_wave6_hitl_gates.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/healing_waves_0C_0B_6_evidence.md

## INSPECTED_FILES

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
agentic_core/L5_safety/reasoning/LocationHealerAgent.py
agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py
agentic_core/L5_safety/reasoning/LocationValidatorAgent.py
ops_scripts/general/restore_from_healing_backup.py
tests/agentic_core/test_wave4_v15_agent_id.py
tests/agentic_core/test_wave5_longpaths_guard.py
tests/agentic_core/test_wave6_hitl_gates.py
tests/conftest.py
pytest.ini

## Wave tests (collected 13, executed 13)

$ python -m pytest tests/agentic_core/test_wave4_v15_agent_id.py tests/agentic_core/test_wave5_longpaths_guard.py tests/agentic_core/test_wave6_hitl_gates.py -q --color=no --tb=short
collected 13 items

tests/agentic_core/test_wave4_v15_agent_id.py::test_no_execute_calls_missing_agent_id PASSED
tests/agentic_core/test_wave4_v15_agent_id.py::test_wave4_registry_entries_exist PASSED
tests/agentic_core/test_wave4_v15_agent_id.py::test_execute_calls_count_at_least_eleven PASSED
tests/agentic_core/test_wave5_longpaths_guard.py::test_longpaths_bypass_guard_present PASSED
tests/agentic_core/test_wave5_longpaths_guard.py::test_longpaths_guard_wraps_advisory PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exists PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_hitl_decision_logger_exports_log_fn PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_hitl_approval_fn_param PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_location_healer_reads_instance_hitl_fn PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_flagged_delta PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_file_classification_hitl_logs_decision PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_wires_hitl_approval_fn PASSED
tests/agentic_core/test_wave6_hitl_gates.py::test_execute_ssot_hitl_gate_before_heal_violations PASSED

13 passed in 1.10s

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

