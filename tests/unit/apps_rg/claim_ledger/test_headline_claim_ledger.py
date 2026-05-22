"""Headline claim ledger helpers — segment coverage."""

from __future__ import annotations

from apps_rg.runtime.claim_ledger.headline_claim_ledger import build_headline_text_claim_coverage

HL = "SVP Engineering | Governed Agentic Platforms | Runtime Infrastructure | Regulated Delivery"


def test_headline_text_claim_coverage_passes_with_segment_rows() -> None:
    ledger = [
        {"claim_text": "Governed Agentic Platforms", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Runtime Infrastructure", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Regulated Delivery", "source_fact_ids": ["bul_1"]},
    ]
    doc = build_headline_text_claim_coverage(HL, ledger, {"bul_1"})
    assert doc["schema"] == "headline_text_claim_coverage_v1"
    assert doc["overall_pass"] is True
    assert len(doc["segments"]) == 3
