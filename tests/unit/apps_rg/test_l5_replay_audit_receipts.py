"""apps-test-model: LAW."""

from types import SimpleNamespace

from apps_rg.runtime.bindings.l2_envelope_adapter import _build_determinism_bundle
from apps_rg.runtime.l5.packet_builder import build_l5_certification_packet


def _make_minimal_cpa(**overrides):
    base = {
        "request_id": "req-replay",
        "run_id": "run-replay",
        "app_id": "apps_rg",
        "trace_id": "trace-replay",
        "tenant_id": "apps_rg",
        "compilation_hash": "prompt-a",
        "replay_key": "replay-a",
        "l5_certification_ref": "l5:apps_rg:u0:valid",
        "signature": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_same_replay_key_produces_same_attempt_seed() -> None:
    cpa = _make_minimal_cpa(replay_key="replay-a", compilation_hash="prompt-a")

    first = _build_determinism_bundle(
        cpa,
        route_id="route",
        node_id="node",
        attempt_number=1,
    )
    second = _build_determinism_bundle(
        cpa,
        route_id="route",
        node_id="node",
        attempt_number=1,
    )

    assert first.attempt_seed == second.attempt_seed


def test_attempt_seed_changes_when_replay_key_changes() -> None:
    first = _build_determinism_bundle(
        _make_minimal_cpa(replay_key="replay-a", compilation_hash="prompt-a"),
        route_id="route",
        node_id="node",
        attempt_number=1,
    )
    second = _build_determinism_bundle(
        _make_minimal_cpa(replay_key="replay-b", compilation_hash="prompt-a"),
        route_id="route",
        node_id="node",
        attempt_number=1,
    )

    assert first.attempt_seed != second.attempt_seed


def test_missing_replay_key_yields_l5_not_certified() -> None:
    cpa = _make_minimal_cpa(replay_key="", compilation_hash="prompt-a")
    result = build_l5_certification_packet(prompt_artifact=cpa)

    assert result.status == "L5_NOT_CERTIFIED"
    assert any("missing_replay_key" in rc for rc in result.packet.reason_codes)
