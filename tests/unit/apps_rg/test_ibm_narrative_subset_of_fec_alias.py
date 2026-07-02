"""ibm_narrative subset-of-FEC slot→bundle alias (typed-edge guardrails, W2.3).

The shared canonical-evidence subset gate (`x2_claim_ledger_source_fact_ids_subset_of_fec`)
aliases the IBM bullet surface (`bul_ibm_*`) to its FEC id. After the typed-edge migration the
FEC is composed of graph-era role-episode BUNDLE ids (`reb_ibm_*`), not legacy `fact_*` ids — so
the prior "first fact_* anchor" yielded None and the alias never built, failing the gate on every
cited `bul_ibm_*` (the ibm_narrative X3 blocker). The gate now aliases each slot to its canonical
bundle via IBM_BULLET_SLOT_BUNDLE_MAP when that bundle is in the FEC.
"""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.evidence.canonical_evidence_x2 import (
    append_canonical_evidence_invariant_x2_gates,
)
from apps_rg.runtime.sections.ibm_role_episode_evidence import IBM_BULLET_SLOT_BUNDLE_MAP


def _subset_pass(fec: set[str], cited: list[str]) -> bool:
    gates: list[Any] = []
    runtime_payload = {"section_id": "ibm_narrative", "allowed_fact_ids": sorted(fec)}
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids=fec,
        claim_ledger=[{"claim_text": "x", "source_fact_ids": cited}],
    )
    by_id = {g.gate_id: g.pass_ for g in gates}
    return bool(by_id.get("x2_claim_ledger_source_fact_ids_subset_of_fec"))


def test_graph_era_fec_resolves_cited_slot_to_bundle() -> None:
    b1 = IBM_BULLET_SLOT_BUNDLE_MAP["bul_ibm_001"]
    b5 = IBM_BULLET_SLOT_BUNDLE_MAP["bul_ibm_005"]
    fec = {b1, b5}  # FEC holds the bundle ids the slots map to
    assert _subset_pass(fec, ["bul_ibm_001", "bul_ibm_005"]) is True


def test_current_fec_resolves_bul_ibm_002_to_data_modeling_bundle() -> None:
    fec = {"reb_ibm_data_modeling_bi_decision_support"}
    assert IBM_BULLET_SLOT_BUNDLE_MAP["bul_ibm_002"] not in fec
    assert _subset_pass(fec, ["bul_ibm_002"]) is True


def test_slot_whose_bundle_absent_from_fec_still_fails() -> None:
    # Only bul_ibm_001's bundle is in the FEC; citing bul_ibm_005 (bundle absent) must fail.
    fec = {IBM_BULLET_SLOT_BUNDLE_MAP["bul_ibm_001"]}
    assert _subset_pass(fec, ["bul_ibm_005"]) is False
