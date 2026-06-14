"""Wave 4.2 — unit tests for apps_rg.runtime.aggregation.warn_policy.

Covers the WARN-handling policy for cross-section X2 vs product ALLOW:
structural assembly tolerates WARN but blocks FAIL/UNKNOWN, while product ALLOW
requires every gate PASS.
"""

from __future__ import annotations

from apps_rg.runtime.aggregation.cross_section_x2 import (
    VERDICT_FAIL,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_WARN,
    CrossSectionGateResult,
)
from apps_rg.runtime.aggregation.warn_policy import (
    POLICY_SCHEMA,
    cross_section_product_pass,
    cross_section_structural_pass,
    evaluate_warn_policy,
)


def _g(gate_id: str, verdict: str) -> CrossSectionGateResult:
    return CrossSectionGateResult(gate_id=gate_id, verdict=verdict)


class TestCrossSectionStructuralPass:
    def test_all_pass(self) -> None:
        assert cross_section_structural_pass([_g("a", VERDICT_PASS)]) is True

    def test_warn_does_not_block_structural(self) -> None:
        assert cross_section_structural_pass([_g("a", VERDICT_WARN)]) is True

    def test_fail_blocks_structural(self) -> None:
        assert cross_section_structural_pass([_g("a", VERDICT_FAIL)]) is False

    def test_unknown_blocks_structural(self) -> None:
        assert cross_section_structural_pass([_g("a", VERDICT_UNKNOWN)]) is False

    def test_empty_passes(self) -> None:
        assert cross_section_structural_pass([]) is True


class TestCrossSectionProductPass:
    def test_all_pass(self) -> None:
        assert cross_section_product_pass([_g("a", VERDICT_PASS)]) is True

    def test_warn_blocks_product(self) -> None:
        assert cross_section_product_pass([_g("a", VERDICT_WARN)]) is False

    def test_fail_blocks_product(self) -> None:
        assert cross_section_product_pass([_g("a", VERDICT_FAIL)]) is False

    def test_unknown_blocks_product(self) -> None:
        assert cross_section_product_pass([_g("a", VERDICT_UNKNOWN)]) is False

    def test_empty_is_vacuously_true(self) -> None:
        assert cross_section_product_pass([]) is True


class TestEvaluateWarnPolicy:
    def test_schema_and_static_rules(self) -> None:
        out = evaluate_warn_policy(cross_gates=[])
        assert out["schema"] == POLICY_SCHEMA
        assert out["rules"]["WARN_never_counts_as_PASS_for_product"] is True
        assert out["rules"]["FAIL_and_UNKNOWN_block_structural_and_product"] is True

    def test_warn_only_structural_eligible_product_blocked(self) -> None:
        out = evaluate_warn_policy(cross_gates=[_g("w1", VERDICT_WARN)])
        assert out["warn_gate_ids"] == ["w1"]
        assert out["structural_cross_section_eligible"] is True
        assert out["rules"]["WARN_permitted_for_structural_assembly"] is True
        assert out["product_allow_blocked_by_cross_section"] is True

    def test_fail_blocks_structural_and_product(self) -> None:
        out = evaluate_warn_policy(cross_gates=[_g("f1", VERDICT_FAIL)])
        assert out["fail_gate_ids"] == ["f1"]
        assert out["structural_cross_section_eligible"] is False
        assert out["product_allow_blocked_by_cross_section"] is True

    def test_unknown_collected_and_blocks(self) -> None:
        out = evaluate_warn_policy(cross_gates=[_g("u1", VERDICT_UNKNOWN)])
        assert out["unknown_gate_ids"] == ["u1"]
        assert out["structural_cross_section_eligible"] is False

    def test_all_pass_not_blocked(self) -> None:
        out = evaluate_warn_policy(cross_gates=[_g("p1", VERDICT_PASS)])
        assert out["product_allow_blocked_by_cross_section"] is False
        assert out["structural_cross_section_eligible"] is True
        assert out["warn_gate_ids"] == []

    def test_mixed_collects_all_categories(self) -> None:
        out = evaluate_warn_policy(
            cross_gates=[
                _g("p", VERDICT_PASS),
                _g("w", VERDICT_WARN),
                _g("f", VERDICT_FAIL),
                _g("u", VERDICT_UNKNOWN),
            ]
        )
        assert out["warn_gate_ids"] == ["w"]
        assert out["fail_gate_ids"] == ["f"]
        assert out["unknown_gate_ids"] == ["u"]
        assert out["structural_cross_section_eligible"] is False
