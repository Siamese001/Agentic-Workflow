"""W1.P1 unit tests — typed routing feature vector contract."""

from __future__ import annotations

import json
import typing

import pytest

from agentic_core.runtime.contracts.routing_features import (
    NO_SIGNAL,
    FreshnessClass,
    RoutingFeatureVector,
    WorkClass,
    build_feature_vector,
    canonical_feature_bytes,
)


class TestWorkClassEnum:
    def test_enum_values_are_string_stable(self) -> None:
        assert WorkClass.FACTUAL.value == "factual"
        assert WorkClass.SUMMARIZE.value == "summarize"
        assert WorkClass.COMPARE.value == "compare"
        assert WorkClass.ANALYZE.value == "analyze"
        assert WorkClass.ACT.value == "act"
        assert WorkClass.GENERATE.value == "generate"
        assert WorkClass.UNKNOWN.value == "unknown"

    def test_enum_is_closed(self) -> None:
        # Exactly 7 members — W3 wiring depends on this cardinality.
        assert len(list(WorkClass)) == 7


class TestFreshnessClassParity:
    """Parity with the L0 Literal — rule: runtime.contracts cannot import L0,
    so the string set is duplicated. This test guards against silent drift.
    """

    def test_freshness_class_parity_with_l0(self) -> None:
        from agentic_core.L0_routing.types import routing_artifact_types as l0_types

        # The L0 Literal's __args__ contains the allowed strings.
        l0_literal = l0_types.FreshnessClass
        l0_values = set(typing.get_args(l0_literal))
        runtime_values = set(typing.get_args(FreshnessClass))
        assert l0_values == runtime_values, (
            f"FreshnessClass drift — L0={l0_values} runtime={runtime_values}. Update both or consolidate."
        )


class TestBuildFeatureVector:
    def test_defaults_produce_all_sentinels(self) -> None:
        fv = build_feature_vector()
        assert fv.work_class is WorkClass.UNKNOWN
        assert fv.freshness_class == "bounded"
        assert fv.grounding_need_score == NO_SIGNAL
        assert fv.ood_score == NO_SIGNAL
        assert fv.budget_headroom_ratio == NO_SIGNAL
        assert fv.has_grounding_signal() is False
        assert fv.has_ood_signal() is False
        assert fv.has_budget_signal() is False

    def test_string_work_class_is_coerced(self) -> None:
        fv = build_feature_vector(work_class="factual")
        assert fv.work_class is WorkClass.FACTUAL

    def test_invalid_work_class_string_rejected(self) -> None:
        with pytest.raises(ValueError, match="not a valid WorkClass"):
            build_feature_vector(work_class="nonsense")

    def test_populated_vector_has_signals(self) -> None:
        fv = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
            ood_score=0.10,
            budget_headroom_ratio=0.45,
        )
        assert fv.has_grounding_signal()
        assert fv.has_ood_signal()
        assert fv.has_budget_signal()
        assert fv.grounding_need_score == pytest.approx(0.82)


class TestValidation:
    def test_out_of_range_grounding_score_rejected(self) -> None:
        with pytest.raises(ValueError, match="grounding_need_score"):
            build_feature_vector(grounding_need_score=1.5)

    def test_negative_grounding_score_not_no_signal_rejected(self) -> None:
        with pytest.raises(ValueError, match="grounding_need_score"):
            build_feature_vector(grounding_need_score=-0.5)

    def test_no_signal_sentinel_passes(self) -> None:
        fv = build_feature_vector(grounding_need_score=NO_SIGNAL)
        assert fv.grounding_need_score == NO_SIGNAL

    def test_nan_score_rejected(self) -> None:
        with pytest.raises(ValueError, match="must not be NaN"):
            build_feature_vector(ood_score=float("nan"))

    def test_bad_freshness_class_rejected(self) -> None:
        # Build directly — build_feature_vector defaults freshness to "bounded".
        with pytest.raises(ValueError, match="freshness_class"):
            RoutingFeatureVector(
                work_class=WorkClass.UNKNOWN,
                freshness_class="eventually",  # type: ignore[arg-type]
                grounding_need_score=NO_SIGNAL,
                ood_score=NO_SIGNAL,
                budget_headroom_ratio=NO_SIGNAL,
            )

    def test_non_enum_work_class_rejected_by_dataclass(self) -> None:
        with pytest.raises(ValueError, match="work_class must be WorkClass enum"):
            RoutingFeatureVector(
                work_class="factual",  # type: ignore[arg-type]
                freshness_class="bounded",
                grounding_need_score=NO_SIGNAL,
                ood_score=NO_SIGNAL,
                budget_headroom_ratio=NO_SIGNAL,
            )


class TestManifestHash:
    def test_hash_is_deterministic(self) -> None:
        fv1 = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
            ood_score=0.10,
            budget_headroom_ratio=0.45,
        )
        fv2 = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
            ood_score=0.10,
            budget_headroom_ratio=0.45,
        )
        assert fv1.manifest_hash == fv2.manifest_hash
        assert len(fv1.manifest_hash) == 64  # sha256 hex

    def test_hash_ignores_metadata(self) -> None:
        fv1 = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
            ood_score=0.10,
            budget_headroom_ratio=0.45,
            metadata={"trace_id": "abc"},
        )
        fv2 = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
            ood_score=0.10,
            budget_headroom_ratio=0.45,
            metadata={"trace_id": "xyz"},
        )
        assert fv1.manifest_hash == fv2.manifest_hash

    def test_hash_changes_with_primary_field(self) -> None:
        fv1 = build_feature_vector(work_class=WorkClass.FACTUAL)
        fv2 = build_feature_vector(work_class=WorkClass.SUMMARIZE)
        assert fv1.manifest_hash != fv2.manifest_hash

    def test_canonical_bytes_are_sorted_json(self) -> None:
        fv = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
            ood_score=0.10,
            budget_headroom_ratio=0.45,
        )
        canonical = canonical_feature_bytes(fv)
        decoded = json.loads(canonical)
        assert list(decoded.keys()) == sorted(decoded.keys())
        assert decoded["work_class"] == "factual"
        assert decoded["freshness_class"] == "fresh"
        assert decoded["grounding_need_score"] == pytest.approx(0.82)


class TestToDict:
    def test_roundtrip_shape(self) -> None:
        fv = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.72,
            ood_score=0.15,
            budget_headroom_ratio=0.95,
            metadata={"trace_id": "t-1"},
        )
        payload = fv.to_dict()
        # Ensure JSON-safe (no custom objects leaking).
        json.dumps(payload)
        assert payload["work_class"] == "factual"
        assert payload["metadata"] == {"trace_id": "t-1"}
        assert payload["manifest_hash"] == fv.manifest_hash

    def test_immutable(self) -> None:
        fv = build_feature_vector(work_class=WorkClass.FACTUAL)
        with pytest.raises((AttributeError, Exception)):
            fv.grounding_need_score = 0.99  # type: ignore[misc]
