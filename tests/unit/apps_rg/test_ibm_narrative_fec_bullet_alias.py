"""Unit tests for ibm_narrative FEC alias map injection.

Closes Bug:IbmNarrativeFecBulletAliasMissing — the ibm_narrative prompt SSOT authorizes
bul_ibm_001..005 as claim_ledger source_fact_ids, but the FEC contains only fact_* IDs.
append_canonical_evidence_invariant_x2_gates must auto-alias the IBM bullet surface to a
fact_* anchor in the FEC so the x2_claim_ledger_source_fact_ids_subset_of_fec gate passes
when Qwen complies with the prompt directive.
"""

from __future__ import annotations

from apps_rg.runtime.evidence.canonical_evidence_x2 import (
    append_canonical_evidence_invariant_x2_gates,
)
from apps_rg.runtime.validators.executive_summary_x2 import X2GateResult
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS


def _gate_pass(gates: list[X2GateResult], gate_id: str) -> bool:
    for g in gates:
        if g.gate_id == gate_id:
            return g.pass_
    raise AssertionError(f"Gate {gate_id} not emitted")


def test_ibm_narrative_alias_lets_bul_ibm_ledger_pass_fec_subset():
    runtime_payload = {
        "section_id": "ibm_narrative",
        "allowed_fact_ids": [
            "fact_consulting_001",
            "fact_governance_003",
            "fact_quant_hpc_001",
        ],
        "canonical_section_evidence_set": {
            "section_id": "ibm_narrative",
            "pool_ids_ordered": [
                "fact_consulting_001",
                "fact_governance_003",
                "fact_quant_hpc_001",
            ],
        },
    }
    claim_ledger = [
        {"claim_text": "ibm enterprise lineage", "source_fact_ids": ["bul_ibm_001", "bul_ibm_004"]},
        {"claim_text": "platform discipline", "source_fact_ids": ["bul_ibm_002"]},
    ]
    gates: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids=set(runtime_payload["allowed_fact_ids"]),
        claim_ledger=claim_ledger,
    )
    assert _gate_pass(gates, "x2_claim_ledger_source_fact_ids_subset_of_fec")


def test_non_ibm_narrative_section_does_not_alias_bul_ibm():
    runtime_payload = {
        "section_id": "executive_summary",
        "allowed_fact_ids": ["fact_consulting_001"],
        "canonical_section_evidence_set": {
            "section_id": "executive_summary",
            "pool_ids_ordered": ["fact_consulting_001"],
        },
    }
    claim_ledger = [{"claim_text": "leaked", "source_fact_ids": ["bul_ibm_001"]}]
    gates: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids={"fact_consulting_001"},
        claim_ledger=claim_ledger,
    )
    assert not _gate_pass(gates, "x2_claim_ledger_source_fact_ids_subset_of_fec")


def test_ibm_narrative_invalid_token_still_fails():
    runtime_payload = {
        "section_id": "ibm_narrative",
        "allowed_fact_ids": ["fact_consulting_001"],
        "canonical_section_evidence_set": {
            "section_id": "ibm_narrative",
            "pool_ids_ordered": ["fact_consulting_001"],
        },
    }
    claim_ledger = [
        {"claim_text": "ok", "source_fact_ids": ["bul_ibm_001"]},
        {"claim_text": "bad", "source_fact_ids": ["fact_unrelated_999"]},
    ]
    gates: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids={"fact_consulting_001"},
        claim_ledger=claim_ledger,
    )
    assert not _gate_pass(gates, "x2_claim_ledger_source_fact_ids_subset_of_fec")


def test_ibm_narrative_with_empty_fec_does_not_explode():
    runtime_payload = {
        "section_id": "ibm_narrative",
        "allowed_fact_ids": [],
        "canonical_section_evidence_set": {
            "section_id": "ibm_narrative",
            "pool_ids_ordered": [],
        },
    }
    claim_ledger = [
        {"claim_text": "x", "source_fact_ids": [IBM_BULLET_IDS[0]]},
    ]
    gates: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids=set(),
        claim_ledger=claim_ledger,
    )
    # No fact_anchor → no alias injected → ledger is not a subset → gate fails (honest)
    assert not _gate_pass(gates, "x2_claim_ledger_source_fact_ids_subset_of_fec")
