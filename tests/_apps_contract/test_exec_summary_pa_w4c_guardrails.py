"""W4C: executive_summary compiled-prompt forbidden-phrase and fact-support guardrails."""
from __future__ import annotations

from pathlib import Path

from apps_rg.fact_inventory.exec_summary_graph_projection_w4b import (
    inspect_role_family_projection,
)
from apps_rg.runtime.dispatch.executive_summary_pa import (
    SRFS_FORBIDDEN_PHRASES_ALWAYS,
    SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER,
    compile_executive_summary_prompt,
    format_srfs_forbidden_phrase_guardrails_block,
)

REPO = Path(__file__).resolve().parents[2]

GRAPH_RAG_FACT = {
    "fact_id": "fact_engineering_platform_001",
    "claim_text": (
        "Designed governed agentic AI with GraphRAG retrieval, sandboxed execution, "
        "and replayable traces."
    ),
}

NO_GRAPH_PARTNER_FACT = {
    "fact_id": "fact_governance_003",
    "claim_text": "Implemented Basel III / CCAR data lineage and automated validation frameworks.",
}


def _graph_product_payload(*, facts: list[dict], run_id: str = "w4c_guardrail") -> dict:
    return {
        "run_id": run_id,
        "target_title": "SVP Engineering",
        "target_company": "Acme",
        "jd_text": "partner engineering GraphRAG alliances co-sell",
        "briefing": "steering for partner GTM and graph retrieval",
        "selected_fact_plan": {
            "facts": facts,
            "required_fact_ids": [str(f["fact_id"]) for f in facts],
        },
        "allowed_fact_ids": [str(f["fact_id"]) for f in facts],
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "graph_skills_proof_pool": True,
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "skills_authority_status": "PASS",
            },
        },
    }


def _compiled_content(payload: dict) -> str:
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    return out.artifact.messages[0]["content"].lower()


def test_forbidden_phrase_block_lists_all_w4c_bans() -> None:
    block = format_srfs_forbidden_phrase_guardrails_block().lower()
    assert SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER.lower() in block
    for phrase in SRFS_FORBIDDEN_PHRASES_ALWAYS:
        assert phrase.lower() in block, f"missing global ban: {phrase}"
    assert "unsupported graphrag claims" in block
    assert "unsupported partner engineering claims" in block


def test_compiled_graph_prompt_includes_w4c_forbidden_contract() -> None:
    content = _compiled_content(_graph_product_payload(facts=[GRAPH_RAG_FACT, NO_GRAPH_PARTNER_FACT]))
    assert "srfs_forbidden_phrase_contract" in content
    for phrase in SRFS_FORBIDDEN_PHRASES_ALWAYS:
        assert phrase.lower() in content, f"missing in compiled prompt: {phrase}"
    assert "unsupported graphrag claims" in content
    assert "unsupported partner engineering claims" in content


def test_graphrag_allowed_only_when_selected_fact_supports_it() -> None:
    with_graph = _compiled_content(_graph_product_payload(facts=[GRAPH_RAG_FACT], run_id="w4c_graphrag_yes"))
    without_graph = _compiled_content(
        _graph_product_payload(facts=[NO_GRAPH_PARTNER_FACT], run_id="w4c_graphrag_no")
    )
    assert "verbatim" in with_graph and "graphrag" in with_graph
    assert "do not introduce graphrag" in without_graph or "unsupported graphrag" in without_graph


def test_partner_engineering_blocked_unless_fact_supports() -> None:
    content = _compiled_content(_graph_product_payload(facts=[NO_GRAPH_PARTNER_FACT], run_id="w4c_partner"))
    assert "partner engineering" in content
    assert "cannot authorize" in content or "do not introduce partner engineering" in content
    assert "jd_text" in content and "not proof" in content


def test_jd_briefing_cannot_authorize_graphrag_or_partner_claims() -> None:
    content = _compiled_content(_graph_product_payload(facts=[NO_GRAPH_PARTNER_FACT], run_id="w4c_jd"))
    assert "targeting-only" in content
    assert "cannot authorize graphrag" in content or "cannot" in content and "graphrag" in content
    assert "partner engineering" in content


def test_skill_id_never_in_allowed_source_fact_ids() -> None:
    row = inspect_role_family_projection("SVP_ENGINEERING_AI_PLATFORM", repo_root=REPO)
    assert row["skill_id_source_fact_id_exclusion"]["excluded_ok"]
    for fid in row["allowed_fact_packet_fact_ids"]:
        assert fid.startswith("fact_")
        assert not fid.startswith("skill_")


def test_allowed_fact_packet_fact_id_only() -> None:
    row = inspect_role_family_projection("ANTHROPIC_PARTNERSHIPS_APPLIED_AI", repo_root=REPO)
    assert row["executive_summary_srfs_fact_ids"]
    assert set(row["allowed_fact_packet_fact_ids"]) == set(row["executive_summary_srfs_fact_ids"])
    assert not any("partnerships_gtm" in fid for fid in row["executive_summary_srfs_fact_ids"])
