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


def test_companion_context_used_as_proof_fails_x2_competency_companion_context_not_proof() -> None:
    competencies = [
        {
            "category_label": "Execution and Delivery",
            "terms": [_term("agentic platform orchestration"), _term("policy-gated routing"), _term("runtime governance")],
            "source_fact_ids": ["bul_unify_001"],
        },
    ]
    for i in range(5):
        competencies.append(
            {
                "category_label": f"Platform Engineering {i}",
                "terms": [_term("cloud architecture"), _term("data platform design"), _term("delivery governance")],
                "source_fact_ids": ["bul_unify_002"],
            }
        )
    parsed = _parsed(competencies)
    parsed["jd_alignment"]["companion_context_used_as_proof"] = True
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob="agentic platform orchestration governance",
        allowed_fact_ids={"bul_unify_001", "bul_unify_002"},
        runtime_generation_status="REAL_LLM",
    )
    assert _gate(gates, "x2_competency_companion_context_not_proof") is False


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
            "category_label": "Technology Strategy & Innovation",
            "terms": [
                _term("enterprise technology roadmap"),
                _term("platform operating model"),
                _term("innovation portfolio governance"),
            ],
            "source_fact_ids": ["bul_unify_001"],
        },
        {
            "category_label": "AI Platform Leadership",
            "terms": [
                _term("multi-agent orchestration"),
                _term("GraphRAG retrieval"),
                _term("policy-gated execution"),
            ],
            "source_fact_ids": ["bul_unify_002"],
        },
        {
            "category_label": "Data & Analytics Modernization",
            "terms": [
                _term("Basel III lineage"),
                _term("data cataloging"),
                _term("lakehouse modernization"),
            ],
            "source_fact_ids": ["bul_ibm_001"],
        },
        {
            "category_label": "Governance, Risk & Compliance",
            "terms": [
                _term("regulatory reporting controls"),
                _term("automated validation frameworks"),
                _term("audit traceability"),
            ],
            "source_fact_ids": ["bul_ibm_001"],
        },
        {
            "category_label": "Engineering & Delivery Leadership",
            "terms": [
                _term("platform engineering scale-out"),
                _term("cross-functional delivery governance"),
                _term("ML engineering leadership"),
            ],
            "source_fact_ids": ["bul_unify_005"],
        },
        {
            "category_label": "LLMOps & Reliability",
            "terms": [
                _term("audit-grade observability"),
                _term("evaluation gauntlet design"),
                _term("telemetry reliability lifecycle"),
            ],
            "source_fact_ids": ["bul_unify_005"],
        },
        {
            "category_label": "Commercial & Operating Impact",
            "terms": [
                _term("IP-led platform commercialization"),
                _term("managed AI services"),
                _term("operating margin expansion"),
            ],
            "source_fact_ids": ["bul_unify_004"],
        },
        {
            "category_label": "Cloud & Partner Ecosystems",
            "terms": [
                _term("AWS platform architecture"),
                _term("Databricks Lakehouse"),
                _term("cloud alliance GTM"),
            ],
            "source_fact_ids": ["bul_unify_003"],
        },
    ]
    results = _run_gates(cats)
    assert _gate(results, "x2_competencies_min_category_count")
    assert _gate(results, "x2_competencies_min_items_per_category")
    assert _gate(results, "x2_competencies_no_credential_relisting")
    assert _gate(results, "x2_competencies_role_alignment_terms")
    assert _gate(results, "x2_competencies_approved_category_labels")
    assert _gate(results, "x2_competencies_no_fragment_or_one_word_terms")


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
