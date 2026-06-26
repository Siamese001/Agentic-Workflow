"""Unit tests: authorized deterministic rewrite operations must not block product quality PASS.

Regression guard for the stress-test finding that finalize_competencies_v3_output and
repair_protected_unify_bullet_metrics were incorrectly triggering ledger_blocks_product_pass.
"""
from __future__ import annotations

from apps_rg.runtime.section_repair_ledger import (
    KIND_DETERMINISTIC_REWRITE,
    KIND_MECHANICAL,
    ledger_blocks_product_pass,
)


def _make_ledger(*, operations: list[tuple], product_fail_closed: bool = True) -> dict:
    """Build a minimal repair ledger with given operations.

    Each entry is (kind, operation, replaced_l2[, detail]).
    """
    repairs = [
        {
            "kind": row[0],
            "operation": row[1],
            "replaced_l2": row[2],
            **({"detail": row[3]} if len(row) > 3 else {}),
        }
        for row in operations
    ]
    return {
        "product_fail_closed": product_fail_closed,
        "authoritative_attempt_number": 1,
        "attempt_1_x2_failed": False,
        "x2_runs": [{"run": 1, "after_l2_source": "initial_llm", "failed_gate_ids": [], "passed": True}],
        "repairs": repairs,
    }


def test_finalize_competencies_v3_output_is_authorized() -> None:
    ledger = _make_ledger(
        operations=[
            (KIND_MECHANICAL, "competencies_pre_x2_deterministic_pipeline", False),
            (KIND_DETERMINISTIC_REWRITE, "finalize_competencies_v3_output", True),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert not blocked, (
        f"finalize_competencies_v3_output is an authorized deterministic op — must NOT block. "
        f"Got reason: {reason!r}"
    )


def test_repair_protected_unify_bullet_metrics_is_authorized() -> None:
    ledger = _make_ledger(
        operations=[
            (KIND_DETERMINISTIC_REWRITE, "repair_protected_unify_bullet_metrics", True),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert not blocked, (
        f"repair_protected_unify_bullet_metrics is an authorized deterministic op — must NOT block. "
        f"Got reason: {reason!r}"
    )


def test_repair_required_brushstroke_citation_is_authorized() -> None:
    ledger = _make_ledger(
        operations=[
            (KIND_DETERMINISTIC_REWRITE, "repair_required_brushstroke_citation", True),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert not blocked, (
        f"repair_required_brushstroke_citation is ledger-only and authorized. "
        f"Got reason: {reason!r}"
    )


def test_repair_exec_summary_thin_sentence_weave_is_authorized() -> None:
    ledger = _make_ledger(
        operations=[
            (KIND_DETERMINISTIC_REWRITE, "repair_exec_summary_thin_sentence_weave", True),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert not blocked, (
        f"repair_exec_summary_thin_sentence_weave is deterministic density repair. "
        f"Got reason: {reason!r}"
    )


def test_graph_only_quality_repair_without_explicit_repair_receipt_blocks() -> None:
    ledger = _make_ledger(
        operations=[
            (KIND_DETERMINISTIC_REWRITE, "graph_only_generation_quality_repair", True),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked, (
        f"graph_only_generation_quality_repair requires explicit repair receipt. Got reason: {reason!r}"
    )


def test_graph_only_quality_repair_with_explicit_repair_receipt_is_authorized() -> None:
    ledger = _make_ledger(
        operations=[
            (
                KIND_DETERMINISTIC_REWRITE,
                "graph_only_generation_quality_repair",
                True,
                {
                    "repair_mode": "explicit_graph_only_repair",
                    "explicit_repair_mode": True,
                    "evidence_authority": "augmented_skills_graph",
                },
            ),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert not blocked, (
        f"graph_only_generation_quality_repair with explicit receipt must not block. Got reason: {reason!r}"
    )


def test_graph_only_display_repair_with_explicit_repair_receipt_is_authorized() -> None:
    ledger = _make_ledger(
        operations=[
            (
                KIND_DETERMINISTIC_REWRITE,
                "graph_only_display_authority_fallback",
                True,
                {
                    "repair_mode": "explicit_graph_only_repair",
                    "explicit_repair_mode": True,
                    "evidence_authority": "augmented_skills_graph",
                },
            ),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert not blocked, (
        f"graph_only_display_authority_fallback with explicit receipt must not block. Got reason: {reason!r}"
    )


def test_unknown_deterministic_rewrite_still_blocks() -> None:
    ledger = _make_ledger(
        operations=[
            (KIND_DETERMINISTIC_REWRITE, "some_ad_hoc_unauthorized_repair", True),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked, "Unknown deterministic rewrites must still block product quality PASS"
    assert "some_ad_hoc_unauthorized_repair" in reason


def test_all_authorized_ops_together_do_not_block() -> None:
    ledger = _make_ledger(
        operations=[
            (
                KIND_DETERMINISTIC_REWRITE,
                "graph_only_generation_quality_repair",
                True,
                {
                    "repair_mode": "explicit_graph_only_repair",
                    "explicit_repair_mode": True,
                    "evidence_authority": "augmented_skills_graph",
                },
            ),
            (KIND_DETERMINISTIC_REWRITE, "finalize_competencies_v3_output", True),
            (KIND_DETERMINISTIC_REWRITE, "repair_protected_unify_bullet_metrics", True),
            (KIND_DETERMINISTIC_REWRITE, "repair_required_brushstroke_citation", True),
            (KIND_DETERMINISTIC_REWRITE, "repair_exec_summary_thin_sentence_weave", True),
        ]
    )
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert not blocked, (
        f"All three authorized ops together must not block. Got reason: {reason!r}"
    )


def test_null_ledger_never_blocks() -> None:
    blocked, reason = ledger_blocks_product_pass(None)
    assert not blocked


def test_product_fail_open_never_blocks() -> None:
    ledger = _make_ledger(
        operations=[(KIND_DETERMINISTIC_REWRITE, "some_unauthorized_op", True)],
        product_fail_closed=False,
    )
    blocked, _ = ledger_blocks_product_pass(ledger)
    assert not blocked, "product_fail_closed=False must skip all checks"
