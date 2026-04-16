"""Wave D4.1 unit tests for the F17 R5 fallback / abstain route.

Coverage requirements (Wave D plan §3 Slice D4 and the D4.1 prompt):

1. R5 fires for low-confidence input
2. existing success routes still behave unchanged
3. contract-error paths still behave unchanged
4. R5 outcome shape is stable and serializable
5. router consumes D3 abstain output rather than re-implementing the logic inline
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from agentic_core.L0_routing.enforcement.routing_contract import (
    RoutingContractError,
)
from agentic_core.L0_routing.reasoning import path_router as path_router_module
from agentic_core.L0_routing.reasoning.path_router import (
    R5_ROUTE,
    Path,
    PathRouter,
    RoutingResult,
)
from agentic_core.L1_cognition.reasoning.abstain_planner import (
    ACTION_CONTINUE,
    ACTION_EMIT_R5,
    DECISION_ABSTAIN,
    DECISION_PROCEED,
    DEFAULT_ABSTAIN_THRESHOLD,
)

REQUIRED_FIELDS = {"route", "reason", "confidence", "threshold", "action"}


def _mock_payload(**overrides: Any) -> Any:
    """Build a minimal GovernedPayload-shaped fixture.

    The real ``GovernedPayload`` is assembled by the L0 routing pipeline and
    carries heavy dependencies. For unit tests we only need the attributes
    that ``select_path`` reads; ``SimpleNamespace`` satisfies the duck-typed
    protocol cheaply.
    """
    attrs: dict[str, Any] = {
        "input_text": "test input",
        "check_ids": [],
        "sanitized": False,
        "d0_injections": None,
    }
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


class TestR5FiresForLowConfidence:
    """Requirement 1: R5 fires for low-confidence input."""

    def test_low_confidence_returns_r5_route(self) -> None:
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.30, threshold=0.50)
        assert result["route"] == R5_ROUTE
        assert result["route"] == "R5"

    def test_low_confidence_emits_emit_r5_candidate_action(self) -> None:
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.10, threshold=0.50)
        assert result["action"] == ACTION_EMIT_R5

    def test_r5_echoes_confidence_and_threshold(self) -> None:
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.42, threshold=0.75)
        assert result["confidence"] == pytest.approx(0.42)
        assert result["threshold"] == pytest.approx(0.75)

    def test_r5_uses_default_abstain_threshold_when_unspecified(self) -> None:
        router = PathRouter()
        # Default threshold is 0.50; confidence=0.49 is strictly below => R5.
        result = router.route_with_confidence(_mock_payload(), confidence=0.49)
        assert result["route"] == R5_ROUTE
        assert result["threshold"] == pytest.approx(DEFAULT_ABSTAIN_THRESHOLD)

    def test_r5_does_not_call_select_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When R5 fires, select_path must NOT be invoked — contract commits
        and success telemetry must not be emitted for an abstain decision.
        """
        select_path_calls: list[Any] = []

        def _tracking_select_path(self: PathRouter, payload: Any) -> Path:
            select_path_calls.append(payload)
            return Path.A

        monkeypatch.setattr(PathRouter, "select_path", _tracking_select_path)
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.10, threshold=0.50)
        assert result["route"] == R5_ROUTE
        assert select_path_calls == [], "select_path must not be called on the R5 branch"


class TestExistingSuccessRoutesUnchanged:
    """Requirement 2: existing success routes still behave unchanged."""

    def test_path_enum_has_exactly_four_values(self) -> None:
        # Wave D4.1 deliberately does NOT extend the Path enum — R5 lives as
        # a module-level string constant. Any future addition to this enum
        # would need its own HITL approval and would break this assertion.
        assert {p.value for p in Path} == {"A", "B", "C", "D"}

    def test_path_a_b_c_d_values_are_stable(self) -> None:
        assert Path.A.value == "A"
        assert Path.B.value == "B"
        assert Path.C.value == "C"
        assert Path.D.value == "D"

    def test_select_path_still_exists_with_original_signature(self) -> None:
        import inspect

        sig = inspect.signature(PathRouter.select_path)
        # self + payload = 2 parameters
        assert len(sig.parameters) == 2
        assert "payload" in sig.parameters
        # Return annotation should remain Path (not RoutingResult).
        assert sig.return_annotation is Path

    def test_proceed_branch_delegates_to_select_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When confidence >= threshold, route_with_confidence must delegate
        to the existing select_path method (which is byte-unchanged).
        """
        captured_payloads: list[Any] = []

        def _fake_select_path(self: PathRouter, payload: Any) -> Path:
            captured_payloads.append(payload)
            return Path.C

        monkeypatch.setattr(PathRouter, "select_path", _fake_select_path)
        router = PathRouter()
        payload = _mock_payload()
        result = router.route_with_confidence(payload, confidence=0.95, threshold=0.50)

        assert len(captured_payloads) == 1
        assert captured_payloads[0] is payload
        assert result["route"] == "C"
        assert result["action"] == ACTION_CONTINUE

    @pytest.mark.parametrize("returned_path", list(Path))
    def test_all_four_existing_paths_propagate_through_proceed_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        returned_path: Path,
    ) -> None:
        monkeypatch.setattr(
            PathRouter,
            "select_path",
            lambda self, p: returned_path,
        )
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.95, threshold=0.50)
        assert result["route"] == returned_path.value
        assert result["action"] == ACTION_CONTINUE


class TestContractErrorPathsUnchanged:
    """Requirement 3: contract-error paths still behave unchanged."""

    def test_contract_error_from_select_path_propagates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _raising_select_path(self: PathRouter, payload: Any) -> Path:
            raise RoutingContractError("simulated contract failure")

        monkeypatch.setattr(PathRouter, "select_path", _raising_select_path)
        router = PathRouter()
        with pytest.raises(RoutingContractError, match="simulated"):
            router.route_with_confidence(_mock_payload(), confidence=0.95, threshold=0.50)

    def test_r5_branch_does_not_swallow_unrelated_exceptions(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """R5 must not mask genuine errors from the D3 primitive (e.g. an
        out-of-range confidence value raises ValueError)."""
        router = PathRouter()
        with pytest.raises(ValueError, match="confidence"):
            router.route_with_confidence(_mock_payload(), confidence=1.5, threshold=0.50)

    def test_out_of_range_threshold_raises(self) -> None:
        router = PathRouter()
        with pytest.raises(ValueError, match="threshold"):
            router.route_with_confidence(_mock_payload(), confidence=0.5, threshold=2.0)


class TestR5OutcomeShapeStableAndSerializable:
    """Requirement 4: R5 outcome shape is stable and serializable."""

    def test_shape_has_exactly_five_required_fields(self) -> None:
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.10, threshold=0.50)
        assert set(result.keys()) == REQUIRED_FIELDS

    def test_r5_result_is_json_serializable(self) -> None:
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.20, threshold=0.50)
        encoded = json.dumps(result)
        decoded = json.loads(encoded)
        assert decoded == dict(result)

    def test_proceed_result_is_json_serializable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(PathRouter, "select_path", lambda self, p: Path.B)
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.95, threshold=0.50)
        encoded = json.dumps(result)
        decoded = json.loads(encoded)
        assert decoded == dict(result)
        assert decoded["route"] == "B"

    def test_field_types_are_primitives(self) -> None:
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.10, threshold=0.50)
        assert isinstance(result["route"], str)
        assert isinstance(result["reason"], str)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["threshold"], float)
        assert isinstance(result["action"], str)

    def test_route_is_in_closed_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(PathRouter, "select_path", lambda self, p: Path.A)
        router = PathRouter()
        proceed = router.route_with_confidence(_mock_payload(), confidence=0.95, threshold=0.50)
        abstain = router.route_with_confidence(_mock_payload(), confidence=0.10, threshold=0.50)
        assert proceed["route"] in {"A", "B", "C", "D", R5_ROUTE}
        assert abstain["route"] in {"A", "B", "C", "D", R5_ROUTE}

    def test_action_is_in_closed_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(PathRouter, "select_path", lambda self, p: Path.A)
        router = PathRouter()
        proceed = router.route_with_confidence(_mock_payload(), confidence=0.95, threshold=0.50)
        abstain = router.route_with_confidence(_mock_payload(), confidence=0.10, threshold=0.50)
        assert proceed["action"] in {ACTION_CONTINUE, ACTION_EMIT_R5}
        assert abstain["action"] in {ACTION_CONTINUE, ACTION_EMIT_R5}

    def test_routing_result_typeddict_is_exported(self) -> None:
        # Public contract: downstream D5 must be able to import the TypedDict
        # for static typing.
        assert RoutingResult is not None


class TestRouterConsumesD3Primitive:
    """Requirement 5: router consumes D3 abstain output rather than
    re-implementing the logic inline."""

    def test_router_calls_plan_abstain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Monkeypatch plan_abstain to verify the router delegates rather
        than computing an abstain decision itself. If the router were
        re-implementing the logic inline, the injected replacement would
        have no effect on the returned result.
        """
        call_log: list[tuple[float, float]] = []

        def _fake_plan_abstain(confidence: float, threshold: float, **kwargs: Any) -> dict[str, Any]:
            call_log.append((confidence, threshold))
            return {
                "decision": DECISION_ABSTAIN,
                "reason": "INJECTED-REASON-FROM-FAKE",
                "confidence": confidence,
                "threshold": threshold,
                "action": ACTION_EMIT_R5,
            }

        monkeypatch.setattr(path_router_module, "plan_abstain", _fake_plan_abstain)
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.42, threshold=0.50)

        assert call_log == [(0.42, 0.50)], "router must call plan_abstain exactly once with the same args"
        # The fake's unique reason string proves the router used the output
        # rather than regenerating it locally.
        assert result["reason"] == "INJECTED-REASON-FROM-FAKE"

    def test_router_respects_plan_abstain_proceed_decision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """If plan_abstain returns a proceed decision, the router must NOT
        take the R5 branch — even if confidence looks low by naive
        comparison. This proves the router treats plan_abstain as the
        source of truth.
        """

        def _override_proceed(confidence: float, threshold: float, **kwargs: Any) -> dict[str, Any]:
            # Force PROCEED even though confidence<threshold.
            return {
                "decision": DECISION_PROCEED,
                "reason": "injected proceed override",
                "confidence": confidence,
                "threshold": threshold,
                "action": ACTION_CONTINUE,
            }

        monkeypatch.setattr(path_router_module, "plan_abstain", _override_proceed)
        monkeypatch.setattr(PathRouter, "select_path", lambda self, p: Path.D)
        router = PathRouter()
        # Naive "confidence<threshold" logic would return R5 here; the router
        # must instead honor the injected plan_abstain decision.
        result = router.route_with_confidence(_mock_payload(), confidence=0.10, threshold=0.50)
        assert result["route"] == "D"
        assert result["action"] == ACTION_CONTINUE
        assert result["reason"] == "injected proceed override"

    def test_router_respects_plan_abstain_abstain_decision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Dual of the proceed test: if plan_abstain returns abstain even
        for high confidence, the router must take the R5 branch.
        """

        def _override_abstain(confidence: float, threshold: float, **kwargs: Any) -> dict[str, Any]:
            return {
                "decision": DECISION_ABSTAIN,
                "reason": "injected abstain override",
                "confidence": confidence,
                "threshold": threshold,
                "action": ACTION_EMIT_R5,
            }

        monkeypatch.setattr(path_router_module, "plan_abstain", _override_abstain)
        select_path_called = False

        def _sentinel_select_path(self: PathRouter, payload: Any) -> Path:
            nonlocal select_path_called
            select_path_called = True
            return Path.A

        monkeypatch.setattr(PathRouter, "select_path", _sentinel_select_path)
        router = PathRouter()
        result = router.route_with_confidence(_mock_payload(), confidence=0.99, threshold=0.50)
        assert result["route"] == R5_ROUTE
        assert select_path_called is False, "select_path must not be called when plan_abstain returns abstain"

    def test_r5_route_matches_plan_abstain_fields_verbatim(self) -> None:
        """End-to-end check: the RoutingResult's (reason, confidence,
        threshold, action) fields must equal the values the real
        plan_abstain primitive produces for the same input. This is the
        strongest behavioral assertion that no inline re-implementation
        exists.
        """
        from agentic_core.L1_cognition.reasoning.abstain_planner import (
            plan_abstain,
        )

        confidence, threshold = 0.30, 0.50
        expected = plan_abstain(confidence, threshold)

        router = PathRouter()
        actual = router.route_with_confidence(_mock_payload(), confidence=confidence, threshold=threshold)

        assert actual["reason"] == expected["reason"]
        assert actual["confidence"] == expected["confidence"]
        assert actual["threshold"] == expected["threshold"]
        assert actual["action"] == expected["action"]
