"""apps-test-model: LAW.

S2C0 regressions for allocation-bound competencies evidence plumbing.
"""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    TraversalRecorder,
    build_candidate_decision,
    build_candidate_receipt,
    finalize_canonical_section_plan,
)
from apps_rg.runtime.c0.c06_weak_refine import _validate_frozen_selected_plan
from apps_rg.runtime.c0.graph_skill_embedding_allocation import (
    build_lane_embedding_allowlists,
)
from apps_rg.runtime.c0.resume_graph_claim_binding import (
    GRAPH_CLAIM_BINDINGS_ARTIFACT,
)
from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.sections.upstream_evidence_block import (
    write_required_proof_absent_artifacts,
)
from apps_rg.runtime.spine.c0_fec_compose import (
    build_spine_c0_fec_artifact,
    merge_compiled_prompt_artifact_fec_fields,
)
from apps_rg.runtime.spine.section_contract_bundles import SectionFrontSpineBridge

SECTION = "competencies"
ALLOCATION_DIGEST = "a" * 64


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _canonical_plan() -> dict[str, object]:
    path_id = "root:root_1/skill:skill_1"
    authority = {
        "authority_pass": True,
        "targeting_consulted": False,
        "authority_evaluated_before_targeting": True,
    }
    decision = build_candidate_decision(
        section_id=SECTION,
        candidate_id="skill_1",
        candidate_type="leaf_skill",
        candidate_path_id=path_id,
        decision="selected",
        reason_codes=["selected_by_authority_then_rank"],
        authority=authority,
        hop_depth=1,
        parent_id="root_1",
        root_id="root_1",
    )
    recorder = TraversalRecorder(section_id=SECTION, max_hop_depth=1)
    recorder.record(
        event_type="edge_traversed",
        hop_depth=1,
        source_node_id="root_1",
        target_node_id="skill_1",
        edge_type="role_episode_contains_skill",
        candidate_path_id=path_id,
    )
    recorder.record(
        event_type="authority_evaluated",
        hop_depth=1,
        source_node_id="root_1",
        target_node_id="skill_1",
        edge_type="role_episode_contains_skill",
        candidate_path_id=path_id,
        authority_pass=True,
    )
    recorder.record(
        event_type="candidate_terminal",
        hop_depth=1,
        source_node_id="root_1",
        target_node_id="skill_1",
        edge_type="role_episode_contains_skill",
        candidate_path_id=path_id,
        authority_pass=True,
        decision="selected",
        reason_codes=["selected_by_authority_then_rank"],
    )
    return finalize_canonical_section_plan(
        {
            "section_id": SECTION,
            "source_authority_contract": {
                "graph_digest": "graph-digest",
                "targeting_inputs_are_non_authority": True,
            },
            "facts": [
                {
                    "fact_id": "root_1",
                    "graph_skill_node_ids": ["skill_1"],
                }
            ],
            "graph_candidate_decision_ledger": [decision],
            "graph_candidate_receipt": build_candidate_receipt(
                section_id=SECTION,
                decisions=[decision],
            ),
            "graph_traversal_receipt": recorder.build_receipt(decisions=[decision]),
        }
    )


def _allocation_assignment() -> dict[str, object]:
    return {
        "section_id": SECTION,
        "claim_unit_id": "competencies:skill:01",
        "skill_id": "skill_1",
        "fact_id": "fact_1",
        "metric_outcome_id": "",
        "root_id": "root_1",
        "graph_path_ids": [
            "root:root_1",
            "root:root_1/skill:skill_1",
            "root:root_1/fact:fact_1",
        ],
        "edge_ids": ["edge:root-skill", "edge:root-fact"],
        "citation_refs": ["source:fact_1"],
    }


def _allocated_plan() -> dict[str, object]:
    source = _canonical_plan()
    source_digest = source["plan_digest"]
    enriched = dict(source)
    enriched.update(
        {
            "allocation_scope": "WHOLE_RESUME",
            "allocation_plan_id": "resume_graph_allocation:test",
            "allocation_plan_digest": ALLOCATION_DIGEST,
            "allocation_assignments": [_allocation_assignment()],
            "final_graph_evidence_contract": {
                "allocation_plan_digest": ALLOCATION_DIGEST,
                "pass": True,
            },
        }
    )
    sealed = finalize_canonical_section_plan(enriched)
    assert source["plan_digest"] == source_digest
    return sealed


def _proof_pool(plan: dict[str, object]) -> SectionProofPool:
    metadata = {
        "selected_graph_evidence_plan": plan,
        "resume_graph_allocation_scope": "WHOLE_RESUME",
        "resume_graph_allocation_plan_id": "resume_graph_allocation:test",
        "resume_graph_allocation_plan_digest": ALLOCATION_DIGEST,
        "resume_graph_global_uniqueness_claimed": True,
        "final_graph_evidence_contract_digest": "b" * 64,
        "durable_graph_state_mutated": False,
    }
    return SectionProofPool(
        section=SECTION,
        proof_source="augmented_skills_graph",
        proof_pool_ref="test",
        proof_pool_digest=str(plan["plan_digest"]),
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=["root_1", "fact_1", "skill_1"],
        allowed_fact_ids={"root_1", "fact_1", "skill_1"},
        bullet_rows=[],
        proof_pool_metadata=metadata,
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="test",
        base_resume_json_hash="0" * 64,
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )


def test_allocation_slice_reseals_plan_and_propagates_digest_to_fec_and_prompt() -> None:
    plan = _allocated_plan()

    assert _validate_frozen_selected_plan(plan, section_id=SECTION) == []
    assert finalize_canonical_section_plan(plan)["plan_digest"] == plan["plan_digest"]
    assert plan["allocation_plan_digest"] == ALLOCATION_DIGEST
    assert plan["allocation_assignments"] == [_allocation_assignment()]

    pool = _proof_pool(plan)
    front_spine = SectionFrontSpineBridge(
        section_id=SECTION,
        validated_request=None,
        l1_plan=None,
        route=object(),
        product_visible=False,
    )
    bridge = build_spine_c0_fec_artifact(
        section_id=SECTION,
        front_spine=front_spine,
        pool=pool,
    )
    runtime_payload = {
        "section_fec_bridge": bridge.bridge_doc,
        "proof_pool_metadata": pool.proof_pool_metadata,
    }
    compiled = merge_compiled_prompt_artifact_fec_fields({}, runtime_payload)

    assert bridge.bridge_doc["resume_graph_allocation_plan_digest"] == ALLOCATION_DIGEST
    assert compiled["resume_graph_allocation_plan_digest"] == ALLOCATION_DIGEST


def test_competencies_embedding_allowlist_keeps_assertion_and_fact_ids_distinct() -> None:
    allocated = _allocation_assignment()
    allocation = {
        "allocation_plan_digest": ALLOCATION_DIGEST,
        "assignments": [allocated],
    }
    candidates = {
        SECTION: [
            {
                "assertion_id": "assertion_authorized",
                "skill_id": "skill_1",
                "fact_links": ["fact_1"],
                "similarity": 0.9,
                "authority_section_id": SECTION,
                "assertion_document_sha256": "1" * 64,
                "authority_envelope_sha256": "2" * 64,
                "skill_row_sha256": "3" * 64,
            },
            {
                "assertion_id": "assertion_unallocated",
                "skill_id": "skill_unallocated",
                "fact_links": ["fact_unallocated"],
                "similarity": 0.95,
                "authority_section_id": SECTION,
                "assertion_document_sha256": "4" * 64,
                "authority_envelope_sha256": "5" * 64,
                "skill_row_sha256": "6" * 64,
            },
        ]
    }

    bundle = build_lane_embedding_allowlists(
        allocation_plan=allocation,
        candidates_by_section=candidates,
        authority_pins={"manifest_sha256": "7" * 64},
        section_order=(SECTION,),
    )
    lane = bundle["lanes"][SECTION]

    assert lane["allocation_plan_digest"] == ALLOCATION_DIGEST
    assert lane["allowlists"] == {
        "assertion_ids": ["assertion_authorized"],
        "skill_ids": ["skill_1"],
        "fact_ids": ["fact_1"],
        "metric_ids": [],
    }
    assert "assertion_authorized" not in lane["allowlists"]["fact_ids"]
    assert "fact_unallocated" not in lane["allowlists"]["fact_ids"]
    assert lane["accepted_assertion_bindings"][0]["fact_links"] == ["fact_1"]


def test_pre_provider_proof_block_does_not_add_graph_claim_binding_failure(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "lane"
    runtime_payload = {
        "run_id": "s2c0-pre-provider",
        "section_id": SECTION,
        "selected_fact_plan": _allocated_plan(),
    }

    result = write_required_proof_absent_artifacts(
        repo_root=tmp_path,
        artifact_dir=artifact_dir,
        section_id=SECTION,
        provider="external_claude",
        temperature=0.0,
        max_tokens=100,
        runtime_payload=runtime_payload,
        reason="missing authoritative proof",
    )

    provider_request = json.loads(
        (artifact_dir / "provider_request.json").read_text(encoding="utf-8")
    )
    x2 = json.loads((artifact_dir / "x2_gate_outputs.json").read_text(encoding="utf-8"))

    assert result["runtime_payload"]["blocked_before_provider"] is True
    assert provider_request["provider_attempted"] is False
    assert x2["failed_gates"] == ["x2_competencies_required_proof_present"]
    assert not (artifact_dir / GRAPH_CLAIM_BINDINGS_ARTIFACT).exists()
