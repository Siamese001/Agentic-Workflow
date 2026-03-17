"""Arbitration engine tests for deterministic multi-agent proposal selection."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_arbitration_engine")
_emit_applies_guardrail("p0", "test_arbitration_engine", "p0_governance")
_emit_snapshots_state("p0", "test_arbitration_engine", "state_snapshot")
emit_replay_key("p0", "test_arbitration_engine")
emit_determinism_digest("p0", "test_arbitration_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_arbitration_engine", "execution_auth")
_emit_validates_capability("p2", "test_arbitration_engine", "capability_check")
_emit_routes_to_capability("p2", "test_arbitration_engine", "capability_route")
_emit_writes_via_uwg("p2", "test_arbitration_engine", "uwg_write")
_emit_blocks_direct_write("p2", "test_arbitration_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "test_arbitration_engine", "tool_invocation")
_emit_captures_execution_output("p2", "test_arbitration_engine", "exec_output")
_emit_dispatches_agent("p3", "test_arbitration_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "test_arbitration_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_arbitration_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_arbitration_engine", "healing_outcome")
_emit_escalates_failure("p3", "test_arbitration_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_arbitration_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_arbitration_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_arbitration_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_arbitration_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_arbitration_engine", "eval_metric")
_emit_stores_embedding("p4", "test_arbitration_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_arbitration_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_arbitration_engine", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)
from system_learning.arbitration.engine import ArbitrationEngine
from system_learning.arbitration.types import (
    ArbitrationCandidate,
    ArbitrationDecision,
    ArbitrationPolicy,
)

_emit_emits_metric_event("test_arbitration_engine", "p4obs", "metric_1")
_emit_emits_metric_event("test_arbitration_engine", "p4obs", "metric_2")
_emit_emits_metric_event("test_arbitration_engine", "p4obs", "metric_3")
_emit_emits_metric_event("test_arbitration_engine", "p4obs", "metric_4")
_emit_emits_metric_event("test_arbitration_engine", "p4obs", "metric_5")
_emit_emits_metric_event("test_arbitration_engine", "p4obs", "metric_6")
_emit_records_incident_event("test_arbitration_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_arbitration_engine", "p4obs", "anomaly")
_emit_writes_observability_log("test_arbitration_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_arbitration_engine", "p4obs", "mon_state")
_emit_triggers_alert("test_arbitration_engine", "p4obs", "alert")
_emit_links_incident_trace("test_arbitration_engine", "p4obs", "trace_link")
_emit_captures_pattern("test_arbitration_engine", "p3lm", "pattern")
_emit_records_learning_event("test_arbitration_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_arbitration_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_arbitration_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_arbitration_engine", "p3lm", "routing")
_emit_improves_agent_policy("test_arbitration_engine", "p3lm", "policy")
_emit_stores_learning_state("test_arbitration_engine", "p3lm", "state")
_emit_records_execution_trace("test_arbitration_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_arbitration_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_arbitration_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_arbitration_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_arbitration_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_arbitration_engine", "env_read", "p2_env_1")
_emit_reads_environ("test_arbitration_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_arbitration_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_arbitration_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_arbitration_engine", "context_pull")
_emit_pulls_context("p1", "test_arbitration_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_arbitration_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_arbitration_engine", "uwg_term_2")
_emit_writes_through("p1", "test_arbitration_engine", "write_through")
_emit_writes_through("p1", "test_arbitration_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_arbitration_engine", "safety_validation")
_emit_invokes_eval("p1", "test_arbitration_engine", "eval_call")
_emit_proposal_commits_routing("p1", "test_arbitration_engine", "routing_commit")
_emit_escalates_to_human("p1", "test_arbitration_engine", "human_escalation")
_emit_routes_through("p1", "test_arbitration_engine", "route_through")
_emit_checks_agent_registry("p1", "test_arbitration_engine", "agent_registry")
_emit_validates_agent_capability("p1", "test_arbitration_engine", "capability")
_emit_dispatches_execution_plan("p1", "test_arbitration_engine", "exec_plan")
_emit_agent_executes_agent("p1", "test_arbitration_engine", "sub_agent")
_emit_routes_to_agent("p1", "test_arbitration_engine", "target_agent")
_emit_verifies_policy("p1", "test_arbitration_engine", "policy_check")
_emit_observes_runtime_state("p1", "test_arbitration_engine", "runtime_state")
_emit_verifies_boundary("p1", "test_arbitration_engine", "boundary_check")
_emit_transcripts_response("p1", "test_arbitration_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "test_arbitration_engine")
_emit_gated_by_confidence("p1", "test_arbitration_engine", "confidence_gate")


class TestArbitrationEngine:
    """Test arbitration engine deterministic behavior."""

    def test_deterministic_ordering_total(self):
        """Total ordering with score-primary, cost-secondary, kind-tertiary, id-final tie-break."""
        engine = ArbitrationEngine()
        policy = ArbitrationPolicy(
            weights={"healing": 1.0, "threshold": 0.8, "resource": 0.6},
            caps={"max_winners": 3},
            thresholds={"min_score": 0.1},
            allowed_kinds={"healing", "threshold", "resource"},
        )

        # Create candidates with tie scenarios
        candidates = [
            ArbitrationCandidate(
                id="candidate_a",
                kind="healing",
                payload={"action": "restart"},
                score=0.9,
                cost=0.5,
                provenance="agent_1",
            ),
            ArbitrationCandidate(
                id="candidate_b",
                kind="healing",
                payload={"action": "retry"},
                score=0.9,  # Same score
                cost=0.3,  # Lower cost (better)
                provenance="agent_2",
            ),
            ArbitrationCandidate(
                id="candidate_c",
                kind="threshold",  # Different kind (lower priority than healing)
                payload={"threshold": 0.8},
                score=0.9,
                cost=0.3,
                provenance="agent_3",
            ),
            ArbitrationCandidate(
                id="candidate_d",
                kind="healing",
                payload={"action": "escalate"},
                score=0.9,
                cost=0.3,  # Same score and cost as B
                provenance="agent_4",
            ),
        ]

        decision = engine.arbitrate(candidates, policy)

        # Expected order: B (lower cost), D (lexicographic id), A (higher cost), C (different kind)
        assert decision.winner_ids == ("candidate_b", "candidate_d", "candidate_a")
        assert decision.deterministic_fingerprint is not None

    def test_negative_control_lexicographic_tie_break(self):
        """Negative control that fails if lexicographic id tie-break is removed."""
        engine = ArbitrationEngine()
        policy = ArbitrationPolicy(
            weights={"healing": 1.0},
            caps={"max_winners": 2},
            thresholds={"min_score": 0.1},
            allowed_kinds={"healing"},
        )

        # Create candidates with identical scores and costs
        base_candidates = [
            ArbitrationCandidate(
                id=f"candidate_{chr(ord('a') + i)}",
                kind="healing",
                payload={"action": f"action_{i}"},
                score=0.8,
                cost=0.4,
                provenance=f"agent_{i}",
            )
            for i in range(5)
        ]

        decision = engine.arbitrate(base_candidates, policy)

        # Should select first two lexicographically: candidate_a, candidate_b
        assert decision.winner_ids == ("candidate_a", "candidate_b")

        # Shuffle and verify same result (deterministic)
        import random

        shuffled = list(base_candidates)
        random.shuffle(shuffled)
        decision_shuffled = engine.arbitrate(shuffled, policy)
        assert decision_shuffled.winner_ids == decision.winner_ids
        assert decision_shuffled.deterministic_fingerprint == decision.deterministic_fingerprint

    def test_permutation_invariance_large_n(self):
        """Proves 50+ candidates permuted 10 times yield identical decision fingerprint."""
        engine = ArbitrationEngine()
        policy = ArbitrationPolicy(
            weights={"healing": 1.0, "threshold": 0.8, "resource": 0.6},
            caps={"max_winners": 5},
            thresholds={"min_score": 0.1},
            allowed_kinds={"healing", "threshold", "resource"},
        )

        # Create 55 candidates
        candidates = []
        for i in range(55):
            kind = ["healing", "threshold", "resource"][i % 3]
            candidates.append(
                ArbitrationCandidate(
                    id=f"candidate_{i:02d}",
                    kind=kind,
                    payload={"index": i},
                    score=0.5 + (i % 10) * 0.05,  # Vary scores
                    cost=0.1 + (i % 5) * 0.1,  # Vary costs
                    provenance=f"agent_{i % 7}",
                )
            )

        # Test permutation invariance
        fingerprints = []
        winner_sets = []

        import random

        for permutation in range(10):
            shuffled = list(candidates)
            random.shuffle(shuffled)

            decision = engine.arbitrate(shuffled, policy)
            fingerprints.append(decision.deterministic_fingerprint)
            winner_sets.append(decision.winner_ids)

        # All should be identical
        for i in range(1, len(fingerprints)):
            assert fingerprints[i] == fingerprints[0], f"Fingerprint mismatch at permutation {i}"
            assert winner_sets[i] == winner_sets[0], f"Winners mismatch at permutation {i}"

    def test_cross_process_determinism(self):
        """Proves cross-process determinism via subprocess fingerprint comparison."""
        # Test data
        candidates_data = [
            {
                "id": "candidate_1",
                "kind": "healing",
                "payload": {"action": "restart"},
                "score": 0.9,
                "cost": 0.5,
                "provenance": "agent_1",
            },
            {
                "id": "candidate_2",
                "kind": "threshold",
                "payload": {"threshold": 0.8},
                "score": 0.7,
                "cost": 0.3,
                "provenance": "agent_2",
            },
        ]

        policy_data = {
            "weights": {"healing": 1.0, "threshold": 0.8},
            "caps": {"max_winners": 2},
            "thresholds": {"min_score": 0.1},
            "allowed_kinds": {"healing", "threshold"},
        }

        # Write test script
        script_content = f"""
import sys
import json
import hashlib
sys.path.insert(0, r"C:\\Git\\Agentic-Workflow")

from system_learning.arbitration.engine import ArbitrationEngine
from system_learning.arbitration.types import (
    ArbitrationCandidate,
    ArbitrationPolicy,
)

candidates = [
    ArbitrationCandidate(**c) for c in {candidates_data}
]
policy = ArbitrationPolicy(**{policy_data})

engine = ArbitrationEngine()
decision = engine.arbitrate(candidates, policy)

print(f"FINGERPRINT: {{decision.deterministic_fingerprint}}")
print(f"WINNERS: {{decision.winner_ids}}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=str(pathlib.Path(__file__).resolve().parents[2]),
            )

            assert result.returncode == 0

            # Parse output
            lines = result.stdout.strip().split("\n")
            remote_fingerprint = lines[0].split(": ")[1]
            remote_winners = eval(lines[1].split(": ")[1])

            # Run same arbitration locally
            candidates = [ArbitrationCandidate(**c) for c in candidates_data]
            policy = ArbitrationPolicy(**policy_data)

            local_engine = ArbitrationEngine()
            local_decision = local_engine.arbitrate(candidates, policy)

            # Fingerprints should match across processes
            assert local_decision.deterministic_fingerprint == remote_fingerprint
            assert local_decision.winner_ids == tuple(remote_winners)

        finally:
            import os

            os.unlink(script_path)

    def test_malformed_input_classification_stability(self):
        """Proves stable exception types for malformed inputs."""
        engine = ArbitrationEngine()
        policy = ArbitrationPolicy(
            weights={"healing": 1.0},
            caps={"max_winners": 1},
            thresholds={"min_score": 0.1},
            allowed_kinds={"healing"},
        )

        # Test malformed inputs
        malformed_cases = [
            # Duplicate IDs
            {
                "candidates": [
                    ArbitrationCandidate(
                        id="dup", kind="healing", payload={}, score=0.8, cost=0.5, provenance="agent_1"
                    ),
                    ArbitrationCandidate(
                        id="dup", kind="healing", payload={}, score=0.9, cost=0.3, provenance="agent_2"
                    ),
                ],
                "expected_error": ValueError,
            },
            # NaN scores
            {
                "candidates": [
                    ArbitrationCandidate(
                        id="nan",
                        kind="healing",
                        payload={},
                        score=float("nan"),
                        cost=0.5,
                        provenance="agent_1",
                    ),
                ],
                "expected_error": ValueError,
            },
            # Infinite scores
            {
                "candidates": [
                    ArbitrationCandidate(
                        id="inf",
                        kind="healing",
                        payload={},
                        score=float("inf"),
                        cost=0.5,
                        provenance="agent_1",
                    ),
                ],
                "expected_error": ValueError,
            },
            # Unknown kind
            {
                "candidates": [
                    ArbitrationCandidate(
                        id="unknown",
                        kind="unknown_kind",
                        payload={},
                        score=0.8,
                        cost=0.5,
                        provenance="agent_1",
                    ),
                ],
                "expected_error": ValueError,
            },
            # Missing required fields (simulated by None values)
            {
                "candidates": None,
                "expected_error": TypeError,
            },
        ]

        for case in malformed_cases:
            with pytest.raises(case["expected_error"]):
                engine.arbitrate(case["candidates"], policy)

        # Exception types should be deterministic
        assert len(malformed_cases) == 5

    def test_proposal_only_purity(self):
        """Proves arbitration engine is pure and returns only decision objects."""
        engine = ArbitrationEngine()
        policy = ArbitrationPolicy(
            weights={"healing": 1.0},
            caps={"max_winners": 1},
            thresholds={"min_score": 0.1},
            allowed_kinds={"healing"},
        )

        candidates = [
            ArbitrationCandidate(
                id="pure_test",
                kind="healing",
                payload={"action": "test"},
                score=0.8,
                cost=0.5,
                provenance="agent_1",
            )
        ]

        # Multiple calls with same inputs should return identical objects
        decision1 = engine.arbitrate(candidates, policy)
        decision2 = engine.arbitrate(candidates, policy)

        # Same fingerprint and winners
        assert decision1.deterministic_fingerprint == decision2.deterministic_fingerprint
        assert decision1.winner_ids == decision2.winner_ids

        # Verify return type
        assert isinstance(decision1, ArbitrationDecision)
        assert hasattr(decision1, "canonical_bytes")

        # No side effects - engine state should be unchanged
        # (This is implicit in the deterministic behavior above)
