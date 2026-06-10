"""W1 contract: canonical section evidence set SSOT + cross-lane FEC invariants."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.evidence.canonical_evidence_x2 import append_canonical_evidence_invariant_x2_gates
from apps_rg.runtime.evidence.canonical_section_evidence_set import (
    PROOF_CLASS_INCOMPLETE,
    X2_BLOCK_ID_NAMESPACE_SPLIT,
    apply_canonical_section_evidence_materialization,
    build_canonical_section_evidence_set,
    canonical_evidence_set_digest,
    classify_lane_proof_bundle_completeness,
    detect_id_namespace_split_without_alias,
    materialize_fec_allowed_from_c04,
)
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    _stamp_unify_canonical_bullet_ids,
)
from apps_rg.runtime.validators.executive_summary_x2 import X2GateResult
from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
    evaluate_proof_pool_source_fact_gate,
)

REPO = Path(__file__).resolve().parents[2]


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


def test_fec_materialization_blocks_widening() -> None:
    pool = _pool(section="headline", ordered=["fact_a", "fact_b"])
    canonical = build_canonical_section_evidence_set(pool)  # type: ignore[arg-type]
    allowed, receipt = materialize_fec_allowed_from_c04(
        c04_allowed=["fact_a", "fact_b", "fact_extra"],
        canonical=canonical,
    )
    assert "fact_extra" not in allowed
    assert receipt["widening_blocked_ids"] == ["fact_extra"]


def test_downstream_widening_blocks_via_x2_gate() -> None:
    gates: list[X2GateResult] = []
    runtime_payload = {
        "allowed_fact_ids": ["fact_a"],
        "canonical_evidence_set_digest": canonical_evidence_set_digest(["fact_a"]),
        "fec_allowed_fact_ids_digest": canonical_evidence_set_digest(["fact_a"]),
        "canonical_section_evidence_set": {
            "pool_ids_ordered": ["fact_a"],
            "canonical_evidence_set_digest": canonical_evidence_set_digest(["fact_a"]),
            "id_alias_map": {},
        },
        "section_fec_bridge": {"allowed_fact_ids": ["fact_a"], "evidence_items": []},
    }
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload=runtime_payload,
        allowed_fact_ids={"fact_a"},
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["fact_b"]}],
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_source_fact_ids_subset_of_fec"].pass_ is False


def test_disjoint_namespace_without_alias_blocks() -> None:
    split, ids = detect_id_namespace_split_without_alias(
        pool_ids={"bul_unify_001"},
        fec_ids={"fact_revenue_ops_001"},
        alias_map={},
    )
    assert split is True
    assert ids

    gates: list[X2GateResult] = []
    append_canonical_evidence_invariant_x2_gates(
        gates,
        runtime_payload={
            "allowed_fact_ids": ["fact_revenue_ops_001"],
            "canonical_evidence_set_digest": canonical_evidence_set_digest(["bul_unify_001"]),
            "fec_allowed_fact_ids_digest": canonical_evidence_set_digest(["fact_revenue_ops_001"]),
            "canonical_section_evidence_set": {
                "pool_ids_ordered": ["bul_unify_001"],
                "id_alias_map": {},
            },
        },
        allowed_fact_ids={"fact_revenue_ops_001"},
        claim_ledger=[],
    )
    assert any(g.gate_id == X2_BLOCK_ID_NAMESPACE_SPLIT and not g.pass_ for g in gates)


def test_ibm_bullet_stamp_maps_ledger_to_bul_ibm() -> None:
    plan = {
        "section_id": "ibm_bullets",
        "facts": [
            {"fact_id": "fact_ibm_001", "claim_text": "a"},
            {"fact_id": "fact_ibm_002", "claim_text": "b"},
            {"fact_id": "fact_ibm_003", "claim_text": "c"},
            {"fact_id": "fact_ibm_004", "claim_text": "d"},
            {"fact_id": "fact_ibm_005", "claim_text": "e"},
        ],
    }
    stamped, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    assert stamped["facts"][0]["fact_id"] == "bul_ibm_001"
    assert stamped["facts"][0]["ledger_candidate_fact_id"] == "fact_ibm_001"
    assert "bul_ibm_001" in allowed
    ok, _, fail = evaluate_proof_pool_source_fact_gate(
        section_id="ibm_bullets",
        collected_ids=["bul_ibm_001", "bul_ibm_002"],
        allowed_fact_ids=allowed,
        proof_pool_metadata={
            "proof_pool_type": "augmented_skills_graph",
            "id_alias_map": {"bul_ibm_001": "fact_ibm_001"},
        },
    )
    assert ok, fail


@pytest.mark.parametrize(
    ("section_id", "prefix"),
    (
        ("insurtech_bullets", "bul_insurtech_"),
        ("insurtech_narrative", "bul_insurtech_"),
        ("ey_bullets", "bul_ey_"),
        ("ey_narrative", "bul_ey_"),
    ),
)
def test_role_lane_stamp_maps_ledger_to_canonical_role_bullet_ids(section_id: str, prefix: str) -> None:
    plan = {
        "section_id": section_id,
        "facts": [
            {"fact_id": f"fact_{section_id}_001", "claim_text": "a"},
            {"fact_id": f"fact_{section_id}_002", "claim_text": "b"},
            {"fact_id": f"fact_{section_id}_003", "claim_text": "c"},
        ],
    }
    stamped, ordered, allowed = _stamp_unify_canonical_bullet_ids(plan)
    assert ordered == [f"{prefix}001", f"{prefix}002", f"{prefix}003"]
    assert allowed == set(ordered)
    assert stamped["facts"][0]["fact_id"] == f"{prefix}001"
    assert stamped["facts"][0]["ledger_candidate_fact_id"] == f"fact_{section_id}_001"

    ok, receipt, fail = evaluate_proof_pool_source_fact_gate(
        section_id=section_id,
        collected_ids=[f"fact_{section_id}_001", f"{prefix}002"],
        allowed_fact_ids=allowed,
        proof_pool_metadata={
            "proof_pool_type": PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
            "id_alias_map": {
                f"{prefix}001": f"fact_{section_id}_001",
                f"{prefix}002": f"fact_{section_id}_002",
            },
        },
    )
    assert ok, fail
    assert receipt["id_alias_map"][f"{prefix}001"] == f"fact_{section_id}_001"


def test_role_lane_namespace_split_uses_alias_map() -> None:
    split, ids = detect_id_namespace_split_without_alias(
        pool_ids={"bul_insurtech_001"},
        fec_ids={"fact_insurtech_001"},
        alias_map={},
    )
    assert split is True
    assert ids

    split, ids = detect_id_namespace_split_without_alias(
        pool_ids={"bul_insurtech_001"},
        fec_ids={"fact_insurtech_001"},
        alias_map={"bul_insurtech_001": "fact_insurtech_001"},
    )
    assert split is False
    assert ids == []


def test_incomplete_lane_proof_classification(tmp_path: Path) -> None:
    run_dir = tmp_path / "lane_run"
    run_dir.mkdir()
    (run_dir / "runtime_payload.json").write_text("{}", encoding="utf-8")
    assert classify_lane_proof_bundle_completeness(run_dir) == PROOF_CLASS_INCOMPLETE


def test_apply_materialization_syncs_runtime_payload() -> None:
    pool = _pool(
        section="executive_summary",
        ordered=["fact_a", "fact_b"],
        plan={"section_id": "executive_summary", "facts": [{"fact_id": "fact_a"}]},
    )
    runtime_payload: dict = {"proof_pool_metadata": {}}
    bridge_doc = {"allowed_fact_ids": ["fact_a", "fact_b", "fact_widen"], "final_evidence_contract": {}}
    bridge = SimpleNamespace(bridge_doc=bridge_doc)
    with pytest.raises(ValueError, match="widens canonical pool"):
        apply_canonical_section_evidence_materialization(
            pool=pool,  # type: ignore[arg-type]
            runtime_payload=runtime_payload,
            bridge=bridge,  # type: ignore[arg-type]
            fec_allowed=["fact_a", "fact_b", "fact_widen"],
        )


def test_apply_materialization_filters_evidence_via_metric_suffix_and_alias() -> None:
    """Metric-suffixed source_fact_id and bul->ledger alias both admit retained FEC evidence."""
    from apps_rg.runtime.evidence.canonical_section_evidence_set import collect_prompt_c0_fact_ids

    pool = _pool(
        section="ey_bullets",
        ordered=["bul_ey_001", "bul_ey_002"],
        plan={
            "section_id": "ey_bullets",
            "facts": [
                {"fact_id": "bul_ey_001", "ledger_candidate_fact_id": "fact_ey_001"},
                {"fact_id": "bul_ey_002", "ledger_candidate_fact_id": "fact_ey_002"},
            ],
        },
    )
    bridge_doc = {
        "allowed_fact_ids": ["bul_ey_001", "bul_ey_002", "bul_ey_003"],
        "source_fact_ids": ["bul_ey_001", "bul_ey_002", "bul_ey_003"],
        "evidence_items": [
            {"evidence_id": "evidence:section:bul_ey_001", "source_fact_id": "bul_ey_001"},
            {
                "evidence_id": "evidence:section:bul_ey_002_metric",
                "source_fact_id": "bul_ey_002_metric_revenue",
            },
            {"evidence_id": "evidence:section:stray", "source_fact_id": "bul_ey_003"},
            {"evidence_id": "evidence:section:context", "source_fact_id": ""},
        ],
        "final_evidence_contract": {},
    }
    runtime_payload: dict = {"proof_pool_metadata": {}, "section_fec_bridge": bridge_doc}
    bridge = SimpleNamespace(bridge_doc=bridge_doc)
    apply_canonical_section_evidence_materialization(
        pool=pool,  # type: ignore[arg-type]
        runtime_payload=runtime_payload,
        bridge=bridge,  # type: ignore[arg-type]
        fec_allowed=["bul_ey_001", "bul_ey_002"],
    )
    kept = {it.get("source_fact_id") for it in bridge_doc["evidence_items"]}
    assert "bul_ey_003" not in kept
    assert "bul_ey_001" in kept
    assert "bul_ey_002_metric_revenue" in kept
    assert "" in kept
    prompt_ids = collect_prompt_c0_fact_ids(runtime_payload)
    assert "bul_ey_003" not in prompt_ids


def test_apply_materialization_filters_stray_evidence_items_to_fec() -> None:
    """R1 (plan apps-rg-fec-grounding-blocker-d9a4b7): evidence_items whose source_fact_id was NOT
    promoted into fec_allowed are dropped (alias-aware), so the FEC bridge prompt-surface stays a
    strict subset of the FEC. Regression for fact_quant_hpc_002 leaking past the canonical narrowing
    to _003 and tripping x2_prompt_c0_ids_subset_of_fec."""
    from apps_rg.runtime.evidence.canonical_section_evidence_set import collect_prompt_c0_fact_ids

    pool = _pool(
        section="competencies",
        ordered=["fact_a", "fact_b", "fact_stray"],
        plan={"section_id": "competencies", "facts": [{"fact_id": "fact_a"}]},
    )
    bridge_doc = {
        "allowed_fact_ids": ["fact_a", "fact_b", "fact_stray"],
        "source_fact_ids": ["fact_a", "fact_b", "fact_stray"],
        "evidence_items": [
            {"evidence_id": "evidence:section:fact_a", "source_fact_id": "fact_a"},
            {"evidence_id": "evidence:section:fact_stray", "source_fact_id": "fact_stray"},
            {"evidence_id": "evidence:section:context", "source_fact_id": ""},  # context, kept
        ],
        "final_evidence_contract": {},
    }
    runtime_payload: dict = {"proof_pool_metadata": {}, "section_fec_bridge": bridge_doc}
    bridge = SimpleNamespace(bridge_doc=bridge_doc)
    apply_canonical_section_evidence_materialization(
        pool=pool,  # type: ignore[arg-type]
        runtime_payload=runtime_payload,
        bridge=bridge,  # type: ignore[arg-type]
        fec_allowed=["fact_a", "fact_b"],  # canonical narrowing drops fact_stray
    )
    kept = {it.get("source_fact_id") for it in bridge_doc["evidence_items"]}
    assert "fact_stray" not in kept  # stray (non-FEC) evidence item dropped
    assert "fact_a" in kept and "" in kept  # allowed fact + non-claim context retained
    prompt_ids = collect_prompt_c0_fact_ids(runtime_payload)
    assert "fact_stray" not in prompt_ids  # prompt surface no longer widens the FEC
    assert prompt_ids <= {"fact_a", "fact_b"}


def test_materialization_carries_role_lane_alias_map_into_metadata() -> None:
    pool = _pool(
        section="ey_bullets",
        ordered=["bul_ey_001", "bul_ey_002", "bul_ey_003"],
        plan={
            "section_id": "ey_bullets",
            "facts": [
                {"fact_id": "bul_ey_001", "ledger_candidate_fact_id": "fact_ey_001"},
                {"fact_id": "bul_ey_002", "ledger_candidate_fact_id": "fact_ey_002"},
                {"fact_id": "bul_ey_003", "ledger_candidate_fact_id": "fact_ey_003"},
            ],
        },
    )
    runtime_payload: dict = {"proof_pool_metadata": {}}
    apply_canonical_section_evidence_materialization(
        pool=pool,  # type: ignore[arg-type]
        runtime_payload=runtime_payload,
        bridge=None,
    )
    meta = runtime_payload["proof_pool_metadata"]
    assert meta["id_alias_map"] == {
        "bul_ey_001": "fact_ey_001",
        "bul_ey_002": "fact_ey_002",
        "bul_ey_003": "fact_ey_003",
    }
    assert meta["canonical_section_evidence_set"]["id_alias_map"] == meta["id_alias_map"]


@pytest.mark.parametrize(
    "section_id",
    (
        "executive_summary",
        "headline",
        "competencies",
        "unify_bullets",
        "unify_narrative",
        "ibm_bullets",
        "ibm_narrative",
    ),
)
def test_materialize_digest_stable_per_section(section_id: str) -> None:
    ordered = [f"fact_{section_id}_001", f"fact_{section_id}_002"]
    pool = _pool(section=section_id, ordered=ordered)
    canonical = build_canonical_section_evidence_set(pool)  # type: ignore[arg-type]
    allowed, _ = materialize_fec_allowed_from_c04(c04_allowed=list(ordered), canonical=canonical)
    assert canonical_evidence_set_digest(allowed) == canonical.pool_digest


def test_digest_chain_load_json_returns_runtime_payload(tmp_path: Path) -> None:
    from apps_rg.runtime.evidence.canonical_evidence_digest_chain import (
        _load_json,
        build_canonical_evidence_digest_chain,
    )

    ids = ["fact_a", "fact_b"]
    digest = canonical_evidence_set_digest(ids)
    payload = {
        "allowed_fact_ids": ids,
        "canonical_evidence_set_digest": digest,
        "canonical_section_evidence_set": {"pool_ids_ordered": ids},
    }
    (tmp_path / "runtime_payload.json").write_text(json.dumps(payload), encoding="utf-8")
    loaded = _load_json(tmp_path / "runtime_payload.json")
    assert isinstance(loaded, dict)
    chain = build_canonical_evidence_digest_chain(tmp_path, section_id="headline")
    assert chain["c05_canonical_evidence_ids"] == ids
    assert chain["c06_fec_ids"] == ids
    assert chain["c05_canonical_evidence_digest"] == digest
