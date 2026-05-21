"""Full-resume LLM coherence aggregation gate."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.assembly.final_resume_x2 import gate_x2_full_resume_llm_coherence_aggregation
from apps_rg.runtime.assembly.full_resume_llm_coherence import (
    aggregate_full_resume_coherence,
    emit_full_resume_llm_coherence_review,
    run_full_resume_coherence_judges,
)
from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput


def _judge(*, key: str, pass_: bool, blocked: bool = False, mocked: bool = False) -> JudgeOutput:
    return JudgeOutput(
        judge_id=f"x1d_{key}_full_resume_coherence",
        provider_name=key,
        provider_key=key,
        evaluator_mode="MOCKED" if mocked else "LIVE",
        provider_status="MOCKED" if mocked else ("BLOCKED_PROVIDER_UNAVAILABLE" if blocked else "OK"),
        model_name="test",
        provider_available=not blocked and not mocked,
        provider_blocked=blocked,
        exact_provider_error="blocked" if blocked else None,
        rubric_version="test",
        input_hash="abc",
        output_hash="def",
        score=0.9 if pass_ else 0.2,
        score_scale="0_to_1",
        normalized_score=0.9 if pass_ else 0.2,
        threshold=0.8,
        normalized_threshold=0.8,
        pass_=pass_,
        decisive_failure=not pass_,
        findings=[],
        cited_sentence_indexes=[],
        remediation_suggestions=[],
    )


def test_provider_blocked_not_counted_as_pass():
    judges = [
        _judge(key="gemini_pro", pass_=True),
        _judge(key="openai_chatgpt", pass_=True, blocked=True),
        _judge(key="anthropic_claude", pass_=False, blocked=True),
    ]
    agg = aggregate_full_resume_coherence(judges, deterministic_blockers=[])
    assert agg["model_backed_pass_count"] == 1
    assert agg["full_resume_coherence_pass"] is False


def test_quorum_pass_with_two_live_judges():
    judges = [
        _judge(key="gemini_pro", pass_=True),
        _judge(key="openai_chatgpt", pass_=True),
        _judge(key="anthropic_claude", pass_=False),
    ]
    agg = aggregate_full_resume_coherence(judges, deterministic_blockers=[])
    assert agg["full_resume_coherence_pass"] is True


def test_duplicate_certifications_in_competencies_fails_deterministic_blocker(tmp_path: Path):
    final = {
        "final_resume_hash": "deadbeef",
        "candidate_identity": {"candidate_name": "Test", "header_contact": {}},
        "sections": [
            {
                "section_id": "competencies",
                "assemble_order": 10,
                "l2_output_snapshot": {
                    "competencies": [
                        {
                            "category_label": "Certifications",
                            "terms": [
                                {"text": "AWS Certified Solutions Architect", "source_fact_id": "f1"},
                                {"text": "Databricks Lakehouse Fundamentals", "source_fact_id": "f1"},
                                {"text": "Fellow of the Society of Actuaries", "source_fact_id": "f1"},
                            ],
                            "source_fact_ids": ["f1"],
                        }
                    ]
                },
            },
            {
                "section_id": "certifications",
                "assemble_order": 12,
                "copied_text_exact": json.dumps([{"name": "AWS Certified Solutions Architect"}]),
            },
        ],
    }
    review = emit_full_resume_llm_coherence_review(
        final_resume=final,
        final_resume_path=tmp_path / "final_resume.json",
        output_dir=tmp_path,
        mode="mocked",
    )
    assert review["full_resume_coherence_pass"] is False
    assert any("credential" in b for b in review["blockers"])
    gate = gate_x2_full_resume_llm_coherence_aggregation(review, required=True)
    assert gate.pass_ is False


def test_strong_resume_passes_deterministic_preflight_when_judges_pass(tmp_path: Path):
    final = {
        "final_resume_hash": "cafebabe",
        "candidate_identity": {"candidate_name": "Test", "header_contact": {}},
        "sections": [
            {
                "section_id": "headline",
                "assemble_order": 1,
                "l2_output_snapshot": {"headline_line": "SVP Engineering | Agentic AI Platforms"},
            },
            {
                "section_id": "executive_summary",
                "assemble_order": 2,
                "l2_output_snapshot": {
                    "resume_display_text": "Executive leader building agentic AI platforms with governance."
                },
            },
            {
                "section_id": "competencies",
                "assemble_order": 10,
                "l2_output_snapshot": {
                    "competencies": [
                        {
                            "category_label": "Agentic AI Platform Architecture",
                            "terms": [
                                {"text": "deterministic routing", "source_fact_id": "b1"},
                                {"text": "multi-agent orchestration", "source_fact_id": "b1"},
                                {"text": "GraphRAG retrieval", "source_fact_id": "b1"},
                            ],
                            "source_fact_ids": ["b1"],
                        },
                        {
                            "category_label": "AI Reliability and Evaluation",
                            "terms": [
                                {"text": "validation gates", "source_fact_id": "b2"},
                                {"text": "telemetry instrumentation", "source_fact_id": "b2"},
                                {"text": "rollback controls", "source_fact_id": "b2"},
                            ],
                            "source_fact_ids": ["b2"],
                        },
                        {
                            "category_label": "Enterprise Data and Governance",
                            "terms": [
                                {"text": "data catalogs", "source_fact_id": "b3"},
                                {"text": "regulatory reporting controls", "source_fact_id": "b3"},
                                {"text": "automated validation frameworks", "source_fact_id": "b3"},
                            ],
                            "source_fact_ids": ["b3"],
                        },
                        {
                            "category_label": "Cloud and Distributed Infrastructure",
                            "terms": [
                                {"text": "AWS", "source_fact_id": "b4"},
                                {"text": "Databricks Lakehouse", "source_fact_id": "b4"},
                                {"text": "microservices", "source_fact_id": "b4"},
                            ],
                            "source_fact_ids": ["b4"],
                        },
                        {
                            "category_label": "Platform Commercialization",
                            "terms": [
                                {"text": "reusable IP strategy", "source_fact_id": "b5"},
                                {"text": "managed AI services", "source_fact_id": "b5"},
                                {"text": "enterprise adoption", "source_fact_id": "b5"},
                            ],
                            "source_fact_ids": ["b5"],
                        },
                        {
                            "category_label": "Engineering Leadership",
                            "terms": [
                                {"text": "platform roadmap ownership", "source_fact_id": "b6"},
                                {"text": "ML engineering scale-out", "source_fact_id": "b6"},
                                {"text": "cross-functional delivery governance", "source_fact_id": "b6"},
                            ],
                            "source_fact_ids": ["b6"],
                        },
                    ]
                },
            },
            {
                "section_id": "certifications",
                "assemble_order": 12,
                "copied_text_exact": json.dumps([{"name": "AWS Certified Solutions Architect"}]),
            },
        ],
    }
    judges = run_full_resume_coherence_judges(
        full_resume_text="SVP agentic AI platform engineering resume.",
        target_company="Brown & Brown",
        target_role="Senior Vice President, IT Strategy & Innovation",
        mode="mocked",
    )
    agg = aggregate_full_resume_coherence(judges, deterministic_blockers=[])
    # mocked judges never pass quorum — artifact still emitted with explicit fail
    assert agg["full_resume_coherence_pass"] is False
    review = emit_full_resume_llm_coherence_review(
        final_resume=final,
        final_resume_path=tmp_path / "final_resume.json",
        output_dir=tmp_path / "strong",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy",
        mode="mocked",
    )
    assert (tmp_path / "strong" / "full_resume_llm_coherence_review.json").is_file()
    pre_blockers = review.get("blockers") or []
    assert not any("credential_duplication" in b for b in pre_blockers)


def test_gate_requires_artifact_when_enabled():
    g = gate_x2_full_resume_llm_coherence_aggregation(None, required=True)
    assert g.pass_ is False
    g2 = gate_x2_full_resume_llm_coherence_aggregation(
        {"full_resume_coherence_pass": True},
        required=True,
    )
    assert g2.pass_ is True
