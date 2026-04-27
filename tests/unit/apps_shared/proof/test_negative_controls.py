"""Tests for apps_shared.proof.negative_controls — controls registry and types."""

from __future__ import annotations

from apps_shared.proof.negative_controls import CONTROLS, NegativeControlResult


def test_thirteen_controls_registered():
    # T1..T12 plus T13 (defense-in-depth probe)
    assert len(CONTROLS) == 13


def test_each_control_is_well_formed():
    for name, desc, target, mutator, expected_reason in CONTROLS:
        assert isinstance(name, str) and name.startswith("T")
        assert isinstance(desc, str) and desc
        assert target in {"trace", "inventory", "replay", "inventory_expect_pass"}
        assert callable(mutator)
        # INSTALL 1: every typed control MUST declare an expected_fail_reason.
        # Only inventory_expect_pass (T13) may declare None.
        if target == "inventory_expect_pass":
            assert expected_reason is None, (
                f"{name}: inventory_expect_pass controls must have None expected_reason"
            )
        else:
            assert isinstance(expected_reason, str) and expected_reason, (
                f"{name}: typed controls must declare a non-empty expected_fail_reason "
                "(prevents wrong-mechanism catches from passing silently)"
            )


def test_control_names_unique():
    names = [c[0] for c in CONTROLS]
    assert len(set(names)) == len(names)


def test_targets_cover_all_three_validators():
    targets = {c[2] for c in CONTROLS}
    # The three primary validators MUST be covered. T13's special target is
    # not a validator, just a documented architectural probe.
    assert {"trace", "inventory", "replay"}.issubset(targets)


def test_at_least_three_per_validator():
    from collections import Counter
    counts = Counter(c[2] for c in CONTROLS)
    assert all(counts[t] >= 3 for t in ("trace", "inventory", "replay"))


def test_t13_defense_in_depth_probe_registered():
    """T13 documents the architectural truth: packet_hash is content-binding,
    not secret authentication. A rehashed tamper passes inventory alone.
    """
    t13 = next((c for c in CONTROLS if c[0] == "T13_packet_recompute_attack"), None)
    assert t13 is not None, "T13 must be registered"
    assert t13[2] == "inventory_expect_pass"


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
