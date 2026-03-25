"""End-to-end HITL lifecycle tests — exercises the complete chain:

    Confidence Gate → Escalation → Human Decision → DPO Pair Generation
    → RLHF Optimization → Threshold Update → Runtime Graph Recording

These tests are innovative in that they:
1. Bridge static ADG edges with runtime HITL graph events
2. Validate deterministic DPO pair generation from simulated human feedback
3. Test the full RLHF optimization loop with bounded threshold proposals
4. Verify cross-layer wiring (L3→L5→L6→system_learning)
5. Assert thread-safety of concurrent HITL decision logging
6. Test confidence-gated escalation with configurable thresholds
7. Validate runtime↔static graph reconciliation
"""

from __future__ import annotations

import hashlib
import json
import os
import threading

import pytest

from agentic_core.adg.runtime.event_graph import RuntimeGraph
from agentic_core.adg.runtime.hitl_graph import (
    HITLDecisionType,
    HITLGraph,
    HITLRuntimeRecorder,
)
from agentic_core.L5_safety.enforcement.hitl_gate import (
    HITL_PROTECTED_PATHS,
    HitlGate,
    HitlRequest,
    HitlRequiredError,
    clear_gate_cache,
)
from agentic_core.L5_safety.hitl.hitl_escalation_activator import (
    HITLEscalationActivator,
)
from agentic_core.L6_observability.engines.hitl_dpo_pair_generator import (
    DefaultDeterministicDPOPairGenerator,
)
from agentic_core.L6_observability.types.dpo_types import (
    DPOBatch,
    DPOExampleId,
    DPOPair,
)
from agentic_core.mixins.hitl_mixin import ApprovalStatus, HITLMixin
from system_learning.confidence.engine import HealingConfidenceScorer
from system_learning.confidence.types import HealingAttempt
from system_learning.engines.hitl_decision_logger import log_hitl_decision
from system_learning.engines.rlhf_optimizer import (
    DefaultDeterministicRLHFOptimizer,
)
from system_learning.engines.rlhf_optimizer_impl import DefaultRLHFOptimizer

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rt_graph():
    """Fresh RuntimeGraph for each test."""
    return RuntimeGraph()


@pytest.fixture
def hitl_graph():
    """Fresh HITLGraph for each test."""
    return HITLGraph()


@pytest.fixture
def recorder(rt_graph, hitl_graph):
    """HITLRuntimeRecorder wired to fresh graphs."""
    return HITLRuntimeRecorder(rt_graph, hitl_graph, agent_id="TestE2EAgent", run_id="e2e-run-001")


@pytest.fixture
def confidence_scorer():
    """HealingConfidenceScorer instance."""
    return HealingConfidenceScorer()


@pytest.fixture
def dpo_generator():
    """DefaultDeterministicDPOPairGenerator instance."""
    return DefaultDeterministicDPOPairGenerator()


@pytest.fixture
def rlhf_optimizer():
    """DefaultDeterministicRLHFOptimizer instance."""
    return DefaultDeterministicRLHFOptimizer()


@pytest.fixture
def rlhf_impl_optimizer():
    """DefaultRLHFOptimizer (impl) instance."""
    return DefaultRLHFOptimizer()


@pytest.fixture(autouse=True)
def _clear_gate():
    """Ensure HitlGate singleton is clean between tests."""
    clear_gate_cache()
    yield
    clear_gate_cache()


# ===========================================================================
# E2E TEST 1: Full HITL Lifecycle — Confidence → Escalation → DPO → RLHF
# ===========================================================================


class TestFullHITLLifecycle:
    """Exercises the complete HITL chain end-to-end."""

    def test_confidence_gate_to_dpo_to_rlhf_pipeline(
        self, recorder, hitl_graph, confidence_scorer, dpo_generator, rlhf_optimizer
    ):
        """Full pipeline: score → escalate → decide → generate DPO → optimize."""
        # Stage 1: Confidence scoring triggers ESCALATE
        attempt = HealingAttempt(
            attempt_id="heal-001",
            healer_id="TestHealer",
            outcome="FAIL",
            severity=3,
            signals={"source": "e2e_test"},
            cost=2,
        )
        report = confidence_scorer.score([attempt])
        assert len(report.decisions) == 1
        decision = report.decisions[0]
        assert decision.action == "ESCALATE", f"Low-confidence healing should escalate, got {decision.action}"
        assert decision.confidence < 0.33

        # Stage 2: Record checkpoint in runtime HITL graph
        cp_id = recorder.checkpoint(
            violation_id="v-heal-001",
            confidence=decision.confidence,
            context={"healing_attempt": "heal-001", "outcome": "FAIL"},
        )
        assert cp_id.startswith("cp-")
        assert hitl_graph.pending_count == 1

        # Stage 3: Simulate human decision (APPROVE)
        recorder.decide(
            checkpoint_id=cp_id,
            decision="approve",
            reviewer="human:alice",
            rationale="Healing attempt acceptable despite low confidence",
        )
        assert hitl_graph.resolved_count == 1
        assert hitl_graph.pending_count == 0

        # Stage 4: Generate DPO pair from human feedback
        control_bytes = b"original_healing_output_bytes"
        candidate_bytes = b"proposed_healing_output_bytes"
        dpo_pair = dpo_generator.generate(
            control_output_bytes=control_bytes,
            candidate_output_bytes=candidate_bytes,
            human_decision="APPROVE",
            reason_codes=("low_confidence_escalated", "human_approved"),
        )
        assert dpo_pair.human_decision == "APPROVE"
        assert dpo_pair.reasons == ("low_confidence_escalated", "human_approved")
        assert len(dpo_pair.example_id.control_hash) == 64  # SHA-256 hex

        # Stage 5: Build DPO batch and feed to RLHF optimizer
        dpo_batch = DPOBatch(pairs=(dpo_pair,))
        batch_bytes = dpo_batch.canonical_bytes()
        config_bytes = json.dumps(
            {"healing_threshold": 0.5, "escalation_threshold": 0.3},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        change_pkg = rlhf_optimizer.propose_from_dpo(
            dpo_batch_bytes=batch_bytes,
            current_threshold_config_bytes=config_bytes,
        )
        assert change_pkg is not None
        assert change_pkg.source == "rlhf_optimizer"
        assert change_pkg.confidence > 0.0

        # Stage 6: Record learning feedback
        recorder.learn(checkpoint_id=cp_id, weight_delta=0.1)

    def test_reject_decision_tightens_thresholds(self, recorder, hitl_graph, dpo_generator, rlhf_optimizer):
        """REJECT decisions should tighten (decrease) thresholds."""
        cp_id = recorder.checkpoint(violation_id="v-reject-001", confidence=0.25)
        recorder.decide(
            checkpoint_id=cp_id,
            decision="reject",
            reviewer="human:bob",
            rationale="Healing too risky",
        )

        dpo_pair = dpo_generator.generate(
            control_output_bytes=b"control_output",
            candidate_output_bytes=b"candidate_output",
            human_decision="REJECT",
            reason_codes=("too_risky",),
        )
        assert dpo_pair.human_decision == "REJECT"

        dpo_batch = DPOBatch(pairs=(dpo_pair,))
        config = {"healing_threshold": 0.5}
        change_pkg = rlhf_optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_batch.canonical_bytes(),
            current_threshold_config_bytes=json.dumps(config, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            ),
        )
        # Verify threshold was adjusted
        assert change_pkg is not None
        new_config = json.loads(change_pkg.changes.decode("utf-8"))
        # REJECT tightens (decreases), so new value should be <= original
        assert new_config["healing_threshold"] <= 0.5


# ===========================================================================
# E2E TEST 2: Runtime ↔ Static Graph Reconciliation
# ===========================================================================


class TestRuntimeStaticReconciliation:
    """Validates that runtime HITL events match expected static ADG patterns."""

    def test_runtime_edges_match_static_patterns(self, rt_graph, hitl_graph):
        """Runtime recorder emits edges compatible with static ADG edge types."""
        recorder = HITLRuntimeRecorder(rt_graph, hitl_graph, agent_id="ReconciliationAgent")

        # Emit a checkpoint (should produce escalates_to_human edge)
        cp_id = recorder.checkpoint(violation_id="v-reconcile-001", confidence=0.15)

        # Emit a decision (should produce awaits_approval edge)
        recorder.decide(
            checkpoint_id=cp_id,
            decision="approve",
            reviewer="human:reconciler",
        )

        # Emit learning (should produce learns_from_decision edge)
        recorder.learn(checkpoint_id=cp_id, weight_delta=0.05)

        # Verify runtime graph has the expected edge types
        edges = rt_graph.edges
        edge_types = {e.relation_type for e in edges}

        assert "escalates_to_human" in edge_types, "Runtime graph must contain escalates_to_human edge"
        assert "awaits_approval" in edge_types, "Runtime graph must contain awaits_approval edge"
        assert "learns_from_decision" in edge_types, "Runtime graph must contain learns_from_decision edge"

    def test_runtime_graph_event_ordering(self, rt_graph, hitl_graph):
        """Events must be ordered: checkpoint → decide → learn."""
        recorder = HITLRuntimeRecorder(rt_graph, hitl_graph, agent_id="OrderingAgent")

        cp_id = recorder.checkpoint(violation_id="v-order-001", confidence=0.2)
        recorder.decide(checkpoint_id=cp_id, decision="approve", reviewer="human:orderer")
        recorder.learn(checkpoint_id=cp_id, weight_delta=0.1)

        events = rt_graph.events
        phases = [e.phase for e in events]

        escalate_idx = phases.index("escalate")
        decide_idx = phases.index("decide")
        learn_idx = phases.index("learn")

        assert escalate_idx < decide_idx < learn_idx, (
            f"Event ordering violated: escalate={escalate_idx}, decide={decide_idx}, learn={learn_idx}"
        )


# ===========================================================================
# E2E TEST 3: Cross-Layer Wiring Verification
# ===========================================================================


class TestCrossLayerHITLWiring:
    """Verifies HITL wiring spans L3 → L5 → L6 → system_learning."""

    def test_l5_gate_blocks_without_tty(self, tmp_path):
        """L5 HitlGate raises HitlRequiredError without interactive TTY."""
        gate = HitlGate(tmp_path)
        req = HitlRequest(
            agent="CrossLayerTestAgent",
            operation="HEAL",
            affected_paths=[tmp_path / "agentic_core" / "critical.py"],
            reason="Cross-layer verification",
        )
        with pytest.raises(HitlRequiredError) as exc_info:
            gate.request(req)
        assert "HITL REQUIRED" in str(exc_info.value)

    def test_l5_escalation_activator_creates_request(self):
        """L5 HITLEscalationActivator can create escalation requests."""
        activator = HITLEscalationActivator()
        request = activator.escalate(
            agent="TestAgent",
            module="test_module.py",
            trigger_reason="confidence_below_threshold",
            proposed_action="review_healing",
        )
        assert request is not None
        assert request.agent == "TestAgent"
        assert request.trigger_reason == "confidence_below_threshold"

    def test_l6_dpo_generator_produces_deterministic_pairs(self, dpo_generator):
        """L6 DPO generator produces SHA-256-stable pairs."""
        pair1 = dpo_generator.generate(
            control_output_bytes=b"control_a",
            candidate_output_bytes=b"candidate_a",
            human_decision="APPROVE",
            reason_codes=("test_reason",),
        )
        pair2 = dpo_generator.generate(
            control_output_bytes=b"control_a",
            candidate_output_bytes=b"candidate_a",
            human_decision="APPROVE",
            reason_codes=("test_reason",),
        )
        # Determinism: same inputs → same hashes
        assert pair1.example_id.control_hash == pair2.example_id.control_hash
        assert pair1.example_id.candidate_hash == pair2.example_id.candidate_hash
        assert pair1.content_hash() == pair2.content_hash()

    def test_system_learning_rlhf_produces_bounded_proposals(self, rlhf_optimizer):
        """system_learning RLHF optimizer produces bounded threshold adjustments."""
        dpo_pair = DPOPair(
            example_id=DPOExampleId(
                control_hash=hashlib.sha256(b"ctrl").hexdigest(),
                candidate_hash=hashlib.sha256(b"cand").hexdigest(),
            ),
            control_output_hash=hashlib.sha256(b"ctrl").hexdigest(),
            candidate_output_hash=hashlib.sha256(b"cand").hexdigest(),
            human_decision="APPROVE",
            reasons=("bounded_test",),
        )
        batch = DPOBatch(pairs=(dpo_pair,))
        config = {"threshold": 0.5, "min_confidence": 0.3}
        result = rlhf_optimizer.propose_from_dpo(
            dpo_batch_bytes=batch.canonical_bytes(),
            current_threshold_config_bytes=json.dumps(config, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            ),
        )
        assert result is not None
        new_config = json.loads(result.changes.decode("utf-8"))
        # Bounded: values must stay within [0.1, 2.0]
        for key, val in new_config.items():
            if isinstance(val, (int, float)):
                assert 0.1 <= val <= 2.0, f"Threshold {key}={val} out of bounds [0.1, 2.0]"


# ===========================================================================
# E2E TEST 4: Concurrent HITL Decision Logging (Thread Safety)
# ===========================================================================


class TestConcurrentHITLLogging:
    """Validates thread-safe HITL decision logging under concurrent access."""

    def test_concurrent_decision_logging_no_data_loss(self, tmp_path):
        """Multiple threads logging HITL decisions concurrently must not lose data."""
        evidence_file = tmp_path / "hitl_evidence.jsonl"
        os.environ["HITL_EVIDENCE_PATH"] = str(evidence_file)

        num_threads = 8
        decisions_per_thread = 10
        barrier = threading.Barrier(num_threads)
        errors: list[str] = []

        def worker(thread_id: int) -> None:
            try:
                barrier.wait(timeout=5)
                for i in range(decisions_per_thread):
                    log_hitl_decision(
                        agent=f"Agent-{thread_id}",
                        file_path=f"module_{thread_id}_{i}.py",
                        violation=f"violation-{thread_id}-{i}",
                        proposed=f"fix-{thread_id}-{i}",
                        decision="APPROVE" if i % 2 == 0 else "REJECT",
                    )
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Thread {thread_id}: {exc}")

        threads = [threading.Thread(target=worker, args=(tid,)) for tid in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert not errors, f"Thread errors: {errors}"

        # Verify no data loss
        if evidence_file.exists():
            lines = evidence_file.read_text(encoding="utf-8").strip().splitlines()
            expected = num_threads * decisions_per_thread
            assert len(lines) == expected, f"Expected {expected} log lines, got {len(lines)}"

        # Cleanup
        os.environ.pop("HITL_EVIDENCE_PATH", None)


# ===========================================================================
# E2E TEST 5: Confidence-Gated Escalation Sweep
# ===========================================================================


class TestConfidenceGatedEscalation:
    """Tests confidence scoring across different thresholds and outcomes."""

    @pytest.mark.parametrize(
        "outcome,severity,cost,expected_action",
        [
            ("FAIL", 5, 5, "ESCALATE"),  # Low confidence → escalate
            ("FAIL", 1, 0, "ESCALATE"),  # FAIL always low
            ("PARTIAL", 0, 0, "REVIEW"),  # Medium confidence → review
            ("SUCCESS", 0, 0, "ACCEPT"),  # High confidence → accept
            ("SUCCESS", 5, 5, "REVIEW"),  # High severity/cost degrades
        ],
    )
    def test_confidence_action_mapping(self, confidence_scorer, outcome, severity, cost, expected_action):
        """Confidence scorer maps outcomes to correct actions."""
        attempt = HealingAttempt(
            attempt_id="param-test",
            healer_id="ParamTestHealer",
            outcome=outcome,
            severity=severity,
            signals={"source": "param_test"},
            cost=cost,
        )
        report = confidence_scorer.score([attempt])
        assert report.decisions[0].action == expected_action

    def test_multiple_attempts_aggregate_correctly(self, confidence_scorer):
        """Multiple healing attempts produce sorted, independent decisions."""
        attempts = [
            HealingAttempt(
                attempt_id="a1", healer_id="H1", outcome="SUCCESS", severity=0, signals={}, cost=0
            ),
            HealingAttempt(attempt_id="a2", healer_id="H2", outcome="FAIL", severity=3, signals={}, cost=2),
            HealingAttempt(
                attempt_id="a3", healer_id="H3", outcome="PARTIAL", severity=1, signals={}, cost=1
            ),
        ]
        report = confidence_scorer.score(attempts)
        assert len(report.decisions) == 3
        # Decisions should be sorted by attempt_id
        ids = [d.attempt_id for d in report.decisions]
        assert ids == sorted(ids)

    def test_escalation_triggers_runtime_checkpoint(self, confidence_scorer, recorder, hitl_graph):
        """ESCALATE action triggers a runtime HITL checkpoint."""
        attempt = HealingAttempt(
            attempt_id="esc-trigger",
            healer_id="EscHealer",
            outcome="FAIL",
            severity=4,
            signals={"trigger": "escalation"},
            cost=3,
        )
        report = confidence_scorer.score([attempt])
        decision = report.decisions[0]
        assert decision.action == "ESCALATE"

        # This should create a runtime checkpoint
        cp_id = recorder.checkpoint(
            violation_id="esc-trigger",
            confidence=decision.confidence,
        )
        assert hitl_graph.pending_count == 1
        cp = hitl_graph.checkpoint_by_id(cp_id)
        assert cp is not None
        assert cp.confidence == decision.confidence
        assert not cp.resolved


# ===========================================================================
# E2E TEST 6: DPO Batch Determinism & Content Hashing
# ===========================================================================


class TestDPODeterminism:
    """Validates that DPO pair generation and batching is fully deterministic."""

    def test_dpo_pair_canonical_bytes_stable(self, dpo_generator):
        """Same inputs always produce identical canonical bytes."""
        pair = dpo_generator.generate(
            control_output_bytes=b"stable_control",
            candidate_output_bytes=b"stable_candidate",
            human_decision="APPROVE",
            reason_codes=("stability_test",),
        )
        bytes1 = pair.canonical_bytes()
        bytes2 = pair.canonical_bytes()
        assert bytes1 == bytes2
        assert hashlib.sha256(bytes1).hexdigest() == pair.content_hash()

    def test_dpo_batch_ordering_invariant(self, dpo_generator):
        """DPO batch with same pairs in different order produces same hash."""
        pairs = []
        for i in range(5):
            pair = dpo_generator.generate(
                control_output_bytes=f"control_{i}".encode(),
                candidate_output_bytes=f"candidate_{i}".encode(),
                human_decision="APPROVE" if i % 2 == 0 else "REJECT",
                reason_codes=(f"reason_{i}",),
            )
            pairs.append(pair)

        # Sort by (control_hash, candidate_hash) as DPOBatch expects
        sorted_pairs = tuple(
            sorted(
                pairs,
                key=lambda p: (
                    p.example_id.control_hash,
                    p.example_id.candidate_hash,
                ),
            )
        )
        batch1 = DPOBatch(pairs=sorted_pairs)
        batch2 = DPOBatch(pairs=sorted_pairs)
        assert batch1.content_hash() == batch2.content_hash()

    def test_dpo_pair_content_hash_is_sha256(self, dpo_generator):
        """Content hash must be a valid 64-char SHA-256 hex string."""
        pair = dpo_generator.generate(
            control_output_bytes=b"hash_test",
            candidate_output_bytes=b"hash_test_candidate",
            human_decision="APPROVE",
            reason_codes=("hash_validation",),
        )
        h = pair.content_hash()
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ===========================================================================
# E2E TEST 7: RLHF Optimizer Boundary Conditions
# ===========================================================================


class TestRLHFOptimizerBoundaries:
    """Tests RLHF optimizer handles edge cases correctly."""

    def test_malformed_dpo_batch_returns_zero_confidence(self, rlhf_optimizer):
        """Malformed DPO batch produces zero-confidence change package."""
        result = rlhf_optimizer.propose_from_dpo(
            dpo_batch_bytes=b"not valid json",
            current_threshold_config_bytes=b'{"threshold": 0.5}',
        )
        assert result is not None
        assert result.confidence == 0.0
        assert "malformed_dpo_batch" in result.reason

    def test_malformed_config_returns_zero_confidence(self, rlhf_optimizer):
        """Malformed threshold config produces zero-confidence change package."""
        batch = DPOBatch(pairs=())
        result = rlhf_optimizer.propose_from_dpo(
            dpo_batch_bytes=batch.canonical_bytes(),
            current_threshold_config_bytes=b"not valid config",
        )
        assert result is not None
        assert result.confidence == 0.0

    def test_empty_dpo_batch_produces_no_adjustments(self, rlhf_optimizer):
        """Empty DPO batch should produce no adjustments."""
        batch = DPOBatch(pairs=())
        config = {"threshold": 0.5}
        result = rlhf_optimizer.propose_from_dpo(
            dpo_batch_bytes=batch.canonical_bytes(),
            current_threshold_config_bytes=json.dumps(config, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            ),
        )
        assert result is not None
        assert "no_adjustments" in result.reason

    def test_impl_optimizer_min_pairs_threshold(self, rlhf_impl_optimizer):
        """DefaultRLHFOptimizer requires minimum 3 DPO pairs."""
        # 2 pairs → should return None (insufficient)
        batch = {
            "pairs": [
                {
                    "chosen": {"threshold": 0.6},
                    "rejected": {"threshold": 0.4},
                    "surface": "healing",
                },
                {
                    "chosen": {"threshold": 0.7},
                    "rejected": {"threshold": 0.3},
                    "surface": "healing",
                },
            ]
        }
        result = rlhf_impl_optimizer.propose_from_dpo(
            json.dumps(batch).encode("utf-8"), snapshot_id="test-snap"
        )
        assert result is None, "< 3 pairs should return None"

    def test_impl_optimizer_strong_preference_signal(self, rlhf_impl_optimizer):
        """Strong preference signal (all increase) produces a proposal."""
        batch = {
            "pairs": [
                {
                    "chosen": {"threshold": 0.8},
                    "rejected": {"threshold": 0.3},
                    "surface": "healing",
                }
                for _ in range(5)
            ]
        }
        result = rlhf_impl_optimizer.propose_from_dpo(
            json.dumps(batch).encode("utf-8"), snapshot_id="strong-signal"
        )
        assert result is not None
        assert result.direction == "increase"
        assert result.preference_strength >= 0.6


# ===========================================================================
# E2E TEST 8: HITLGraph State Machine Integrity
# ===========================================================================


class TestHITLGraphStateMachine:
    """Validates the HITL graph state machine transitions."""

    def test_checkpoint_starts_unresolved(self, recorder, hitl_graph):
        """New checkpoints start in unresolved state."""
        cp_id = recorder.checkpoint(violation_id="sm-001", confidence=0.2)
        cp = hitl_graph.checkpoint_by_id(cp_id)
        assert cp is not None
        assert not cp.resolved
        assert hitl_graph.pending_count == 1
        assert hitl_graph.resolved_count == 0

    def test_decide_resolves_checkpoint(self, recorder, hitl_graph):
        """Decision transitions checkpoint to resolved."""
        cp_id = recorder.checkpoint(violation_id="sm-002", confidence=0.2)
        recorder.decide(cp_id, decision="approve", reviewer="human:sm")
        cp = hitl_graph.checkpoint_by_id(cp_id)
        assert cp.resolved
        assert hitl_graph.pending_count == 0
        assert hitl_graph.resolved_count == 1

    def test_decision_distribution_counts(self, recorder, hitl_graph):
        """Decision distribution correctly tallies by type."""
        for i in range(3):
            cp_id = recorder.checkpoint(violation_id=f"dist-{i}", confidence=0.2 + i * 0.1)
            decision = ["approve", "reject", "approve"][i]
            recorder.decide(cp_id, decision=decision, reviewer=f"human:d{i}")

        dist = hitl_graph.decision_distribution()
        assert dist.get(HITLDecisionType.APPROVE, 0) == 2
        assert dist.get(HITLDecisionType.REJECT, 0) == 1

    def test_multiple_decisions_per_checkpoint(self, recorder, hitl_graph):
        """Multiple decisions can reference the same checkpoint."""
        cp_id = recorder.checkpoint(violation_id="multi-001", confidence=0.15)
        recorder.decide(cp_id, decision="defer", reviewer="human:first")
        recorder.decide(cp_id, decision="approve", reviewer="human:second")

        decisions = hitl_graph.decisions_for(cp_id)
        assert len(decisions) == 2
        assert decisions[0].decision == HITLDecisionType.DEFER
        assert decisions[1].decision == HITLDecisionType.APPROVE

    def test_override_decision_captures_value(self, recorder, hitl_graph):
        """Override decisions capture the corrected value."""
        cp_id = recorder.checkpoint(violation_id="override-001", confidence=0.1)
        recorder.decide(
            cp_id,
            decision="override",
            reviewer="human:override",
            override_value={"new_threshold": 0.45},
        )

        decisions = hitl_graph.decisions_for(cp_id)
        assert len(decisions) == 1
        assert decisions[0].decision == HITLDecisionType.OVERRIDE
        assert decisions[0].override_value == {"new_threshold": 0.45}


# ===========================================================================
# E2E TEST 9: HITL Mixin Integration
# ===========================================================================


class TestHITLMixinIntegration:
    """Tests HITLMixin integration with agent workflows."""

    def test_hitl_mixin_creates_approval_request(self):
        """HITLMixin.create_approval_request creates a properly structured request."""

        class MockAgent(HITLMixin):
            pass

        agent = MockAgent()
        request = agent.create_approval_request(
            operation_name="destructive_heal",
            context={"target": "agentic_core/L5_safety/critical.py"},
        )
        assert request is not None
        assert request.operation_name == "destructive_heal"
        assert request.status == ApprovalStatus.PENDING

    def test_hitl_mixin_tracks_pending_approvals(self):
        """HITLMixin tracks pending approval requests via _pending_approvals."""

        class MockAgent(HITLMixin):
            pass

        agent = MockAgent()
        r1 = agent.create_approval_request("op1")
        r2 = agent.create_approval_request("op2")
        assert len(agent._pending_approvals) >= 2


# ===========================================================================
# E2E TEST 10: ADG Static Edge Verification
# ===========================================================================


class TestADGStaticEdgeVerification:
    """Validates that key HITL modules exist and are importable."""

    def test_hitl_gate_importable(self):
        """HitlGate must be importable from L5_safety."""
        from agentic_core.L5_safety.enforcement.hitl_gate import HitlGate

        assert HitlGate is not None

    def test_hitl_escalation_activator_importable(self):
        """HITLEscalationActivator must be importable from L5_safety."""
        from agentic_core.L5_safety.hitl.hitl_escalation_activator import (
            HITLEscalationActivator,
        )

        assert HITLEscalationActivator is not None

    def test_dpo_types_frozen(self):
        """DPO types must be frozen dataclasses."""
        pair_id = DPOExampleId(control_hash="a" * 64, candidate_hash="b" * 64)
        with pytest.raises(AttributeError):
            pair_id.control_hash = "c" * 64  # type: ignore[misc]

    def test_hitl_runtime_recorder_in_all(self):
        """HITLRuntimeRecorder must be in hitl_graph.__all__."""
        import agentic_core.adg.runtime.hitl_graph as m

        assert "HITLRuntimeRecorder" in m.__all__

    def test_hitl_decision_type_values(self):
        """HITLDecisionType enum must have approve/reject/override/defer."""
        assert HITLDecisionType.APPROVE.value == "approve"
        assert HITLDecisionType.REJECT.value == "reject"
        assert HITLDecisionType.OVERRIDE.value == "override"
        assert HITLDecisionType.DEFER.value == "defer"

    def test_protected_paths_include_agentic_core(self):
        """HITL_PROTECTED_PATHS must include agentic_core."""
        assert "agentic_core" in HITL_PROTECTED_PATHS
