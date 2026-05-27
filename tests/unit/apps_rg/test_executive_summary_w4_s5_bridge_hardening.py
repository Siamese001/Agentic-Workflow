"""W4 — S5 derivatives inventory + stock bridge hardening (plan exec-summary-s5-bridge-hardening-acc0f0)."""

from __future__ import annotations

import pytest

from apps_rg.runtime.sections.executive_summary_pa import format_selected_facts_for_c0
from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_stock_bridge_count


# ---------------------------------------------------------------------------
# Test 1: format_selected_facts_for_c0 must NOT emit "derivatives pricing"
#         for fact_quant_hpc_003 via any path.
# ---------------------------------------------------------------------------

def _make_fact(fact_id: str, claim_text: str, **kw) -> dict:
    return {"fact_id": fact_id, "claim_text": claim_text, **kw}


_QUANT_HPC_003_RAW_CLAIM = (
    "Built quantitative rigor through derivatives pricing, capital modeling, and portfolio "
    "stress analytics across early-career actuarial roles."
)

_QUANT_HPC_001_CLAIM = (
    "Re-architected monolithic risk analytics with containerized microservices and HPC, "
    "trimming calculation or stress-testing cycles by 40% and enabling real-time stress testing."
)


def test_format_selected_facts_for_c0_excludes_derivatives_phrase():
    """C0 DISPLAY_OVERRIDE text for fact_quant_hpc_003 must not expose 'derivatives pricing'."""
    facts = [
        _make_fact("fact_quant_hpc_003", _QUANT_HPC_003_RAW_CLAIM),
        _make_fact("fact_quant_hpc_001", _QUANT_HPC_001_CLAIM, metric_raw="40% faster calculations"),
    ]
    allowed = ["fact_quant_hpc_003", "fact_quant_hpc_001"]
    c0 = format_selected_facts_for_c0(facts, allowed)
    # The display override text must NOT contain "derivatives pricing"
    assert "[DISPLAY_OVERRIDE: use exactly this text]" in c0, "Override label must be present."
    # Extract the display override line for fact_quant_hpc_003
    for line in c0.splitlines():
        if "fact_quant_hpc_003" in line and "[DISPLAY_OVERRIDE" in line:
            assert "derivatives pricing" not in line, (
                f"Display override text must not contain 'derivatives pricing'. Got line:\n{line}"
            )
            break
    else:
        raise AssertionError("fact_quant_hpc_003 DISPLAY_OVERRIDE line not found in C0 output.")


def test_format_selected_facts_for_c0_preferred_display_text_field_takes_priority():
    """preferred_c0_display_text on the fact dict wins over both override dict and claim_text."""
    custom_framing = "Graph-node-level framing text: FSA foundation for quantitative rigor."
    facts = [
        _make_fact(
            "fact_quant_hpc_003",
            _QUANT_HPC_003_RAW_CLAIM,
            preferred_c0_display_text=custom_framing,
        ),
    ]
    c0 = format_selected_facts_for_c0(facts, ["fact_quant_hpc_003"])
    assert custom_framing in c0, "Graph-node preferred_c0_display_text must appear in C0 output."
    # Display override line must not contain "derivatives pricing" in the display text portion
    for line in c0.splitlines():
        if "fact_quant_hpc_003" in line and "[DISPLAY_OVERRIDE" in line:
            assert "derivatives pricing" not in line, (
                f"Display override line must not contain 'derivatives pricing'. Got:\n{line}"
            )
            break


# ---------------------------------------------------------------------------
# Test 2: composition plan emits s4_opener_directive for SVP lane ≥3 brushstrokes.
# ---------------------------------------------------------------------------

def _make_brushstroke(bid: str) -> dict:
    return {"brushstroke_id": bid, "required_fact_ids": [], "image_goal": f"goal for {bid}"}


def test_composition_plan_s4_opener_directive_svp_lane():
    """format_composition_plan_for_pa must emit s4_opener_directive when SVP lane + ≥3 brushstrokes."""
    from apps_rg.runtime.sections.executive_summary_composition import format_composition_plan_for_pa

    plan = {
        "schema": "executive_summary_composition_plan_v1",
        "dominant_arc": "B2_governed_platform_system",
        "target_picture": "SVP IT strategy arc",
        "strategy_executive": True,
        "brushstrokes": [
            _make_brushstroke("B1_executive_identity"),
            _make_brushstroke("B2_governed_platform_system"),
            _make_brushstroke("B3_control_evidence_discipline"),
            _make_brushstroke("B4_business_role_fit"),
        ],
        "s5_metric_binding": {
            "metric_display_fact_id": "fact_quant_hpc_001",
            "credential_fact_id": "fact_quant_hpc_003",
            "display_metric_required": True,
        },
    }
    block = format_composition_plan_for_pa(plan)
    assert "s4_opener_directive" in block, (
        f"s4_opener_directive must appear in composition block for SVP lane with ≥3 brushstrokes.\n{block}"
    )
    assert "non-stock opener" in block


def test_composition_plan_no_s4_directive_when_fewer_than_3_brushstrokes():
    """s4_opener_directive must NOT fire for plans with < 3 brushstrokes (no triple-stack risk)."""
    from apps_rg.runtime.sections.executive_summary_composition import format_composition_plan_for_pa

    plan = {
        "schema": "executive_summary_composition_plan_v1",
        "dominant_arc": "B2_governed_platform_system",
        "target_picture": "short arc",
        "strategy_executive": True,
        "brushstrokes": [
            _make_brushstroke("B1_executive_identity"),
            _make_brushstroke("B2_governed_platform_system"),
        ],
    }
    block = format_composition_plan_for_pa(plan)
    assert "s4_opener_directive" not in block


# ---------------------------------------------------------------------------
# Test 3: stock bridge gate regression — exact failing text from run 074803.
# ---------------------------------------------------------------------------

_FAILING_PARAGRAPH_074803 = (
    "Enterprise technology leader who unifies governed AI platforms, regulatory lineage, and "
    "commercialization into one IT strategy and innovation agenda for decentralized regulated enterprises. "
    "From that platform footprint, platform commercialization generated $22M in IP-led revenue and expanded "
    "gross margins by 20% while scaling the ML engineering organization from 8 to 28 specialists. "
    "Against that lineage backdrop, Basel III and CCAR data lineage, cataloging, and automated validation "
    "frameworks cut regulatory reporting errors by 40%. "
    "Complementing that regulatory foundation, re-architected monolithic risk analytics with containerized "
    "HPC microservices, trimming stress-testing cycles by 40% and enabling real-time stress testing. "
    "Built quantitative rigor through derivatives pricing, capital modeling, and portfolio stress analytics "
    "across early-career actuarial roles. "
    "Innovation incubation and architecture standards can federate governed platform capabilities across "
    "autonomous business units without weakening Basel III lineage controls."
)


def test_stock_bridge_gate_regression_triple_stack():
    """Exact failing paragraph from exec_summary_20260527_074803 must fail the stock bridge gate."""
    ok, reason = check_exec_summary_stock_bridge_count(_FAILING_PARAGRAPH_074803, max_bridges=2)
    assert not ok, "Gate should fail on triple stock bridge stack."
    assert reason is not None
    assert "stock_bridge_stack:3" in str(reason), f"Expected 3-bridge count in reason. Got: {reason}"
    assert "from that" in str(reason)
    assert "against that" in str(reason)
    assert "complementing that" in str(reason)
