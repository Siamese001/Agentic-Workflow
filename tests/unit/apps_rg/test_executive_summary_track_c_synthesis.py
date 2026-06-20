"""Track C: exec-summary synthesis enforcement (graph-only, stacking, conflation)."""

from __future__ import annotations

from apps_rg.runtime.section_repair_policy import graph_only_reformat_allowed
from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
    apply_graph_only_generation_quality_repair,
    detect_graph_only_synthesis_violations,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_cross_fact_display_conflation,
    check_exec_summary_mechanical_opener_stack,
)


def test_graph_only_reformat_allowed_on_product_fail_closed(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_GRAPH_ONLY_REPAIR_MODE", raising=False)
    assert graph_only_reformat_allowed() is False
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_GRAPH_ONLY_REPAIR_MODE", "1")
    assert graph_only_reformat_allowed() is True


def test_mechanical_opener_stack_fails_three_led_style() -> None:
    text = (
        "Led platform work. Successfully scaled teams. Also re-architected analytics. "
        "Built quantitative depth."
    )
    ok, reason = check_exec_summary_mechanical_opener_stack(text)
    assert ok is False
    assert reason and "mechanical_opener_stack" in reason


def test_cross_fact_conflation_detects_platform_and_governance() -> None:
    resume = (
        "Led the creation of a governed enterprise AI platform, reducing regulatory "
        "reporting errors by 40% and expanding gross margins by 20%."
    )
    ledger = [
        {
            "claim_text": resume,
            "source_fact_ids": [
                "fact_engineering_platform_001",
                "fact_governance_003",
                "fact_engineering_platform_006",
            ],
        }
    ]
    ok, reason = check_cross_fact_display_conflation(resume, ledger)
    assert ok is False
    assert reason and "conflation" in reason


def test_graph_only_repair_applies_on_conflation() -> None:
    parsed = {
        "resume_display_text": (
            "Led the creation of a governed enterprise AI platform, reducing regulatory "
            "reporting errors by 40%."
        ),
        "claim_ledger": [
            {
                "claim_text": "Led the creation of a governed enterprise AI platform, reducing regulatory reporting errors by 40%.",
                "source_fact_ids": ["fact_engineering_platform_001", "fact_governance_003"],
            }
        ],
    }
    plan_facts = [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Designed governed agentic AI platform capabilities.",
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Implemented Basel III / CCAR frameworks that cut reporting errors by 40%.",
            "metric_raw": "40% reporting error reduction",
        },
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": "Productized primitives, $22M revenue, 20% margins.",
            "metric_raw": "$22M IP-led revenue|20% gross margin expansion",
        },
        {"fact_id": "fact_exec_002", "claim_text": "Scaled ML org 8 to 28.", "metric_raw": "team 8 to 28"},
    ]
    allowed = {f["fact_id"] for f in plan_facts}
    needs, _ = detect_graph_only_synthesis_violations(
        parsed, allowed_fact_ids=allowed, plan_facts=plan_facts
    )
    assert needs is True
    out, meta = apply_graph_only_generation_quality_repair(
        parsed, allowed_fact_ids=allowed, plan_facts=plan_facts
    )
    assert meta.get("applied") is True
    assert "Basel III" in out["resume_display_text"]
    lowered = out["resume_display_text"].lower()
    assert "agentic ai" in lowered or "governed enterprise" in lowered
    ok, _ = check_cross_fact_display_conflation(
        out["resume_display_text"], out["claim_ledger"]
    )
    assert ok is True
