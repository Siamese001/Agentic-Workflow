"""Unit tests for ``agentic_core.L6_observability.decision_provenance``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W3.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from agentic_core.L6_observability.decision_events_schema import (
    UnknownDecisionLayerError,
)
from agentic_core.L6_observability.decision_provenance import (
    UNKNOWN_CALIBRATION_VERSION,
    UNKNOWN_JUDGE_VERSION,
    UNKNOWN_POLICY_HASH,
    UNKNOWN_SNAPSHOT_ID,
    DecisionProvenance,
    current_provenance,
    provenance_digest,
    reset_active_provenance,
    set_active_provenance,
)


@pytest.fixture(autouse=True)
def _isolated_provenance(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Each test starts with no env overrides + clean in-process cache."""
    monkeypatch.delenv("AGENTIC_POLICY_HASH", raising=False)
    monkeypatch.delenv("AGENTIC_SNAPSHOT_ID", raising=False)
    monkeypatch.delenv("AGENTIC_CALIBRATION_VERSION", raising=False)
    monkeypatch.delenv("AGENTIC_JUDGE_VERSION", raising=False)
    reset_active_provenance()
    yield
    reset_active_provenance()


def test_dataclass_rejects_unknown_layer() -> None:
    with pytest.raises(UnknownDecisionLayerError):
        DecisionProvenance(decision_layer="L99_phantom")


def test_default_fields_use_sentinels() -> None:
    prov = DecisionProvenance(decision_layer="L0_routing")
    assert prov.policy_hash == UNKNOWN_POLICY_HASH
    assert prov.snapshot_id == UNKNOWN_SNAPSHOT_ID
    assert prov.calibration_version == UNKNOWN_CALIBRATION_VERSION
    assert prov.judge_version == UNKNOWN_JUDGE_VERSION


def test_digest_is_deterministic() -> None:
    p1 = DecisionProvenance(
        decision_layer="L0_routing",
        policy_hash="ph_a",
        snapshot_id="snap_b",
        calibration_version="cal_c",
        judge_version="judge_d",
    )
    p2 = DecisionProvenance(
        decision_layer="L0_routing",
        policy_hash="ph_a",
        snapshot_id="snap_b",
        calibration_version="cal_c",
        judge_version="judge_d",
    )
    assert provenance_digest(p1) == provenance_digest(p2)
    # 32-char hex (truncated sha256)
    assert len(provenance_digest(p1)) == 32


def test_digest_changes_on_field_change() -> None:
    base = DecisionProvenance(decision_layer="L0_routing", policy_hash="A")
    flipped = DecisionProvenance(decision_layer="L0_routing", policy_hash="B")
    assert provenance_digest(base) != provenance_digest(flipped)


def test_current_provenance_uses_env_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTIC_POLICY_HASH", "env_policy")
    monkeypatch.setenv("AGENTIC_SNAPSHOT_ID", "env_snap")
    prov = current_provenance("Exit_eval")
    assert prov.decision_layer == "Exit_eval"
    assert prov.policy_hash == "env_policy"
    assert prov.snapshot_id == "env_snap"
    # Unset fields fall through to sentinels
    assert prov.calibration_version == UNKNOWN_CALIBRATION_VERSION
    assert prov.judge_version == UNKNOWN_JUDGE_VERSION


def test_current_provenance_uses_in_process_cache_when_no_env() -> None:
    set_active_provenance(
        policy_hash="ip_policy",
        calibration_version="ip_cal",
    )
    prov = current_provenance("L3_orchestration")
    assert prov.policy_hash == "ip_policy"
    assert prov.calibration_version == "ip_cal"
    # Other fields still sentinel
    assert prov.snapshot_id == UNKNOWN_SNAPSHOT_ID
    assert prov.judge_version == UNKNOWN_JUDGE_VERSION


def test_env_overrides_in_process_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Env var must win over the in-process cache (deployment > runtime bind)."""
    set_active_provenance(policy_hash="ip_loses")
    monkeypatch.setenv("AGENTIC_POLICY_HASH", "env_wins")
    prov = current_provenance("L0_routing")
    assert prov.policy_hash == "env_wins"


def test_to_dict_round_trip() -> None:
    prov = DecisionProvenance(
        decision_layer="UWG",
        policy_hash="ph",
        snapshot_id="sn",
        calibration_version="cv",
        judge_version="jv",
    )
    payload = prov.to_dict()
    assert payload == {
        "decision_layer": "UWG",
        "policy_hash": "ph",
        "snapshot_id": "sn",
        "calibration_version": "cv",
        "judge_version": "jv",
    }


def test_current_provenance_never_raises_on_unset_environment() -> None:
    """All five fields fall through to sentinels — function must not raise."""
    prov = current_provenance("L6_promotion")
    assert prov.decision_layer == "L6_promotion"
    assert prov.policy_hash == UNKNOWN_POLICY_HASH
