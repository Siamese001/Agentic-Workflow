"""Unit tests for FEC bridge evidence_items filtering during materialization.

Regression guard for ed41cc822d: stray prompt-surface evidence must not widen the FEC
allowlist. Covers alias-aware admission and ``_metric_`` suffix normalization.
"""

from __future__ import annotations

from types import SimpleNamespace

from apps_rg.runtime.evidence.canonical_section_evidence_set import (
    apply_canonical_section_evidence_materialization,
    canonical_evidence_set_digest,
    collect_prompt_c0_fact_ids,
    validate_downstream_subset,
)
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH


def _pool(*, section: str, ordered: list[str], plan: dict | None = None) -> SimpleNamespace:
    digest = canonical_evidence_set_digest(ordered)
    return SimpleNamespace(
        section=section,
        allowed_fact_ids_ordered=ordered,
        allowed_fact_ids=set(ordered),
        proof_pool_digest=digest,
        proof_pool_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        proof_source=PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        selected_fact_plan=plan or {"section_id": section, "facts": []},
        proof_pool_metadata={"proof_pool_type": "augmented_skills_graph"},
    )


def _apply_with_bridge(
    *,
    section: str,
    ordered: list[str],
    fec_allowed: list[str],
    evidence_items: list[dict],
    plan: dict | None = None,
) -> dict:
    bridge_doc = {
        "allowed_fact_ids": list(ordered),
        "source_fact_ids": list(ordered),
        "evidence_items": evidence_items,
        "final_evidence_contract": {},
    }
    runtime_payload: dict = {"proof_pool_metadata": {}, "section_fec_bridge": bridge_doc}
    bridge = SimpleNamespace(bridge_doc=bridge_doc)
    apply_canonical_section_evidence_materialization(
        pool=_pool(section=section, ordered=ordered, plan=plan),  # type: ignore[arg-type]
        runtime_payload=runtime_payload,
        bridge=bridge,  # type: ignore[arg-type]
        fec_allowed=fec_allowed,
    )
    return bridge_doc


def test_materialization_keeps_metric_suffixed_evidence_when_base_in_fec() -> None:
    """Metric variants (fact_x_metric_001) stay when the base ledger id is FEC-allowed."""
    bridge_doc = _apply_with_bridge(
        section="ibm_narrative",
        ordered=["fact_quant_hpc_002", "fact_quant_hpc_003"],
        fec_allowed=["fact_quant_hpc_002"],
        evidence_items=[
            {
                "evidence_id": "evidence:section:fact_quant_hpc_002_metric_001",
                "source_fact_id": "fact_quant_hpc_002_metric_001",
            },
            {
                "evidence_id": "evidence:section:fact_quant_hpc_003",
                "source_fact_id": "fact_quant_hpc_003",
            },
        ],
    )
    kept = {it.get("source_fact_id") for it in bridge_doc["evidence_items"]}
    assert "fact_quant_hpc_002_metric_001" in kept
    assert "fact_quant_hpc_003" not in kept


def test_materialization_keeps_alias_surface_when_ledger_in_fec() -> None:
    """Surface bul_* evidence is retained when alias map resolves to an FEC-allowed fact_* id."""
    plan = {
        "section_id": "ey_bullets",
        "facts": [
            {"fact_id": "bul_ey_001", "ledger_candidate_fact_id": "fact_ey_001"},
            {"fact_id": "bul_ey_002", "ledger_candidate_fact_id": "fact_ey_002"},
        ],
    }
    bridge_doc = _apply_with_bridge(
        section="ey_bullets",
        ordered=["bul_ey_001", "bul_ey_002", "bul_ey_003", "fact_ey_001", "fact_ey_002"],
        fec_allowed=["fact_ey_001", "fact_ey_002"],
        evidence_items=[
            {"evidence_id": "evidence:section:bul_ey_001", "source_fact_id": "bul_ey_001"},
            {"evidence_id": "evidence:section:bul_ey_003", "source_fact_id": "bul_ey_003"},
        ],
        plan=plan,
    )
    kept = {it.get("source_fact_id") for it in bridge_doc["evidence_items"]}
    assert "bul_ey_001" in kept
    assert "bul_ey_003" not in kept


def test_materialization_drops_unaliased_surface_not_in_fec() -> None:
    """Without alias resolution, surface ids outside fec_allowed are removed."""
    bridge_doc = _apply_with_bridge(
        section="ey_bullets",
        ordered=["bul_ey_001", "fact_ey_001"],
        fec_allowed=["fact_ey_001"],
        evidence_items=[
            {"evidence_id": "evidence:section:bul_ey_001", "source_fact_id": "bul_ey_001"},
            {"evidence_id": "evidence:section:fact_ey_001", "source_fact_id": "fact_ey_001"},
        ],
        plan={"section_id": "ey_bullets", "facts": []},
    )
    kept = {it.get("source_fact_id") for it in bridge_doc["evidence_items"]}
    assert kept == {"fact_ey_001"}


def test_prompt_surface_stays_subset_of_fec_after_filtering() -> None:
    runtime_payload: dict = {
        "proof_pool_metadata": {},
        "section_fec_bridge": {
            "allowed_fact_ids": ["fact_a", "fact_b", "fact_stray"],
            "evidence_items": [
                {"source_fact_id": "fact_a"},
                {"source_fact_id": "fact_stray"},
            ],
        },
    }
    bridge = SimpleNamespace(bridge_doc=runtime_payload["section_fec_bridge"])
    apply_canonical_section_evidence_materialization(
        pool=_pool(section="competencies", ordered=["fact_a", "fact_b", "fact_stray"]),  # type: ignore[arg-type]
        runtime_payload=runtime_payload,
        bridge=bridge,  # type: ignore[arg-type]
        fec_allowed=["fact_a", "fact_b"],
    )
    prompt_ids = collect_prompt_c0_fact_ids(runtime_payload)
    assert prompt_ids <= {"fact_a", "fact_b"}


def test_validate_downstream_subset_accepts_metric_suffix_like_fec_filter() -> None:
    fec_ids = {"fact_quant_hpc_002"}
    ok, violations = validate_downstream_subset(
        ["fact_quant_hpc_002_metric_001", "fact_quant_hpc_003"],
        fec_ids,
        label="claim_ledger",
    )
    assert ok is False
    assert violations == ["fact_quant_hpc_003"]
    ok_metric, violations_metric = validate_downstream_subset(
        ["fact_quant_hpc_002_metric_001"],
        fec_ids,
        label="claim_ledger",
    )
    assert ok_metric is True
    assert violations_metric == []
