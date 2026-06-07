from __future__ import annotations

from pathlib import Path

from apps_rg.prompt_assembly.contracts import CompiledPromptArtifact
from apps_rg.runtime.aggregation.cross_section_x2 import run_cross_section_x2_gates
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import (
    finalize_section_compiled_with_proof_pool,
)
from apps_rg.runtime.graph_skills_utilization_scorer import (
    build_graph_binding_materiality_summary,
)
from apps_rg.runtime.internal.resume_package_disposition import (
    summarize_graph_skills_product_closeout,
)
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_executive_summary_judge_packet,
)


def _aig_runtime_payload() -> dict:
    return {
        "section_id": "executive_summary",
        "target_company": "AIG",
        "target_title": "VP, Global Head of Agentic AI Solutions",
        "allowed_fact_ids": ["fact_governance_003", "fact_engineering_platform_001"],
        "canonical_final_evidence_contract_snapshot": {
            "final_evidence_digest": "fec-aig",
            "allowed_fact_ids": ["fact_governance_003", "fact_engineering_platform_001"],
        },
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                "ledger_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                "graph_digest": "graph-digest",
                "ledger_digest": "ledger-digest",
                "skills_authority_status": "PASS",
            },
        },
        "section_fec_bridge": {
            "schema_version": "section_fec_bridge_v1",
            "route_contract_ref": "route_contract.json",
            "pa_proof_authority_metadata": {
                "proof_pool_type": "augmented_skills_graph",
                "evidence_authority": {
                    "authority": "augmented_skills_graph",
                    "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                    "ledger_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                    "graph_digest": "graph-digest",
                    "ledger_digest": "ledger-digest",
                    "skills_authority_status": "PASS",
                },
            },
        },
        "graph_targeting_for_pa": {
            "claim_support_graph_refs": [
                "skill_governed_agentic_systems_architecture",
                "skill_exit_disposition_governance",
            ],
            "targeting_graph_refs": [
                "pillar_agentic_ai_platforms",
                "pillar_insurance_carrier_transformation",
            ],
            "role_family_projection": {
                "pillar_hint_ids": [
                    "pillar_agentic_ai_platforms",
                    "pillar_insurance_carrier_transformation",
                ],
            },
            "receipt_only_lineage_refs": ["ref:graph:edge:1"],
            "overloaded_fact_compression": [
                {
                    "fact_id": "fact_engineering_platform_001",
                    "skill_binding_count_before": 8,
                    "skill_binding_count_after": 3,
                    "executive_capability_phrases": ["governed enterprise AI platform delivery"],
                }
            ],
        },
    }


def test_aig_prompt_and_judge_packet_reflect_graph_materiality() -> None:
    runtime_payload = _aig_runtime_payload()
    summary = build_graph_binding_materiality_summary(
        section_id="executive_summary",
        runtime_payload=runtime_payload,
    )
    assert summary["allowed_fact_count"] == 2
    assert "pillar_agentic_ai_platforms" in summary["pillar_hint_ids"]

    compiled = SectionCompiledPrompt(
        section_id="executive_summary",
        apps_rg_prompt_template_ref="test",
        artifact=CompiledPromptArtifact(messages=[{"role": "user", "content": "draft"}]),
    )
    augmented = finalize_section_compiled_with_proof_pool(compiled, runtime_payload=runtime_payload)
    prompt_text = augmented.artifact.messages[-1]["content"]
    assert "GRAPH_BINDING_MATERIALITY_SUMMARY" in prompt_text
    assert "skill_governed_agentic_systems_architecture" in prompt_text

    packet = build_executive_summary_judge_packet(
        resume_display_text="Built governed enterprise AI platform delivery.",
        claim_ledger=[
            {
                "claim_text": "Built governed enterprise AI platform delivery.",
                "source_fact_ids": ["fact_engineering_platform_001"],
            }
        ],
        allowed_fact_packet=[
            {
                "fact_id": "fact_engineering_platform_001",
                "claim_text": "Built governed enterprise AI platform delivery.",
            }
        ],
        allowed_fact_ids={"fact_engineering_platform_001"},
        target_title="VP, Global Head of Agentic AI Solutions",
        target_company="AIG",
        jd_text="targeting only",
        briefing_text="targeting only",
        parsed_output={"sentences": []},
        graph_targeting_capsule=runtime_payload["graph_targeting_for_pa"],
    )
    assert packet["graph_binding_materiality_summary"]["section_id"] == "executive_summary"
    assert "skill_governed_agentic_systems_architecture" in packet["graph_binding_materiality_summary"][
        "claim_support_graph_refs"
    ]


def test_cross_section_and_package_closeout_reflect_graph_materiality(tmp_path: Path) -> None:
    summary = build_graph_binding_materiality_summary(
        section_id="executive_summary",
        runtime_payload=_aig_runtime_payload(),
    )
    final_resume = {
        "sections": [
            {
                "section_id": "executive_summary",
                "section_kind": "generated_lane",
                "l2_output_snapshot": {
                    "resume_display_text": "AIG governed platform.",
                    "claim_ledger": [{"claim_text": "AIG governed platform.", "source_fact_ids": ["f1"]}],
                    "graph_binding_materiality_summary": summary,
                },
            },
            {
                "section_id": "competencies",
                "section_kind": "generated_lane",
                "l2_output_snapshot": {
                    "competencies": ["Agentic AI platforms"],
                    "graph_binding_materiality_summary": summary,
                },
            },
        ]
    }
    gates, *_ = run_cross_section_x2_gates(
        repo=tmp_path,
        final_resume_blob=final_resume,
        fingerprint={"review_lanes": []},
        sealed_index={"pointers": []},
    )
    gate_doc = {"gates": [g.to_dict() for g in gates]}
    graph_gate = next(g for g in gate_doc["gates"] if g["gate_id"] == "x2_cross_section_graph_coherence")
    assert graph_gate["pass"] is True

    closeout = summarize_graph_skills_product_closeout(gate_doc)
    assert closeout["graph_coherence_gate_present"] is True
    assert closeout["product_closeout_status"] == "PASS"
