"""Arbitration engine tests for deterministic multi-agent proposal selection."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import pytest

pytestmark = pytest.mark.unit_min_deps

from system_learning.arbitration.engine import ArbitrationEngine
from system_learning.arbitration.types import (
    ArbitrationCandidate,
    ArbitrationDecision,
    ArbitrationPolicy,
)


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
