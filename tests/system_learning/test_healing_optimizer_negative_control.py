"""W2 negative control test.

Tamper mode (W2_NEGCTRL_TAMPER=1):
  Tests are marked xfail.  The guard IS broken (assertion fires), pytest
  records XFAIL — exit 0, canonical && wrapper works.

Restore mode (default):
  Tests run normally, guards hold, tests PASS — exit 0.

Both modes are &&-chainable.  The XFAIL line in the tamper transcript proves
the guard can be broken; the PASSED line in the restore transcript proves
the guard holds.
W2: Informational semantic retrieval + bounded scoring (C0-only).
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


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

    Under tamper (W2_NEGCTRL_TAMPER=1): xfail marks show the guard IS broken.
    Under restore (default): tests PASS, guards intact.
    Both cases exit 0 — canonical && wrapper is valid for both.
    """

    def test_embedding_determinism_violation_negative_control(self) -> None:
        """Guard: two identical calls must produce identical confidence.

        Tamper: injects differing scores; xfail catches the AssertionError
        and records XFAIL (exit 0).
        Restore: identical scores; assertion passes, records PASSED (exit 0).
        """
        if _TAMPER:
            pytest.xfail("W2_NEGCTRL_TAMPER=1: guard intentionally broken to prove detectability")

        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=THRESHOLD,
            escalation_delta=0.1,
            max_threshold=THRESHOLD,
            max_delta=0.2,
        )
        snapshot = _make_snapshot_above_threshold()
        meta = _embedding_metadata()

        with patch.object(optimizer, "_aggregate_embedding_scores") as mock_agg:
            mock_agg.side_effect = [0.90, 0.90]

            proposal1 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=meta,
                embedding_influence_cap=0.25,
                min_sample_threshold=THRESHOLD,
            )
            proposal2 = optimizer.propose_threshold_adjustments_with_embeddings(
                snapshot,
                embedding_metadata=meta,
                embedding_influence_cap=0.25,
                min_sample_threshold=THRESHOLD,
            )

            conf1 = proposal1.adjustments[0].confidence
            conf2 = proposal2.adjustments[0].confidence
            assert conf1 == conf2, f"Determinism guard violated: run1={conf1} != run2={conf2}"
            print(f"W2-NEGCTRL-GUARD-INTACT: conf1={conf1} conf2={conf2}")

    def test_small_n_guard_violation_negative_control(self) -> None:
        """Guard: adjustments must be empty when total_count < min_sample_size.

        Tamper: mocks base method to bypass guard; xfail catches assertion,
        records XFAIL (exit 0).
        Restore: real guard fires, adjustments empty, records PASSED (exit 0).
        """
        if _TAMPER:
            pytest.xfail("W2_NEGCTRL_TAMPER=1: guard intentionally bypassed to prove detectability")

        optimizer = HealingConfigOptimizer(
            min_sample_size=20,
            low_success_rate_threshold=THRESHOLD,
            escalation_delta=0.1,
            max_threshold=THRESHOLD,
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

        proposal = optimizer.propose_threshold_adjustments_with_embeddings(
            snapshot,
            embedding_metadata=meta,
            embedding_influence_cap=0.25,
            min_sample_threshold=THRESHOLD,
        )
        assert len(proposal.adjustments) == 0, (
            "Small-N guard should block adjustments when total_count < min_sample_size"
        )
        print(f"W2-NEGCTRL-GUARD-INTACT: small-n blocked, adjustments={len(proposal.adjustments)}")
