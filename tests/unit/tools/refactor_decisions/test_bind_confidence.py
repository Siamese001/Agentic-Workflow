"""Unit tests for bind-confidence tiering (Author-Gate learning W1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.refactor_decisions.bind_confidence import (
    BIND_DISPUTED,
    BIND_HIGH,
    BIND_LOW,
    BIND_MEDIUM,
    BindConfidenceInput,
    CI_ABSENT,
    CI_FULL,
    CI_PARTIAL,
    classify_bind_confidence,
    commit_within_binding_window,
    meaningful_file_overlap,
    parse_ci_receipt,
    refine_outcome_label_with_ci,
)

_BASE = {
    "scope_files": frozenset({"apps/foo/a.py"}),
    "commit_files": frozenset({"apps/foo/a.py"}),
    "decision_created_at_iso": "2026-05-01T12:00:00+00:00",
    "commit_timestamp_iso": "2026-05-02T12:00:00+00:00",
    "binding_window_seconds": 86400 * 14,
    "direct_sha_bind": False,
    "overlapping_commit_count": 1,
    "operator_disputed": False,
}


def test_high_full_ci_overlap_single_candidate() -> None:
    inp = BindConfidenceInput(**{**_BASE, "ci_receipt_status": CI_FULL})
    tier, echo = classify_bind_confidence(inp)
    assert tier == BIND_HIGH
    assert echo == CI_FULL


def test_medium_partial_ci() -> None:
    inp = BindConfidenceInput(**{**_BASE, "ci_receipt_status": CI_PARTIAL})
    tier, _ = classify_bind_confidence(inp)
    assert tier == BIND_MEDIUM


def test_medium_absent_ci() -> None:
    inp = BindConfidenceInput(**{**_BASE, "ci_receipt_status": CI_ABSENT})
    tier, _ = classify_bind_confidence(inp)
    assert tier == BIND_MEDIUM


def test_low_ambiguous_multiple_commits() -> None:
    inp = BindConfidenceInput(**{**_BASE, "ci_receipt_status": CI_FULL, "overlapping_commit_count": 2})
    tier, _ = classify_bind_confidence(inp)
    assert tier == BIND_LOW


def test_low_no_overlap_non_direct() -> None:
    inp = BindConfidenceInput(
        **{
            **_BASE,
            "commit_files": frozenset({"other/b.py"}),
            "ci_receipt_status": CI_FULL,
        }
    )
    tier, _ = classify_bind_confidence(inp)
    assert tier == BIND_LOW


def test_low_direct_but_missing_scope_overlap() -> None:
    inp = BindConfidenceInput(
        **{
            **_BASE,
            "commit_files": frozenset({"other/b.py"}),
            "ci_receipt_status": CI_FULL,
            "direct_sha_bind": True,
        }
    )
    tier, _ = classify_bind_confidence(inp)
    assert tier == BIND_LOW


def test_disputed_operator() -> None:
    inp = BindConfidenceInput(**{**_BASE, "ci_receipt_status": CI_FULL, "operator_disputed": True})
    tier, _ = classify_bind_confidence(inp)
    assert tier == BIND_DISPUTED


def test_parse_ci_receipt_full(tmp_path: Path) -> None:
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"complete": True, "conclusion": "success"}), encoding="utf-8")
    st, meta = parse_ci_receipt(p)
    assert st == CI_FULL
    assert meta.get("conclusion") == "success"


def test_parse_ci_receipt_absent(tmp_path: Path) -> None:
    st, meta = parse_ci_receipt(tmp_path / "missing.json")
    assert st == CI_ABSENT
    assert meta == {}


def test_refine_outcome_with_ci_failure() -> None:
    label, flags = refine_outcome_label_with_ci(
        "undecided",
        {
            "execution_completed": 1,
            "tests_passed": 0,
            "regression_found": 0,
            "rollback_required": 0,
            "promote_to_pattern": 0,
            "pattern_promotion_eligible": 0,
        },
        CI_FULL,
        {"conclusion": "failure"},
    )
    assert label == "rework"
    assert flags["regression_found"] == 1


def test_meaningful_overlap_false_on_empty_scope() -> None:
    assert not meaningful_file_overlap(frozenset(), frozenset({"a.py"}))


def test_commit_window_rejects_before_decision() -> None:
    assert not commit_within_binding_window(
        "2026-05-10T12:00:00+00:00",
        "2026-05-01T12:00:00+00:00",
        86400 * 14,
    )
