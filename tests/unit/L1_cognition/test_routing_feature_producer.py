"""W5.P2 tests — L1 producer hook for RoutingFeatureVector."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.routing_feature_producer import (
    build_routing_feature_vector,
)
from agentic_core.runtime.contracts.routing_features import (
    NO_SIGNAL,
    RoutingFeatureVector,
    WorkClass,
)


class TestBuildRoutingFeatureVector:
    def test_returns_routing_feature_vector(self) -> None:
        fv = build_routing_feature_vector("What is the latest policy?")
        assert isinstance(fv, RoutingFeatureVector)

    def test_grounding_score_computed_when_omitted(self) -> None:
        fv = build_routing_feature_vector(
            "What is the current Federal Reserve rate as of today?",
            work_class=WorkClass.FACTUAL,
        )
        # W1.P2 heuristic should score this high.
        assert fv.grounding_need_score > 0.60

    def test_grounding_score_honors_explicit_override(self) -> None:
        fv = build_routing_feature_vector(
            "anything", grounding_need_score=0.12,
        )
        assert fv.grounding_need_score == pytest.approx(0.12)

    def test_work_class_auto_detected(self) -> None:
        fv = build_routing_feature_vector("Summarize the document below")
        assert fv.work_class is WorkClass.SUMMARIZE

    def test_work_class_explicit_enum(self) -> None:
        fv = build_routing_feature_vector(
            "q", work_class=WorkClass.ANALYZE,
        )
        assert fv.work_class is WorkClass.ANALYZE

    def test_work_class_string_coerced_to_enum(self) -> None:
        fv = build_routing_feature_vector("q", work_class="compare")
        assert fv.work_class is WorkClass.COMPARE

    def test_invalid_work_class_string_raises(self) -> None:
        with pytest.raises(ValueError):
            build_routing_feature_vector("q", work_class="nonsense")

    def test_freshness_default_bounded(self) -> None:
        fv = build_routing_feature_vector("q")
        assert fv.freshness_class == "bounded"

    def test_freshness_explicit(self) -> None:
        fv = build_routing_feature_vector("q", freshness_class="fresh")
        assert fv.freshness_class == "fresh"

    def test_ood_and_budget_default_no_signal(self) -> None:
        fv = build_routing_feature_vector("q")
        assert fv.has_ood_signal() is False
        assert fv.has_budget_signal() is False

    def test_ood_and_budget_passthrough(self) -> None:
        fv = build_routing_feature_vector(
            "q", ood_score=0.33, budget_headroom_ratio=0.66,
        )
        assert fv.ood_score == pytest.approx(0.33)
        assert fv.budget_headroom_ratio == pytest.approx(0.66)

    def test_metadata_passthrough(self) -> None:
        fv = build_routing_feature_vector("q", metadata={"trace_id": "t-1"})
        assert fv.metadata == {"trace_id": "t-1"}

    def test_none_query_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be None"):
            build_routing_feature_vector(None)  # type: ignore[arg-type]

    def test_empty_query_allowed(self) -> None:
        fv = build_routing_feature_vector("")
        assert fv.grounding_need_score >= 0.0  # classifier produced something
        assert fv.has_grounding_signal() is True

    def test_no_signal_grounding_pass_through(self) -> None:
        fv = build_routing_feature_vector("q", grounding_need_score=NO_SIGNAL)
        assert fv.has_grounding_signal() is False
