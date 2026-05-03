"""Contract tests for apps_eval FEC producer.

Plan: .windsurf/plans/dom007-fec-producers-followup-e9f3c1.md W1.P1.

Verifies:
- Importing ``apps_eval.cert`` auto-registers the producer in the shared registry.
- ``produce_fec`` returns a well-shaped FEC dict for calibrated and empty paths.
- Malformed / empty run_context never raises; yields shape-valid empty packet.
- Producer is idempotent - distinct returns on each call (never shares mutable state).
"""

from __future__ import annotations

import pytest


def test_import_registers_producer() -> None:
    from apps_shared.cert.fec_producer import clear_registry, get_producer, _noop_producer  # noqa: PLC2701

    clear_registry()
    assert get_producer("apps_eval") is _noop_producer

    import apps_eval.cert  # noqa: F401 - side-effect import

    resolved = get_producer("apps_eval")
    assert resolved is not _noop_producer
    assert callable(resolved)


def test_grounded_path_with_calibration() -> None:
    from apps_eval.cert.fec_producer import produce_fec

    ctx = {
        "route_id": "apps_eval.grade_v1",
        "calibrated_rubric_id": "rubric_v3_calibrated",
        "judge_versions": ["judge_a_v2", "judge_b_v1"],
        "taxonomy_match_count": 5,
        "self_contradiction_checked": True,
    }
    fec = produce_fec(ctx)
    assert fec["schema_version"] == "1.0"
    assert fec["producer"] == "apps_eval.cert.fec_producer"
    assert fec["grounded"] is True
    assert fec["evidence_sufficiency"] == "grounded"
    assert fec["route_id"] == "apps_eval.grade_v1"
    assert fec["judge_calibration"]["calibrated_rubric_id"] == "rubric_v3_calibrated"
    assert fec["judge_calibration"]["taxonomy_match_count"] == 5
    assert fec["judge_calibration"]["self_contradiction_checked"] is True


def test_calibrated_only_path() -> None:
    from apps_eval.cert.fec_producer import produce_fec

    ctx = {"calibrated_rubric_id": "rubric_v1"}
    fec = produce_fec(ctx)
    assert fec["grounded"] is False
    assert fec["evidence_sufficiency"] == "calibrated_only"


def test_empty_context_yields_shape_valid_empty() -> None:
    from apps_eval.cert.fec_producer import produce_fec

    fec = produce_fec({})
    assert fec["schema_version"] == "1.0"
    assert fec["grounded"] is False
    assert fec["retrieval_sources"] == []
    assert fec["template_ids"] == []
    assert fec["route_id"] == ""
    assert fec["evidence_sufficiency"] == "empty"
    assert fec["judge_calibration"]["taxonomy_match_count"] == 0


def test_malformed_inputs_never_raise() -> None:
    from apps_eval.cert.fec_producer import produce_fec

    fec = produce_fec(None)  # type: ignore[arg-type]
    assert isinstance(fec, dict)
    fec = produce_fec({"judge_versions": "not-a-list", "taxonomy_match_count": "abc"})
    assert fec["judge_calibration"]["judge_versions"] == []
    assert fec["judge_calibration"]["taxonomy_match_count"] == 0


def test_resolver_round_trip() -> None:
    """resolve_fec via shared registry returns the apps_eval producer's output."""
    from apps_shared.cert.fec_producer import clear_registry, register_producer, resolve_fec
    from apps_eval.cert.fec_producer import produce_fec

    clear_registry()
    register_producer("apps_eval", produce_fec)

    fec = resolve_fec("apps_eval", {"calibrated_rubric_id": "r_v1"})
    assert fec["producer"] == "apps_eval.cert.fec_producer"
    assert fec["evidence_sufficiency"] == "calibrated_only"


def test_distinct_return_per_call() -> None:
    """Producer must return a fresh dict each call - no shared mutable state."""
    from apps_eval.cert.fec_producer import produce_fec

    a = produce_fec({"judge_versions": ["v1"]})
    b = produce_fec({"judge_versions": ["v1"]})
    assert a == b
    assert a is not b
    a["judge_calibration"]["judge_versions"].append("mutated")
    assert "mutated" not in b["judge_calibration"]["judge_versions"]


@pytest.fixture(autouse=True)
def _restore_registry():
    """Ensure tests don't leak registry state across runs."""
    from apps_shared.cert.fec_producer import clear_registry
    yield
    clear_registry()
