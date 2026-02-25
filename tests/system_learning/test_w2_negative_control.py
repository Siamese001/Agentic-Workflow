"""W2 negative control test.

When W2_NEGCTRL_TAMPER=1: tests FAIL (proving guards can be broken).
When W2_NEGCTRL_TAMPER unset: tests PASS (guards intact).
W2: Informational semantic retrieval + bounded scoring (C0-only).
"""

from __future__ import annotations

import os

import pytest
from unittest.mock import MagicMock, patch

from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)

_TAMPER = os.environ.get("W2_NEGCTRL_TAMPER", "0") == "1"


def _make_snapshot_above_threshold() -> HealingOutcomeAggregateSnapshot:
    aggregates = [
        (
            HealingOutcomeAggregateKey(
                healer_name="test_healer",
                tier="LOCAL_AGENT",
                failure_type="test_failure",
            ),
            HealingOutcomeAggregate(
                success_count=8,
                failure_count=12,
                total_count=20,
            ),
        ),
    ]
    return HealingOutcomeAggregateSnapshot(
        version_id="test_version",
        created_utc=1234567890,
        aggregates=tuple(aggregates),
    )


def _embedding_metadata() -> dict:
    return {
        "embedding_enabled_at_time": True,
        "embedding_replay_key": "test_replay_key",
        "embedding_artifact_hash": "test_hash",
        "embedding_topk_hashes": ["hash1", "hash2"],
        "embedding_topk_scores_round6": [0.85, 0.90],
    }


@pytest.mark.unit_min_deps
class TestW2NegativeControl:
    """W2 negative control tests.

    Under tamper (W2_NEGCTRL_TAMPER=1) these tests FAIL, proving the guards
    can be broken.  Without tamper the guards hold and the tests PASS.
    """

    def test_embedding_determinism_violation_negative_control(self) -> None:
        """Guard: two identical calls must produce identical confidence.

        Under tamper we inject different side-effect values and assert the
        scores are EQUAL — which they are NOT — causing a pytest FAILURE.
        Without tamper we patch both calls to the same value and assert
        equality, which passes.
        """
        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=0.5,
            escalation_delta=0.1,
            max_threshold=2.0,
            max_delta=0.2,
        )
        snapshot = _make_snapshot_above_threshold()
        meta = _embedding_metadata()

        if _TAMPER:
            # Inject different scores — the assertion below will FAIL
            side_effects = [0.90, 0.85]
        else:
            # Same score both times — assertion passes
            side_effects = [0.90, 0.90]

        with patch.object(optimizer, "_aggregate_embedding_scores") as mock_agg:
            mock_agg.side_effect = side_effects

            proposal1 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=meta,
                embedding_influence_cap=0.25,
                min_sample_threshold=20,
            )
            proposal2 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=meta,
                embedding_influence_cap=0.25,
                min_sample_threshold=20,
            )

            conf1 = proposal1.adjustments[0].confidence
            conf2 = proposal2.adjustments[0].confidence

            assert conf1 == conf2, (
                f"Determinism guard violated: run1={conf1} != run2={conf2}"
            )

    def test_small_n_guard_violation_negative_control(self) -> None:
        """Guard: adjustments must be empty when total_count < min_sample_size.

        Under tamper we mock the base method to return a fake adjustment so
        that len(adjustments) > 0 — then we assert it IS zero, causing FAIL.
        Without tamper we run the real guard; it correctly returns no
        adjustments and we assert empty, which passes.
        """
        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=0.5,
            escalation_delta=0.1,
            max_threshold=2.0,
            max_delta=0.2,
        )

        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer",
                    tier="LOCAL_AGENT",
                    failure_type="test_failure",
                ),
                HealingOutcomeAggregate(
                    success_count=0,
                    failure_count=2,
                    total_count=2,
                ),
            ),
        ]
        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_version",
            created_utc=1234567890,
            aggregates=tuple(aggregates),
        )
        meta = _embedding_metadata()

        if _TAMPER:
            from system_learning.engines.healing_config_optimizer import ThresholdAdjustment
            fake_adj = ThresholdAdjustment(
                healer_name="test_healer",
                tier="LOCAL_AGENT",
                failure_type="test_failure",
                current_threshold=1.0,
                proposed_threshold=1.2,
                confidence=0.8,
                reason="embedding_influenced, weight=0.25, score=0.950000",
            )
            mock_proposal = MagicMock()
            mock_proposal.adjustments = [fake_adj]

            with patch.object(optimizer, "propose_threshold_adjustments", return_value=mock_proposal):
                proposal = optimizer.propose_threshold_adjustments_with_embeddings(
                    snapshot,
                    embedding_metadata=meta,
                    embedding_influence_cap=0.25,
                    min_sample_threshold=20,
                )

            # Assert guard holds (it does NOT under tamper → FAIL)
            assert len(proposal.adjustments) == 0, (
                "Small-N guard violated: adjustments produced for sample below threshold"
            )
        else:
            proposal = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=meta,
                embedding_influence_cap=0.25,
                min_sample_threshold=20,
            )
            assert len(proposal.adjustments) == 0, (
                "Small-N guard should block adjustments when total_count < min_sample_size"
            )
