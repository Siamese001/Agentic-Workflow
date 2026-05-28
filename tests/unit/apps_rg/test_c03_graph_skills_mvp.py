"""C0.3 graph-skills MVP — judge graph visibility + targeting keywords (plan c03-graph-skills-mvp-b4f9a2)."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from apps_rg.runtime.c0.c03_graph_ref_policy import (
    merge_graph_targeting_jd_alignment,
    resolve_role_family_projection,
)
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    GRAPH_ONLY_GRADE_ONLY_RUBRIC,
    GRADE_ONLY_INSTRUCTION,
    enrich_allowed_fact_packet_for_judges,
)
from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    format_evidence_capsule_c0_block,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    DEPENDENCY_GRAPH_FACT_ID,
    FSA_CREDENTIAL_FACT_ID,
)


def _sample_bindings() -> list[dict[str, Any]]:
    return [
        {
            "fact_id": FSA_CREDENTIAL_FACT_ID,
            "claim_support_graph_refs": ["skill_actuarial_capital_001", "skill_stress_test_002"],
            "executive_capability_phrases": ["actuarial risk quantification and capital modeling"],
        },
        {
            "fact_id": DEPENDENCY_GRAPH_FACT_ID,
            "claim_support_graph_refs": ["skill_graph_aware_003"],
            "executive_capability_phrases": ["graph-aware evidence grounding for regulated workflows"],
        },
    ]


def _mock_skill_graph() -> dict[str, Any]:
    return {
        "skill_rows": [
            {
                "skill_id": "skill_actuarial_capital_001",
                "source_resume_files": ["artifacts/resume/actuarial_section.md"],
            },
            {
                "skill_id": "skill_graph_aware_003",
                "source_resume_files": ["artifacts/resume/platform_section.md"],
            },
        ]
    }


def test_enricher_attaches_graph_proof_refs_for_bound_facts() -> None:
    plan_facts = [
        {"fact_id": FSA_CREDENTIAL_FACT_ID, "claim_text": "actuarial claim"},
        {"fact_id": DEPENDENCY_GRAPH_FACT_ID, "claim_text": "graph claim"},
    ]
    with patch(
        "apps_rg.fact_inventory.augmented_skills_graph.load_augmented_skills_graph",
        return_value=_mock_skill_graph(),
    ):
        rows = enrich_allowed_fact_packet_for_judges(
            plan_facts,
            {FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID},
            graph_bindings=_sample_bindings(),
        )
    by_fid = {str(r["fact_id"]): r for r in rows}
    fsa = by_fid[FSA_CREDENTIAL_FACT_ID]
    assert fsa["graph_proof_refs"]["claim_support_graph_refs"] == [
        "skill_actuarial_capital_001",
        "skill_stress_test_002",
    ]
    assert fsa["graph_proof_refs"]["source_resume_files"] == ["artifacts/resume/actuarial_section.md"]
    assert fsa["executive_capability_phrases"] == [
        "actuarial risk quantification and capital modeling"
    ]
    graph_row = by_fid[DEPENDENCY_GRAPH_FACT_ID]
    assert graph_row["graph_proof_refs"]["claim_support_graph_refs"] == ["skill_graph_aware_003"]
    assert graph_row["graph_proof_refs"]["source_resume_files"] == ["artifacts/resume/platform_section.md"]


def test_rubric_and_instruction_authorize_graph_proof_refs() -> None:
    assert "graph_proof_refs" in GRADE_ONLY_INSTRUCTION.lower()
    assert "source_resume_files" in GRAPH_ONLY_GRADE_ONLY_RUBRIC


def test_resolve_role_family_projection_parses_sqlite_row_body() -> None:
    class _FakeConn:
        def execute(self, *_args: Any, **_kwargs: Any) -> Any:
            return self

        def fetchone(self) -> tuple[Any, ...]:
            return (
                "SVP_ENGINEERING_AI_PLATFORM",
                "SVP_ENGINEERING_AI_PLATFORM",
                '{"track_a": 0.8}',
                '["enterprise AI", "digital transformation"]',
                "marketplace claims require human confirmation",
            )

        def close(self) -> None:
            return None

    with patch(
        "apps_rg.fact_inventory.augmented_skills_graph_sqlite.default_graph_sqlite_path",
        return_value=__import__("pathlib").Path("fake.db"),
    ), patch(
        "apps_rg.fact_inventory.augmented_skills_graph_sqlite.open_graph_sqlite",
        return_value=_FakeConn(),
    ), patch(
        "apps_rg.runtime.c0.c03_graph_ref_policy.resolve_c0_pillar_hints",
        return_value=["pillar_ai_platform"],
    ), patch(
        "pathlib.Path.is_file",
        return_value=True,
    ):
        out = resolve_role_family_projection("SVP_ENGINEERING_AI_PLATFORM")
    assert out["sqlite_projection_row_found"] is True
    assert out["targeting_keywords"] == ["enterprise AI", "digital transformation"]
    assert out["track_weight_profile"] == {"track_a": 0.8}
    assert "marketplace" in out["proof_policy_note"]


def test_evidence_capsule_emits_graph_targeting_keywords() -> None:
    capsule = {
        "proof_pool_type": "graph",
        "selection_id": "sel-1",
        "facts": [{"source_fact_id": FSA_CREDENTIAL_FACT_ID, "claim_text": "claim"}],
    }
    runtime_payload = {
        "graph_targeting_for_pa": {
            "receipt_only_json_expansion_excluded_from_pa": True,
            "targeting_graph_refs": ["pillar_ai_platform"],
            "mechanism_vocabulary_cap": {"max_mechanism_terms_sentence_0": 2},
            "role_family_projection": {
                "targeting_keywords": ["enterprise AI", "IT strategy", "innovation"],
            },
        }
    }
    block = format_evidence_capsule_c0_block(
        capsule,
        [FSA_CREDENTIAL_FACT_ID],
        runtime_payload=runtime_payload,
    )
    assert "GRAPH_TARGETING_KEYWORDS=enterprise AI,IT strategy,innovation" in block


def test_merge_graph_targeting_briefing_supplement_when_run_specific() -> None:
    merged = merge_graph_targeting_jd_alignment(
        {},
        role_family_projection={"role_family_key": "SVP_ENGINEERING_AI_PLATFORM", "pillar_hint_ids": []},
        briefing_text="Lead digital transformation and cloud modernization for regulated insurers.",
        briefing_source="RUN_SPECIFIC",
    )
    supplement = merged["graph_targeting"]["briefing_targeting_supplement"]
    assert supplement, "briefing_targeting_supplement must be non-empty for RUN_SPECIFIC briefing"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
