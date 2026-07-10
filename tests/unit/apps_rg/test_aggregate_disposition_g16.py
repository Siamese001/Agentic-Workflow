"""X3 remains immutable when later whole-run completion gates fail.

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

Later apps_eval, L6, promotion, or closeout failures are represented by completion status and fault.
They must not rewrite the source X3 judge decision. Pure product-mode unit test.
"""

from __future__ import annotations

from apps_rg.runtime.orchestration.r3r4_whole_run_orchestration import _aggregate_x3_for_outcome


def test_x3a_is_preserved_when_completion_is_blocked() -> None:
    assert _aggregate_x3_for_outcome("X3A", outcome=False) == "X3A"


def test_blank_source_disposition_remains_blank() -> None:
    assert _aggregate_x3_for_outcome("", outcome=False) == ""
    assert _aggregate_x3_for_outcome(None, outcome=False) == ""


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
    assert _aggregate_x3_for_outcome("X3_ALLOW", outcome=False) == "X3_ALLOW"
