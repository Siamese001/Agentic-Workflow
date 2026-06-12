"""W5 / G12: base-resume n-gram overlap is advisory (WARN mode), not a hard X2 blocker.

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

A valid graph-sourced bullet must not be blocked by base-resume n-gram overlap. The gate runs in
WARN mode by default (records the overlap for debug but never fails X2); the hard mode stays
available for explicit opt-in. Verbatim-copy + hydration-operation blockers live in separate gates
and are unaffected. Pure product-mode lock test.
"""

from __future__ import annotations

from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
    BASE_RESUME_NGRAM_THRESHOLD,
    check_bullet_base_resume_ngram_overlap,
    run_bullet_ngram_overlap_gates,
)

# An exact copy of a base-resume bullet -> 100% 4-gram overlap (well above the 25% threshold).
_BASE_TEXT = "Led the migration of forty production services to Kubernetes reducing tail latency"


def test_base_resume_ngram_is_advisory_by_default() -> None:
    result = check_bullet_base_resume_ngram_overlap("bul_ibm_1", _BASE_TEXT, [_BASE_TEXT])
    assert result.overlap_fraction > BASE_RESUME_NGRAM_THRESHOLD  # high overlap
    assert result.warn_only is True
    assert result.passed is True  # advisory -> still passes the gate
    assert result.failure_reason is not None  # ... but the overlap is recorded for debug


def test_run_gates_base_pass_true_in_warn_mode() -> None:
    bullets = [{"bullet_id": "bul_ibm_1", "bullet_text": _BASE_TEXT}]
    base_pass, base_results, _e0_pass, _e0_results = run_bullet_ngram_overlap_gates(
        bullets, section_id="ibm_bullets", base_resume_texts=[_BASE_TEXT]
    )
    assert base_pass is True  # advisory: a high-overlap bullet never blocks X2
    assert base_results and base_results[0].overlap_fraction > BASE_RESUME_NGRAM_THRESHOLD


def test_hard_mode_remains_available_for_explicit_opt_in() -> None:
    result = check_bullet_base_resume_ngram_overlap(
        "bul_ibm_1", _BASE_TEXT, [_BASE_TEXT], warn_only=False
    )
    assert result.passed is False  # hard mode still fails on high overlap (kept, not the default)
