"""Golden trace tests for offline replay — Wave 7.0.13.

Validates:
  a) Deterministic replay bundle: identical inputs produce byte-identical JSON.
  b) Drift detection: changing a single event metric_value changes downstream trace_ids.
  c) Fail-closed path: approval=REJECT -> decision=REJECT, change_package/rollout=None.
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    APPS_RG_DIR,
)

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from system_learning.types.app_signal_types import (
    AppSignalEventArtifact,
    build_app_signal_event,
)
from system_learning.types.offline_replay_types import (
    OfflineReplayBundle,
    render_offline_replay_bundle,
    replay_aggregate_to_rollout,
    replay_app_signals_to_aggregate,
)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


def _make_events(
    values: list[float],
    *,
    prefix: str = "msg",
) -> list[AppSignalEventArtifact]:
    """Helper: build AppSignalEventArtifact list for replay tests."""
    return [
        build_app_signal_event(
            app_id=APPS_RG_DIR,
            run_id="run_golden",
            message_id=f"{prefix}_{i:03d}",
            metric_name="resume_message_response_rate",
            metric_value=v,
            semantic_clock=_CLOCK,
        )
        for i, v in enumerate(values)
    ]


def _build_full_bundle(
    baseline_vals: list[float],
    candidate_vals: list[float],
    *,
    approval_decision: str = "APPROVE",
) -> OfflineReplayBundle:
    """Build a complete replay bundle from baseline/candidate value lists."""
    baseline_events = _make_events(baseline_vals, prefix="bl")
    candidate_events = _make_events(candidate_vals, prefix="cd")
    all_events = baseline_events + candidate_events

    aggregate = replay_app_signals_to_aggregate(
        events=all_events,
        metric_name="resume_message_response_rate",
        app_id=APPS_RG_DIR,
        window_id="w_golden",
        baseline_selector=lambda e: e.message_id.startswith("bl"),
        candidate_selector=lambda e: e.message_id.startswith("cd"),
        evidence_hash="golden_evidence",
        semantic_clock=_CLOCK,
    )

    return replay_aggregate_to_rollout(
        aggregate=aggregate,
        proposer=APPS_RG_DIR,
        target_component="routing_thresholds",
        before={"threshold": 0.5},
        after={"threshold": 0.7},
        evaluator="offline_bench",
        dataset_id="ds_golden",
        eval_evidence_hash="eval_golden",
        approver="human_reviewer",
        approval_decision=approval_decision,
        approval_rationale="Golden trace test.",
        rollout_strategy="ALL_AT_ONCE",
        rollout_invariants=["guardian_green"],
        rollout_max_duration_minutes=60,
        semantic_clock=_CLOCK,
    )


class TestDeterministicReplayBundle:
    def test_identical_inputs_produce_byte_identical_json(self) -> None:
        """Two replay bundles with same inputs produce byte-identical JSON."""
        bundle1 = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.89])
        bundle2 = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.89])

        json1 = render_offline_replay_bundle(bundle1)
        json2 = render_offline_replay_bundle(bundle2)
        assert json1 == json2

        parsed = json.loads(json1)
        assert parsed["proposal"]["artifact_type"] == "META_LEARNING_PROPOSAL"
        assert parsed["decision"]["decision"] == "ALLOW_TO_APPLY"
        assert parsed["rollout_plan"] is not None
        assert parsed["change_package"] is not None
        assert bundle1.rollout_plan is not None
        assert bundle1.rollout_plan.trace_id == bundle2.rollout_plan.trace_id


class TestDriftDetection:
    def test_single_event_change_propagates_trace_ids(self) -> None:
        """Changing a single event metric_value changes downstream trace_ids."""
        bundle_a = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.89])
        bundle_b = _build_full_bundle([0.80, 0.82, 0.84], [0.85, 0.87, 0.90])

        assert bundle_a.aggregate.trace_id != bundle_b.aggregate.trace_id
        assert bundle_a.proposal.trace_id != bundle_b.proposal.trace_id
        assert bundle_a.evaluation.trace_id != bundle_b.evaluation.trace_id

        assert bundle_a.change_package is not None
        assert bundle_b.change_package is not None
        assert bundle_a.change_package.trace_id != bundle_b.change_package.trace_id

        assert bundle_a.rollout_plan is not None
        assert bundle_b.rollout_plan is not None
        assert bundle_a.rollout_plan.trace_id != bundle_b.rollout_plan.trace_id


class TestFailClosedPath:
    def test_reject_approval_blocks_change_package_and_rollout(self) -> None:
        """Approval=REJECT -> decision=REJECT, change_package=None, rollout=None."""
        bundle = _build_full_bundle(
            [0.80, 0.82],
            [0.85, 0.87],
            approval_decision="REJECT",
        )
        assert bundle.decision.decision == "REJECT"
        assert bundle.decision.deny_reason == "APPROVAL_REJECTED"
        assert bundle.change_package is None
        assert bundle.rollout_plan is None

        json_str = render_offline_replay_bundle(bundle)
        parsed = json.loads(json_str)
        assert parsed["change_package"] is None
        assert parsed["rollout_plan"] is None
        assert parsed["decision"]["decision"] == "REJECT"

        bundle2 = _build_full_bundle(
            [0.80, 0.82],
            [0.85, 0.87],
            approval_decision="REJECT",
        )
        assert render_offline_replay_bundle(bundle) == render_offline_replay_bundle(bundle2)
