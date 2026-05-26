"""G1 ledger metric sync — deterministic fail-closed repair (plan f8a3c2 W2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.executive_summary_judge_regen_loop import (
    sync_claim_ledger_metrics_from_facts,
)


def _gov_fact() -> dict:
    return {
        "fact_id": "fact_governance_003",
        "claim_text": (
            "Basel III / CCAR data lineage, cataloging, and automated validation "
            "frameworks that cut regulatory reporting errors by 40%."
        ),
        "metric_raw": "40% reporting errors",
    }


def test_g1_repairs_claim_text_10_to_40_single_source() -> None:
    parsed = {
        "resume_display_text": (
            "Basel III and CCAR data lineage frameworks cut regulatory reporting errors by 40%."
        ),
        "claim_ledger": [
            {
                "claim_id": "exec_summary_claim_3",
                "claim": "Cut regulatory reporting errors by 40%",
                "claim_text": (
                    "Implemented Basel III / CCAR data lineage, cataloging, and automated "
                    "validation frameworks that cut regulatory reporting errors by 10%."
                ),
                "source_fact_ids": ["fact_governance_003"],
            },
        ],
    }
    out, receipt = sync_claim_ledger_metrics_from_facts(
        parsed,
        plan_facts=[_gov_fact()],
        allowed_fact_ids={"fact_governance_003"},
    )
    assert receipt["passed"] is True
    assert receipt["reject_gate"] is None
    assert receipt["repairs_applied"] == 1
    row = out["claim_ledger"][0]
    assert "10%" not in row["claim_text"].lower()
    assert "40%" in row["claim_text"].lower()
    assert receipt["row_repairs"][0]["before_metric"] == "10%"
    assert receipt["row_repairs"][0]["after_metric"] == "40%"
    assert receipt["row_repairs"][0]["source_fact_id"] == "fact_governance_003"


def test_g1_ambiguous_conflicting_facts_rejects() -> None:
    parsed = {
        "resume_display_text": "Summary with mixed metrics.",
        "claim_ledger": [
            {
                "claim_text": "Cut errors by 10%.",
                "source_fact_ids": ["fact_a", "fact_b"],
            },
        ],
    }
    facts = [
        {"fact_id": "fact_a", "metric_raw": "10% reduction"},
        {"fact_id": "fact_b", "metric_raw": "40% reduction"},
    ]
    out, receipt = sync_claim_ledger_metrics_from_facts(
        parsed,
        plan_facts=facts,
        allowed_fact_ids={"fact_a", "fact_b"},
    )
    assert receipt["passed"] is False
    assert receipt["reject_gate"] == "ledger_metric_sync_ambiguous"
    assert out["claim_ledger"][0]["claim_text"] == "Cut errors by 10%."


def test_g1_brown_070105_claim_ledger_fixture() -> None:
    fixture = (
        Path(__file__).resolve().parents[3]
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "executive_summary"
        / "real"
        / "exec_summary_20260526_070105"
        / "claim_ledger.json"
    )
    if not fixture.is_file():
        pytest.skip(f"missing fixture: {fixture}")
    ledger = json.loads(fixture.read_text(encoding="utf-8"))
    allowed: set[str] = set()
    for row in ledger:
        for fid in row.get("source_fact_ids") or []:
            allowed.add(str(fid))
    parsed = {
        "resume_display_text": (
            "Building on that operating model, Basel III and CCAR data lineage frameworks "
            "cut regulatory reporting errors by 40%."
        ),
        "claim_ledger": ledger,
    }
    facts = [_gov_fact()]
    for fid in sorted(allowed - {"fact_governance_003"}):
        facts.append({"fact_id": fid, "metric_raw": "40%", "claim_text": "Supported metric 40%."})
    out, receipt = sync_claim_ledger_metrics_from_facts(
        parsed,
        plan_facts=facts,
        allowed_fact_ids=allowed,
    )
    assert receipt["passed"] is True
    row = out["claim_ledger"][2]
    assert "10%" not in str(row.get("claim_text") or "").lower()
    assert "40%" in str(row.get("claim_text") or "").lower()
