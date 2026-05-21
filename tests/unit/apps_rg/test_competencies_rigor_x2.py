"""Competencies executive rigor X2 gates."""

from __future__ import annotations

from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates


def _term(text: str, fid: str = "bul_unify_001") -> dict:
    return {"text": text, "source_fact_id": fid, "source_fact_ids": [fid]}


def _parsed(competencies: list[dict]) -> dict:
    return {
        "competencies": competencies,
        "selected_fact_plan": {"selected_fact_ids": ["bul_unify_001"]},
        "claim_ledger": [
            {
                "claim_id": "c1",
                "claim_text": "Built agentic AI platforms with runtime governance.",
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
    }


def _run_gates(competencies: list[dict]):
    parsed = _parsed(competencies)
    return run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob=(
            "agentic platform orchestration governance aws databricks graphrag "
            "microservices derivatives hedging basel regulatory"
        ),
        allowed_fact_ids={
            "bul_unify_001",
            "bul_unify_002",
            "bul_unify_003",
            "bul_unify_004",
            "bul_unify_005",
            "bul_ibm_001",
            "bul_ibm_002",
            "fact_certs_001",
        },
        runtime_generation_status="REAL_LLM",
    )


def _gate(results, gate_id: str) -> bool:
    for g in results:
        if g.gate_id == gate_id:
            return g.pass_
    raise AssertionError(f"missing gate {gate_id}")


def test_weak_two_item_category_fails_rigor_gates():
    weak = [
        {
            "category_label": "Execution and Delivery",
            "terms": [_term("team scaling"), _term("margin expansion")],
            "source_fact_ids": ["bul_unify_001"],
        },
        {
            "category_label": "Sales and Accounts",
            "terms": [_term("enterprise adoption"), _term("budget optimization")],
            "source_fact_ids": ["bul_unify_002"],
        },
    ]
    for i in range(4):
        weak.append(
            {
                "category_label": f"Platform Area {i}",
                "terms": [_term("pipeline analytics"), _term("synergy modeling")],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
    results = _run_gates(weak)
    assert not _gate(results, "x2_competencies_min_items_per_category")
    assert not _gate(results, "x2_competencies_no_low_rigor_two_word_items")


def test_certifications_row_in_competencies_fails():
    cats = [
        {
            "category_label": "Certifications",
            "terms": [
                _term("Databricks Lakehouse Fundamentals", "fact_certs_001"),
                _term("AWS Certified Solutions Architect", "fact_certs_001"),
                _term("Fellow of the Society of Actuaries", "fact_certs_001"),
            ],
            "source_fact_ids": ["fact_certs_001"],
        },
    ]
    for i in range(5):
        cats.append(
            {
                "category_label": f"Engineering Cluster {i}",
                "terms": [
                    _term("agentic AI platform architecture"),
                    _term("runtime governance controls"),
                    _term("GraphRAG retrieval engineering"),
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
    results = _run_gates(cats)
    assert not _gate(results, "x2_competencies_no_reserved_certification_category")
    assert not _gate(results, "x2_competencies_no_credential_relisting")


def test_metrics_only_skill_fails():
    cats = []
    labels = (
        "Agentic AI Platform Architecture",
        "AI Reliability and Evaluation",
        "Enterprise Data and Governance",
        "Cloud and Distributed Infrastructure",
        "Platform Commercialization",
        "Engineering Leadership",
    )
    for label in labels:
        cats.append(
            {
                "category_label": label,
                "terms": [
                    _term("deterministic routing"),
                    _term("validation gates"),
                    _term("team scaling"),
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
    results = _run_gates(cats)
    assert not _gate(results, "x2_competencies_no_metrics_as_skills_without_capability_context")


def test_target_quality_competencies_pass_rigor_gates():
    cats = [
        {
            "category_label": "Agentic AI Platform Architecture",
            "terms": [
                _term("deterministic routing"),
                _term("multi-agent orchestration"),
                _term("GraphRAG retrieval"),
            ],
            "source_fact_ids": ["bul_unify_001"],
        },
        {
            "category_label": "AI Reliability and Evaluation",
            "terms": [
                _term("validation gates"),
                _term("replayable execution traces"),
                _term("telemetry instrumentation"),
            ],
            "source_fact_ids": ["bul_unify_002"],
        },
        {
            "category_label": "Enterprise Data and Governance",
            "terms": [
                _term("Basel III lineage"),
                _term("data catalogs"),
                _term("regulatory reporting controls"),
            ],
            "source_fact_ids": ["bul_ibm_001"],
        },
        {
            "category_label": "Cloud and Distributed Infrastructure",
            "terms": [
                _term("AWS"),
                _term("Databricks Lakehouse"),
                _term("microservices"),
            ],
            "source_fact_ids": ["bul_unify_003"],
        },
        {
            "category_label": "Platform Commercialization",
            "terms": [
                _term("reusable IP strategy"),
                _term("managed AI services"),
                _term("platform commercialization"),
            ],
            "source_fact_ids": ["bul_unify_004"],
        },
        {
            "category_label": "Engineering Leadership",
            "terms": [
                _term("platform roadmap ownership"),
                _term("ML engineering scale-out"),
                _term("cross-functional delivery governance"),
            ],
            "source_fact_ids": ["bul_unify_005"],
        },
        {
            "category_label": "Quantitative and Risk Systems",
            "terms": [
                _term("deterministic modeling"),
                _term("derivatives pricing"),
                _term("multi-Greek hedging"),
            ],
            "source_fact_ids": ["bul_ibm_002"],
        },
    ]
    results = _run_gates(cats)
    assert _gate(results, "x2_competencies_min_category_count")
    assert _gate(results, "x2_competencies_min_items_per_category")
    assert _gate(results, "x2_competencies_no_credential_relisting")
    assert _gate(results, "x2_competencies_role_alignment_terms")


def test_all_generic_skill_phrase_fails():
    cats = []
    labels = (
        "Agentic AI Platform Architecture",
        "AI Reliability and Evaluation",
        "Enterprise Data and Governance",
        "Cloud and Distributed Infrastructure",
        "Platform Commercialization",
        "Engineering Leadership",
    )
    for label in labels:
        cats.append(
            {
                "category_label": label,
                "terms": [
                    _term("team scaling"),
                    _term("pipeline analytics"),
                    _term("synergy modeling"),
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
    results = _run_gates(cats)
    assert not _gate(results, "x2_competencies_no_all_generic_skill_phrase")


def test_keyword_repetition_limit_fails():
    cats = []
    labels = (
        "Agentic AI Platform Architecture",
        "AI Reliability and Evaluation",
        "Enterprise Data and Governance",
        "Cloud and Distributed Infrastructure",
        "Platform Commercialization",
        "Engineering Leadership",
    )
    for label in labels:
        cats.append(
            {
                "category_label": label,
                "terms": [
                    _term("deterministic routing"),
                    _term("deterministic orchestration"),
                    _term("deterministic governance"),
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
    results = _run_gates(cats)
    assert not _gate(results, "x2_competencies_keyword_repetition_limit")
