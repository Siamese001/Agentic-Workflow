"""W4 / G16: a whole run that authorized zero lanes surfaces an explicit BLOCK.

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

The frozen AIG/Brown failure reported aggregate disposition ``X3A`` (which normalizes to UNKNOWN —
never an allow) while every lane was ``X3_BLOCK``. ``_aggregate_x3_for_outcome`` forces an explicit
``X3_BLOCK`` for that ambiguous, unauthorized case and leaves authorized / already-explicit
dispositions untouched. Pure product-mode unit test.
"""

from __future__ import annotations

from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import _aggregate_x3_for_outcome


def test_frozen_x3a_unauthorized_forced_to_block() -> None:
    # The exact W0-frozen case: X3A (-> UNKNOWN) with no authorized lane.
    assert _aggregate_x3_for_outcome("X3A", outcome=False) == "X3_BLOCK"


def test_blank_unauthorized_forced_to_block() -> None:
    assert _aggregate_x3_for_outcome("", outcome=False) == "X3_BLOCK"
    assert _aggregate_x3_for_outcome(None, outcome=False) == "X3_BLOCK"


def test_authorized_disposition_untouched() -> None:
    assert _aggregate_x3_for_outcome("X3C", outcome=True) == "X3C"
    assert _aggregate_x3_for_outcome("X3D", outcome=True) == "X3D"


def test_explicit_block_untouched() -> None:
    assert _aggregate_x3_for_outcome("X3_BLOCK", outcome=False) == "X3_BLOCK"


def test_explicit_review_untouched() -> None:
    assert (
        _aggregate_x3_for_outcome("X3_REVIEW_JUDGE_SOFT_FAIL", outcome=False)
        == "X3_REVIEW_JUDGE_SOFT_FAIL"
    )


def test_explicit_allow_not_reclassified() -> None:
    # Only the ambiguous UNKNOWN bucket is forced to BLOCK; an explicit allow label is left as-is.
    assert _aggregate_x3_for_outcome("X3_ALLOW", outcome=False) == "X3_ALLOW"
