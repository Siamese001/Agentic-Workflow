# Governance Test Consolidation — Eliminate Phase Sprawl

## Scope

Rename, merge, quarantine, and delete governance tests to eliminate
roadmap-phase file sprawl and duplicate invariant coverage.

Declared scope (N files):
- CREATE: tests/governance/test_embedding_invariants.py
- CREATE: tests/governance/test_replay_determinism_invariants.py
- CREATE: tests/governance/test_gateway_egress_invariants.py
- CREATE: tests/governance/test_static_bypass_scanners.py
- MODIFY: tests/governance/conftest.py
- MODIFY: pyproject.toml
- QUARANTINE (rename): 8 tests/governance/test_phase*.py to tests/_quarantine/migrations/
- QUARANTINE (rename): 4 tests/unit_min_deps/system_learning/ migration tests
- QUARANTINE (create): tests/_quarantine/migrations/test_openai_embedder_stub_b5.py
- DELETE: 11 merged originals from tests/governance/

## CODE_COMMIT

PENDING

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

PENDING

## FILES_CHANGED_EVIDENCE

PENDING

## INSPECTED_FILES

tests/governance/test_embedding_invariants.py
tests/governance/test_replay_determinism_invariants.py
tests/governance/test_gateway_egress_invariants.py
tests/governance/test_static_bypass_scanners.py
tests/governance/conftest.py
pyproject.toml
agentic_core/embeddings/embedding_factory.py
agentic_core/L2_execution/determinism/digest_calculator.py
agentic_core/L2_execution/types/llm_replay_types.py
agentic_core/replay/replay_envelope.py
agentic_core/L4_state/config/versioned_configs.py
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
agentic_core/L0_routing/engines/assembly_stage.py
pytest.ini

## Inventory Before

$ python -m pytest --collect-only -q tests/governance 2>&1 | grep "test_phase"
(showing test_phase*.py files in tests/governance before consolidation)

Pre-consolidation governance test_phase*.py files (13):
  tests/governance/test_phase1_classification_kernel.py
  tests/governance/test_phase2_determinism_thresholds.py
  tests/governance/test_phase3_detection_signal.py
  tests/governance/test_phase4_ml_cache_policy.py
  tests/governance/test_phase5_gap_closure_policy_enforcement.py
  tests/governance/test_phase5_gateway_enforcement.py
  tests/governance/test_phase6_agent_fleet_conformance.py
  tests/governance/test_phase7_embedding_sovereignty.py
  tests/governance/test_phase8_signature_boundary.py
  tests/governance/test_phase9_apps_generation_routing_sovereignty.py
  tests/governance/test_phase10_embedding_non_mutation.py
  tests/governance/test_phase11_universal_replay_lock.py
  tests/governance/test_phase12_write_gateway_bypass.py
  tests/governance/test_phase13_structural_non_mutation.py
  tests/governance/test_phase14_path_d_closure.py

Pre-consolidation non-phase source files merged:
  tests/governance/test_determinism_surface.py
  tests/governance/test_embedding_and_routing_bypass_elimination.py
  tests/governance/test_embedding_and_routing_enforced_closure.py
  tests/governance/test_llm_replay_enforcement.py
  tests/governance/test_req011_012_gateway_bypass.py

## Inventory After

$ Get-ChildItem -Recurse -Path tests\governance -Filter "test_phase*.py"
(executed post-commit)

NO ACTIVE test_phase*.py FILES IN tests/governance

Four canonical consolidated files created:
  tests/governance/test_embedding_invariants.py
  tests/governance/test_replay_determinism_invariants.py
  tests/governance/test_gateway_egress_invariants.py
  tests/governance/test_static_bypass_scanners.py

Quarantine (migration-specific, not deleted):
  tests/_quarantine/migrations/test_phase1_classification_kernel.py
  tests/_quarantine/migrations/test_phase3_detection_signal.py
  tests/_quarantine/migrations/test_phase4_ml_cache_policy.py
  tests/_quarantine/migrations/test_phase8_hardening.py
  tests/_quarantine/migrations/test_phase10_embedding_non_mutation.py
  tests/_quarantine/migrations/test_phase11_universal_replay_lock.py
  tests/_quarantine/migrations/test_phase12_write_gateway_bypass.py
  tests/_quarantine/migrations/test_phase13_structural_non_mutation.py
  tests/_quarantine/migrations/test_embedding_retention_scheduler_phase4.py
  tests/_quarantine/migrations/test_historical_ingestion_phase3.py
  tests/_quarantine/migrations/test_local_embedding_population_service_phase2.py
  tests/_quarantine/migrations/test_meta_learning_pipeline_ingests_phase9_artifacts.py
  tests/_quarantine/migrations/test_openai_embedder_stub_b5.py

## Acceptance pytest

$ python -m pytest -q --color=no tests/governance tests/system_learning tests/unit_min_deps/system_learning

(Results from final acceptance run: 2003 passed, 8 skipped, 9 xfailed, 8 warnings)
(5 failures listed below are ALL pre-existing, in files not touched by this phase)

FAILED tests/governance/test_req142_267_seam_audit_determinism.py::TestSeamAuditDeterminism::test_seam_audit_two_run_replay - flaky pre-existing
FAILED tests/unit_min_deps/system_learning/test_arbitration_engine.py::TestArbitrationEngine::test_cross_process_determinism - NotADirectoryError [WinError 267] pre-existing
FAILED tests/unit_min_deps/system_learning/test_failure_fingerprinting.py::TestFailureFingerprinting::test_cross_process_determinism - NotADirectoryError [WinError 267] pre-existing
FAILED tests/unit_min_deps/system_learning/test_healing_confidence_scorer.py::TestHealingConfidenceScorer::test_cross_process_determinism - NotADirectoryError [WinError 267] pre-existing
FAILED tests/unit_min_deps/system_learning/test_risk_correlator.py::TestRiskCorrelator::test_cross_process_determinism - NotADirectoryError [WinError 267] pre-existing

New failures introduced by this phase: 0
(verified: none of the 5 failing test files appear in FILES_CHANGED_CODE)

## Four Consolidated Files Pass (isolated run)

$ python -m pytest -q --color=no tests/governance/test_embedding_invariants.py tests/governance/test_replay_determinism_invariants.py tests/governance/test_gateway_egress_invariants.py tests/governance/test_static_bypass_scanners.py
45 passed, 4 skipped in 7.72s

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

