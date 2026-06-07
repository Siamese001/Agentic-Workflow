"""W5: graph binding materiality reaches PA and judge packets."""

from __future__ import annotations

import json

from apps_rg.prompt_assembly.contracts import CompiledPromptArtifact
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import (
    augment_section_compiled_with_graph_binding_materiality,
)
from apps_rg.runtime.graph_skills_utilization_scorer import (
    build_graph_binding_materiality_summary,
)
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_executive_summary_judge_packet,
    render_judge_prompt_from_packet as render_exec_judge_prompt,
)
from apps_rg.runtime.judges.grade_only_judge_packet import (
    build_grade_only_judge_packet,
    render_judge_prompt_from_packet,
)


def _graph_meta() -> dict:
    return {
        "native_c03_status": "EMITTED",
        "native_c03_final_evidence": {
            "contract_type": "apps_rg.native_c03_final_evidence",
            "selected_source_fact_ids": ["fact_platform_001"],
        },
        "role_episode_bundle_consumption": True,
        "role_episode_bundle_ids": ["reb_platform"],
        "role_episode_bundles": [
            {
                "role_episode_bundle_id": "reb_platform",
                "graph_skill_node_ids": ["skill_governed_platforms"],
                "linked_source_fact_ids": ["fact_platform_001"],
            }
        ],
    }


def _native_c03_meta() -> dict:
    return {
        "native_c03_status": "EMITTED",
        "native_c03_final_evidence": {
            "contract_type": "apps_rg.native_c03_final_evidence",
            "selected_source_fact_ids": ["fact_platform_001"],
        },
    }


def test_materiality_summary_passes_when_candidate_uses_graph_bindings() -> None:
    summary = build_graph_binding_materiality_summary(
        section_id="unify_bullets",
        proof_pool_metadata=_graph_meta(),
        candidate_output={
            "bullets": [
                {
                    "source_fact_ids": ["fact_platform_001"],
                    "role_episode_bundle_id": "reb_platform",
                    "graph_skill_node_ids": ["skill_governed_platforms"],
                }
            ]
        },
        claim_ledger=[{"claim_text": "platform", "source_fact_ids": ["fact_platform_001"]}],
    )

    assert summary["status"] == "PASS"
    assert summary["native_c03_cited_fact_count"] == 1
    assert summary["role_episode_bundle_intersection_count"] == 1
    assert summary["role_episode_skill_intersection_count"] == 1


def test_materiality_summary_fails_metadata_only_candidate() -> None:
    summary = build_graph_binding_materiality_summary(
        section_id="unify_bullets",
        proof_pool_metadata=_graph_meta(),
        candidate_output={"bullets": [{"source_fact_ids": ["other_fact"]}]},
        claim_ledger=[{"claim_text": "other", "source_fact_ids": ["other_fact"]}],
    )

    assert summary["status"] == "FAIL"
    assert {
        row["reason_code"] for row in summary["violations"]
    } >= {
        "native_c03_metadata_without_cited_fact_use",
        "role_episode_metadata_without_bundle_use",
    }


def test_pa_compiled_prompt_surfaces_pending_materiality_summary() -> None:
    compiled = SectionCompiledPrompt(
        section_id="unify_bullets",
        apps_rg_prompt_template_ref="test",
        artifact=CompiledPromptArtifact(
            messages=[{"role": "system", "content": "base"}],
            template_id="test",
        ),
    )

    out = augment_section_compiled_with_graph_binding_materiality(
        compiled,
        runtime_payload={"proof_pool_metadata": _graph_meta()},
    )
    content = out.artifact.messages[0]["content"]

    assert "GRAPH_BINDING_MATERIALITY_SUMMARY" in content
    payload = json.loads(content.split("GRAPH_BINDING_MATERIALITY_SUMMARY (deterministic JSON):", 1)[1])
    assert payload["status"] == "PENDING_CANDIDATE_OUTPUT"
    assert payload["native_c03_active"] is True
    assert payload["role_episode_active"] is True


def test_generic_judge_packet_and_prompt_include_materiality_summary() -> None:
    packet = build_grade_only_judge_packet(
        section_id="unify_bullets",
        candidate_output={
            "bullets": [
                {
                    "source_fact_ids": ["fact_platform_001"],
                    "role_episode_bundle_id": "reb_platform",
                    "graph_skill_node_ids": ["skill_governed_platforms"],
                }
            ]
        },
        claim_ledger=[{"claim_text": "platform", "source_fact_ids": ["fact_platform_001"]}],
        section_rubric="rubric",
        rubric_ref="test",
        proof_pool_metadata=_graph_meta(),
    )

    assert packet["graph_binding_materiality_summary"]["status"] == "PASS"
    assert packet["proof_boundary"]["metadata_only_graph_context_is_insufficient"] is True
    assert "GRAPH_BINDING_MATERIALITY_SUMMARY" in render_judge_prompt_from_packet(packet)


def test_executive_summary_judge_packet_includes_native_c03_materiality() -> None:
    packet = build_executive_summary_judge_packet(
        resume_display_text="Built governed platform.",
        claim_ledger=[{"claim_text": "platform", "source_fact_ids": ["fact_platform_001"]}],
        allowed_fact_packet=[],
        allowed_fact_ids={"fact_platform_001"},
        target_title="SVP",
        target_company="Acme",
        jd_text="targeting only",
        briefing_text="targeting only",
        parsed_output={},
        proof_pool_metadata=_native_c03_meta(),
    )

    assert packet["graph_binding_materiality_summary"]["status"] == "PASS"
    assert packet["proof_boundary"]["metadata_only_graph_context_is_insufficient"] is True
    assert "GRAPH_BINDING_MATERIALITY_SUMMARY" in render_exec_judge_prompt(packet)
