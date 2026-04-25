"""Test coverage for `agentic_core.L0_routing.types.shadow_routing_types`.

Wave 1 of `.windsurf/plans/test-coverage-waves-f8f5a7.md`.

Module rationale: Phase 9 shadow router contract surface. Frozen dataclasses
that drive non-invasive routing drift detection. Tests pin: enum members,
dataclass shape (frozen, mandatory fields), canonical-JSON shape, and
deterministic 64-hex fingerprint output.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L0_routing.types.shadow_routing_types"


@pytest.fixture(scope="module")
def shadow_types():
    return pytest.importorskip(MODULE)


@pytest.fixture(scope="module")
def route_path_enum():
    mod = pytest.importorskip("agentic_core.L0_routing.types.routing_artifact_types")
    return mod.RoutePath


def test_module_imports_cleanly(shadow_types):
    assert shadow_types is not None


def test_public_surface(shadow_types):
    for name in [
        "ShadowRoutingRationale",
        "ShadowRoutingDecision",
        "ShadowRoutingTelemetry",
        "canonical_json",
    ]:
        assert hasattr(shadow_types, name), f"{name} missing"


@pytest.mark.parametrize(
    "member,value",
    [
        ("ALIGN_WITH_LIVE", "align_with_live"),
        ("ALTERNATE_PATH_SUGGESTED", "alternate_path_suggested"),
        ("RISK_MITIGATION", "risk_mitigation"),
        ("POLICY_OPTIMIZATION", "policy_optimization"),
        ("FEATURE_DRIFT_DETECTED", "feature_drift_detected"),
    ],
)
def test_rationale_enum_members(shadow_types, member, value):
    rationale = shadow_types.ShadowRoutingRationale
    assert hasattr(rationale, member)
    assert getattr(rationale, member).value == value


def test_decision_dataclass_is_frozen(shadow_types):
    cls = shadow_types.ShadowRoutingDecision
    assert dataclasses.is_dataclass(cls)
    fields = {f.name: f for f in dataclasses.fields(cls)}
    for required in [
        "trace_id",
        "observed_route",
        "shadow_route",
        "drift_score",
        "feature_fingerprint",
        "timestamp",
        "shadow_rationale",
    ]:
        assert required in fields, f"missing field {required}"
    # frozen=True means assignment raises FrozenInstanceError
    inst = _make_decision(shadow_types)
    with pytest.raises(dataclasses.FrozenInstanceError):
        inst.drift_score = 0.99  # type: ignore[misc]


def test_telemetry_dataclass_shape(shadow_types):
    cls = shadow_types.ShadowRoutingTelemetry
    assert dataclasses.is_dataclass(cls)
    fields = {f.name for f in dataclasses.fields(cls)}
    assert {"trace_id", "shadow_decision", "emitted_at"}.issubset(fields)


def _make_decision(shadow_types):
    """Build a minimal valid ShadowRoutingDecision for round-trip tests."""
    from agentic_core.L0_routing.types.routing_artifact_types import RoutePath

    # Pick the first available RoutePath enum member rather than hardcoding.
    a_route = next(iter(RoutePath))
    return shadow_types.ShadowRoutingDecision(
        trace_id="trace-abc-123",
        observed_route=a_route,
        shadow_route=a_route,
        drift_score=0.0,
        feature_fingerprint="deadbeef" * 8,
        timestamp="2026-01-01T00:00:00Z",
        shadow_rationale=shadow_types.ShadowRoutingRationale.ALIGN_WITH_LIVE,
    )


def test_compute_canonical_fingerprint_returns_64_hex(shadow_types):
    decision = _make_decision(shadow_types)
    digest = decision.compute_canonical_fingerprint({"k": "v", "n": 1})
    assert isinstance(digest, str)
    assert len(digest) == 64
    int(digest, 16)  # must be valid hex


def test_compute_canonical_fingerprint_is_deterministic(shadow_types):
    decision = _make_decision(shadow_types)
    features = {"foo": "bar", "n": 42, "nested": {"a": [1, 2, 3]}}
    a = decision.compute_canonical_fingerprint(features)
    b = decision.compute_canonical_fingerprint(features)
    assert a == b


def test_compute_canonical_fingerprint_distinguishes_inputs(shadow_types):
    decision = _make_decision(shadow_types)
    a = decision.compute_canonical_fingerprint({"k": "v1"})
    b = decision.compute_canonical_fingerprint({"k": "v2"})
    assert a != b


def test_to_canonical_json_emits_required_keys(shadow_types):
    decision = _make_decision(shadow_types)
    payload = decision.to_canonical_json()
    assert isinstance(payload, str)
    parsed = json.loads(payload)
    for key in [
        "trace_id",
        "observed_route",
        "shadow_route",
        "drift_score",
        "feature_fingerprint",
        "model_version",
        "ruleset_version",
        "shadow_rationale",
    ]:
        assert key in parsed, f"missing {key} in canonical JSON"


def test_telemetry_canonical_json_includes_decision(shadow_types):
    decision = _make_decision(shadow_types)
    telemetry = shadow_types.ShadowRoutingTelemetry(
        trace_id="t1",
        shadow_decision=decision,
        emitted_at="2026-01-01T00:00:00Z",
    )
    payload = telemetry.to_canonical_json()
    parsed = json.loads(payload)
    assert parsed["trace_id"] == "t1"
    assert "shadow_decision" in parsed
    assert parsed["shadow_decision"]["trace_id"] == decision.trace_id
