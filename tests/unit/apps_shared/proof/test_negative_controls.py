"""Tests for apps_shared.proof.negative_controls — controls registry and types."""

from __future__ import annotations

from apps_shared.proof.negative_controls import CONTROLS, NegativeControlResult


def test_twelve_controls_registered():
    assert len(CONTROLS) == 12


def test_each_control_is_well_formed():
    for name, desc, target, mutator in CONTROLS:
        assert isinstance(name, str) and name.startswith("T")
        assert isinstance(desc, str) and desc
        assert target in {"trace", "inventory", "replay"}
        assert callable(mutator)


def test_control_names_unique():
    names = [c[0] for c in CONTROLS]
    assert len(set(names)) == len(names)


def test_targets_cover_all_three_validators():
    targets = {c[2] for c in CONTROLS}
    assert targets == {"trace", "inventory", "replay"}


def test_at_least_three_per_validator():
    from collections import Counter

    counts = Counter(c[2] for c in CONTROLS)
    assert all(counts[t] >= 3 for t in ("trace", "inventory", "replay"))


def test_negative_control_result_to_dict():
    r = NegativeControlResult(
        name="T1",
        description="d",
        target_validator="inventory",
        caught=True,
        validator_verdict_ok=False,
        fail_reasons=["x"],
    )
    d = r.to_dict()
    assert d["caught"] is True and d["fail_reasons"] == ["x"]
