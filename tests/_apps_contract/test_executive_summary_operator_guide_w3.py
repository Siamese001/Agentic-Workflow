"""W3 contract: operator guide documents token/regen budget ergonomics."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GUIDE = REPO / "docs" / "apps_rg" / "executive_summary_operator_guide.md"


def test_operator_guide_includes_token_regen_budget_sections() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    required = (
        "Token budget & Qwen transport",
        "APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS",
        "TOKEN_BUDGET_EXCEEDED_FIRST_PASS_85PCT",
        "provider_context_window_source",
        "Transport timeout vs budget",
        "executive_summary_qwen_call_plan.json",
        "regen_token_budget_receipt.json",
        "call_id",
        "Brown budget soak",
        "not judge-cert soak",
        "transport_timeout",
        "budget_blocked",
    )
    missing = [needle for needle in required if needle not in text]
    assert not missing, f"operator guide missing W3 sections: {missing}"
