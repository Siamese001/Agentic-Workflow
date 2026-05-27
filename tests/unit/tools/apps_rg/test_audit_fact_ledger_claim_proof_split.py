"""Tests for fail-closed claim/proof split ledger audit tool (W2.3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.apps_rg import audit_fact_ledger_claim_proof_split as audit_mod


def _minimal_ledger_fact(
    *,
    fact_id: str,
    claim_text: str,
    proof_text: str | None = None,
) -> dict:
    row = {
        "candidate_fact_id": fact_id,
        "claim_text": claim_text,
        "confidence": "HIGH",
        "source_resume_variants": ["base"],
        "role_families_supported": ["it_strategy"],
    }
    if proof_text is not None:
        row["proof_text"] = proof_text
    return row


def test_audit_facts_passes_clean_rows() -> None:
    facts = [
        {
            "candidate_fact_id": "fact_exec_002",
            "claim_text": "Governed platform delivery with audit-ready execution.",
            "proof_text": "Full provenance with mechanism inventory not shown to reader.",
        },
        {
            "candidate_fact_id": "fact_no_split_yet",
            "claim_text": "Claim without proof_text field yet.",
        },
    ]
    failures, total = audit_mod._audit_facts(facts)
    assert total == 2
    assert failures == []


def test_audit_facts_flags_banned_claim_and_missing_claim() -> None:
    facts = [
        {
            "candidate_fact_id": "fact_bad_mechanism",
            "claim_text": (
                "Uses deterministic routing, multi-agent orchestration, graphrag, "
                "sandboxed execution, validation controls."
            ),
            "proof_text": "provenance",
        },
        {"candidate_fact_id": "fact_empty", "claim_text": "  "},
        "not_a_dict",
    ]
    failures, total = audit_mod._audit_facts(facts)
    assert total == 3
    assert len(failures) == 3
    by_id = {f.get("candidate_fact_id"): f for f in failures if isinstance(f, dict)}
    assert "mechanism_inventory_chain_hits" in " ".join(by_id["fact_bad_mechanism"]["issues"])
    assert "missing_claim_text" in by_id["fact_empty"]["issues"]


def test_main_json_exit_code_on_fixture_ledger(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(
        json.dumps(
            {
                "candidate_facts": [
                    _minimal_ledger_fact(
                        fact_id="fact_ok",
                        claim_text="Clean display claim.",
                        proof_text="Longer provenance body.",
                    ),
                    _minimal_ledger_fact(
                        fact_id="fact_bad",
                        claim_text="Same",
                        proof_text="Same",
                    ),
                ]
            }
        ),
        encoding="utf-8",
    )
    assert audit_mod.main(["--ledger", str(ledger), "--json"]) == 1


def test_main_passes_clean_fixture_ledger(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger_clean.json"
    ledger.write_text(
        json.dumps(
            {
                "candidate_facts": [
                    _minimal_ledger_fact(
                        fact_id="fact_ok",
                        claim_text="Clean display claim.",
                        proof_text="Longer provenance body.",
                    ),
                ]
            }
        ),
        encoding="utf-8",
    )
    assert audit_mod.main(["--ledger", str(ledger), "--json"]) == 0
