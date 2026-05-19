"""IBM canonical hydration when graph-skills authority emits fact_* claim ids."""
from __future__ import annotations

from apps_rg.runtime.sections.ibm_canonical_hydration import (
    align_ibm_narrative_claim_ledger_to_bul_ibm,
    should_hydrate_ibm_bullets_from_canonical,
)
from apps_rg.runtime.validators.ibm_narrative_x2 import ibm_narrative_material_fact_ids_for_sentence


def test_should_hydrate_graph_pool_when_ledger_lacks_bul_ibm() -> None:
    parsed = {
        "bullets": [
            {
                "bullet_id": "bul_ibm_001",
                "bullet_text": "Wrong metrics only 20%.",
                "source_fact_ids": ["fact_partnerships_gtm_002"],
            }
        ],
        "claim_ledger": [
            {
                "claim_text": "Wrong metrics only 20%.",
                "source_fact_ids": ["fact_partnerships_gtm_002"],
            }
        ],
    }
    runtime_payload = {
        "proof_pool_metadata": {"claim_evidence_source_type": "augmented_skills_graph"},
        "selected_fact_plan": {"facts": [{"fact_id": "fact_partnerships_gtm_002"}]},
    }
    assert should_hydrate_ibm_bullets_from_canonical(runtime_payload, parsed) is True


def test_align_narrative_ledger_replaces_fact_ids_with_bul_ibm() -> None:
    sentence = (
        "At IBM, led enterprise-scale cloud, data, lineage and observability initiatives "
        "for regulated financial services."
    )
    parsed = {
        "narrative_sentence": sentence,
        "claim_ledger": [
            {
                "claim_text": sentence.rstrip("."),
                "source_fact_ids": ["fact_consulting_001", "fact_governance_003"],
            }
        ],
    }
    themes = ibm_narrative_material_fact_ids_for_sentence(sentence)
    align_ibm_narrative_claim_ledger_to_bul_ibm(
        parsed,
        narrative_sentence=sentence,
        allowed_fact_ids={"bul_ibm_001", "bul_ibm_004", "fact_consulting_001"},
    )
    src = parsed["claim_ledger"][0]["source_fact_ids"]
    assert all(str(s).startswith("bul_ibm_") for s in src)
    assert themes.issubset(set(src)) or src
