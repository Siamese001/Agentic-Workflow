"""X2 + sanitize: competencies must not duplicate CERTIFICATIONS & CREDENTIALS section."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.competencies_certification_contract import (
    check_competencies_no_reserved_certification_category,
    sanitize_competencies_no_certification_category,
)
from apps_rg.runtime.sections.competencies_lane_runtime import competencies_display_text
from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates


def _term(text: str, fid: str = "fact_engineering_platform_005") -> dict:
    return {"text": text, "source_fact_id": fid, "source_fact_ids": [fid]}


def _eight_category_fixture(*, include_cert_category: bool = False) -> list[dict]:
    cats = [
        {"category_label": "Agentic AI Platforms", "terms": [_term("agentic AI platforms"), _term("policy gating")], "source_fact_ids": ["bul_unify_001"]},
        {"category_label": "AI Runtime Governance", "terms": [_term("runtime governance"), _term("audit trails")], "source_fact_ids": ["fact_governance_003"]},
        {"category_label": "Retrieval Engineering", "terms": [_term("GraphRAG retrieval"), _term("context assembly")], "source_fact_ids": ["bul_unify_003"]},
        {"category_label": "LLMOps Discipline", "terms": [_term("evaluation gates"), _term("rollback controls")], "source_fact_ids": ["bul_unify_004"]},
        {"category_label": "Distributed Systems", "terms": [_term("microservices"), _term("API gateways")], "source_fact_ids": ["bul_unify_005"]},
        {"category_label": "Platform Productization", "terms": [_term("IP-led packaging"), _term("margin expansion")], "source_fact_ids": ["bul_unify_006"]},
        {"category_label": "Enterprise Analytics", "terms": [_term("regulated analytics"), _term("lineage controls")], "source_fact_ids": ["bul_ibm_001"]},
    ]
    if include_cert_category:
        cats.append(
            {
                "category_label": "Certifications",
                "terms": [
                    _term("Databricks Lakehouse Fundamentals", "fact_certs_001"),
                    _term("AWS Certified Solutions Architect", "fact_certs_001"),
                    _term("Fellow of the Society of Actuaries", "fact_certs_001"),
                ],
                "source_fact_ids": ["fact_certs_001"],
            }
        )
    else:
        cats.append(
            {
                "category_label": "Partnership Execution",
                "terms": [_term("co-sell motions"), _term("alliance rhythm")],
                "source_fact_ids": ["bul_ibm_005"],
            }
        )
    return cats


def test_certifications_category_fails_x2_gate() -> None:
    competencies = _eight_category_fixture(include_cert_category=True)
    ok, reason = check_competencies_no_reserved_certification_category(competencies)
    assert ok is False
    assert reason and "reserved_category" in reason

    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output={"competencies": competencies, "claim_ledger": []},
        claim_ledger=[],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob="aws databricks microservices",
        allowed_fact_ids={"fact_certs_001", "bul_unify_001"},
        runtime_generation_status="REAL_LLM",
    )
    gate = next(g for g in gates if g.gate_id == "x2_competencies_no_reserved_certification_category")
    assert gate.pass_ is False


def test_credential_names_in_terms_fail_x2() -> None:
    competencies = _eight_category_fixture(include_cert_category=False)
    competencies[0]["terms"].append(_term("AWS Certified Solutions Architect", "fact_certs_001"))
    ok, reason = check_competencies_no_reserved_certification_category(competencies)
    assert ok is False
    assert "credential_term" in (reason or "")


def test_cloud_platforms_skill_terms_pass_x2() -> None:
    competencies = _eight_category_fixture(include_cert_category=False)
    competencies[4] = {
        "category_label": "Cloud and Data Platforms",
        "terms": [
            _term("AWS"),
            _term("Databricks Lakehouse"),
            _term("vector services"),
        ],
        "source_fact_ids": ["bul_unify_005"],
    }
    ok, _ = check_competencies_no_reserved_certification_category(competencies)
    assert ok is True


def test_sanitize_removes_certifications_category_and_remaps_skills() -> None:
    competencies = _eight_category_fixture(include_cert_category=True)
    sanitized, log = sanitize_competencies_no_certification_category(competencies)
    assert len(sanitized) == 8
    labels = [str(c.get("category_label") or "") for c in sanitized]
    assert not any(lab.strip().lower() == "certifications" for lab in labels)
    display = competencies_display_text(sanitized)
    assert "Certifications:" not in display
    assert "Fellow of the Society of Actuaries" not in display
    assert any("Databricks Lakehouse" in display or "AWS" in display for _ in [0])
    assert any(e.get("operation") == "remap_reserved_certification_category" for e in log)


def test_final_resume_json_competencies_sanitize_eliminates_duplicate_cert_block() -> None:
    """Proves fix on stored assembly snapshot (pre-fix run) without requiring full re-run."""
    final_json = (
        Path(__file__).resolve().parents[3]
        / "artifacts/apps_rg/runtime_proofs/full_resume_d46da9438d47/modular_r4/final_resume_assembly/final_resume.json"
    )
    if not final_json.is_file():
        return
    payload = json.loads(final_json.read_text(encoding="utf-8"))
    comps: list[dict] = []
    for sec in payload.get("sections") or []:
        if isinstance(sec, dict) and sec.get("section_id") == "competencies":
            snap = sec.get("l2_output_snapshot") or {}
            comps = list(snap.get("competencies") or [])
            break
    assert any(
        str(c.get("category_label", "")).strip().lower() == "certifications" for c in comps
    ), "fixture must include Certifications category (pre-fix snapshot)"
    sanitized, _ = sanitize_competencies_no_certification_category(comps)
    display = competencies_display_text(sanitized)
    assert "Certifications:" not in display
    assert "Fellow of the Society of Actuaries" not in display
    ok, _ = check_competencies_no_reserved_certification_category(sanitized)
    assert ok is True


def test_sanitize_preserves_valid_source_fact_ids() -> None:
    competencies = _eight_category_fixture(include_cert_category=True)
    sanitized, _ = sanitize_competencies_no_certification_category(competencies)
    for cat in sanitized:
        for t in cat.get("terms") or []:
            if isinstance(t, dict) and t.get("source_fact_id"):
                assert str(t["source_fact_id"]).startswith(("bul_", "fact_"))
