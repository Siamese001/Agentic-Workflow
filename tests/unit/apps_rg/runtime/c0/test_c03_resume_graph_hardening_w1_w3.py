"""W1-W3 contracts for apps_rg C0.3 resume graph hardening."""
from __future__ import annotations

import inspect
import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    materialize_augmented_skills_graph_sqlite,
)
from apps_rg.runtime.c0.c03_graph_expansion import (
    C03GraphSelectionError,
    expand_c03_graph_bindings,
)
from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    CANONICAL_PLAN_SCHEMA_VERSION,
    TraversalRecorder,
    build_candidate_decision,
    build_candidate_receipt,
    evaluate_pretarget_authority,
    finalize_canonical_section_plan,
    validate_canonical_section_plan,
)
from apps_rg.runtime.c0.c03_sqlite_graph_selection import (
    select_c03_sqlite_graph_candidates,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)

REPO = Path(__file__).resolve().parents[5]


def test_pretarget_authority_is_independent_of_targeting_text() -> None:
    kwargs = {
        "candidate_id": "skill_test",
        "candidate_type": "leaf_skill",
        "section_id": "competencies",
        "section_allowed": True,
        "activation_status": "ACTIVE",
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "external_eligible": True,
        "claim_eligible": True,
        "source_refs": ["fact_test"],
        "path_present": True,
    }
    first = evaluate_pretarget_authority(**kwargs)
    second = evaluate_pretarget_authority(**kwargs)
    assert first == second
    assert first["authority_pass"] is True
    assert first["targeting_consulted"] is False
    assert first["authority_evaluated_before_targeting"] is True


def test_pretarget_authority_blocks_explicit_nonclaimable_metadata() -> None:
    decision = evaluate_pretarget_authority(
        candidate_id="skill_blocked",
        candidate_type="leaf_skill",
        section_id="executive_summary",
        section_allowed=False,
        activation_status="DRAFT",
        support_level="TARGETING_ONLY",
        external_claim_policy="internal_only",
        external_eligible=False,
        claim_eligible=False,
        source_refs=[],
        path_present=False,
    )
    assert decision["authority_pass"] is False
    assert "section_not_allowed" in decision["reason_codes"]
    assert "external_eligible_false" in decision["reason_codes"]
    assert "missing_graph_path" in decision["reason_codes"]
    assert "missing_source_lineage" in decision["reason_codes"]


def test_canonical_plan_rejects_selected_candidate_without_authority() -> None:
    authority = evaluate_pretarget_authority(
        candidate_id="skill_blocked",
        candidate_type="leaf_skill",
        section_id="competencies",
        section_allowed=False,
        source_refs=["fact_test"],
    )
    row = build_candidate_decision(
        section_id="competencies",
        candidate_id="skill_blocked",
        candidate_type="leaf_skill",
        candidate_path_id="root:r/skill:skill_blocked",
        decision="selected",
        reason_codes=["bad_test_selection"],
        authority=authority,
        hop_depth=1,
    )
    recorder = TraversalRecorder(section_id="competencies", max_hop_depth=1)
    recorder.record(
        event_type="authority_evaluated",
        hop_depth=1,
        candidate_path_id=row["candidate_path_id"],
        authority_pass=False,
    )
    plan = {
        "schema_version": CANONICAL_PLAN_SCHEMA_VERSION,
        "section_id": "competencies",
        "source_authority_contract": {"targeting_inputs_are_non_authority": True},
        "graph_candidate_decision_ledger": [row],
        "graph_candidate_receipt": build_candidate_receipt(
            section_id="competencies", decisions=[row]
        ),
        "graph_traversal_receipt": recorder.build_receipt(decisions=[row]),
    }
    failures = validate_canonical_section_plan(plan)
    assert "decision_0_selected_without_authority" in failures
    with pytest.raises(ValueError, match="canonical C0.3 plan invalid"):
        finalize_canonical_section_plan(plan)


def _build_competencies_plan(*, target_role: str, jd_text: str) -> dict:
    plan, ordered, allowed = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO,
        section_id="competencies",
        target_role=target_role,
        jd_text=jd_text,
    )
    assert ordered
    assert allowed
    return plan


def test_role_selector_emits_exhaustive_replayable_traversal() -> None:
    plan = _build_competencies_plan(
        target_role="SVP Agentic Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform governance",
    )
    assert plan["schema_version"] == CANONICAL_PLAN_SCHEMA_VERSION
    assert plan["source_authority_contract"]["targeting_inputs_are_non_authority"] is True
    assert plan["pretarget_authority_receipt"]["targeting_consulted_count"] == 0
    assert plan["pretarget_authority_receipt"]["authority_before_targeting_pass"] is True

    decisions = plan["graph_candidate_decision_ledger"]
    receipt = plan["graph_candidate_receipt"]
    traversal = plan["graph_traversal_receipt"]
    assert decisions
    assert receipt["candidate_conservation_pass"] is True
    assert traversal["pass"] is True
    assert traversal["replayable"] is True
    assert traversal["events"]
    assert traversal["authority_event_count"] >= len(decisions)
    assert len({row["candidate_path_id"] for row in decisions}) == len(decisions)
    assert all(row["decision"] in {"selected", "rejected"} for row in decisions)
    assert all(
        row["authority_pass"] is True
        for row in decisions
        if row["decision"] == "selected"
    )
    leaf_rows = [row for row in decisions if row["candidate_type"] == "leaf_skill"]
    assert len(leaf_rows) > len(plan["selected_skill_ids"])
    assert any(row["decision"] == "rejected" for row in leaf_rows)
    assert len(plan["selected_skill_ids"]) == len(set(plan["selected_skill_ids"]))
    assert len(plan["selected_metrics"]) == len(set(plan["selected_metrics"]))


def test_targeting_changes_ranking_not_authority_frontier() -> None:
    agentic = _build_competencies_plan(
        target_role="SVP Agentic Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform governance",
    )
    insurance = _build_competencies_plan(
        target_role="SVP IT Strategy & Innovation",
        jd_text="insurance brokerage policy administration Guidewire claims cloud architecture",
    )

    def authority_map(plan: dict) -> dict[str, tuple[bool, tuple[str, ...]]]:
        return {
            str(row["candidate_path_id"]): (
                bool(row["authority_pass"]),
                tuple((row.get("authority") or {}).get("reason_codes") or []),
            )
            for row in plan["graph_candidate_decision_ledger"]
        }

    assert authority_map(agentic) == authority_map(insurance)
    assert agentic["target_role_profile"] != insurance["target_role_profile"]


def test_selected_graph_plan_directly_binds_c02_atom() -> None:
    plan = _build_competencies_plan(
        target_role="SVP Agentic Engineering",
        jd_text="agentic runtime governance platform",
    )
    fact = plan["facts"][0]
    fact_id = fact["fact_id"]
    c03 = expand_c03_graph_bindings(
        section_id="competencies",
        atoms=[
            {
                "fact_id": fact_id,
                "proof_status": "proof_eligible",
                "source_span_ref": f"ledger:{fact_id}",
                "skill_tags": [],
                "metric_refs": [],
                "career_phase_refs": [],
            }
        ],
        repo_root=REPO,
        selected_graph_plan=plan,
    )
    binding = c03["bindings"][0]
    assert binding["graph_support_strength"] == "DIRECT"
    assert binding["claim_support_allowed"] is True
    assert set(binding["graph_node_refs"]) == set(fact["graph_skill_node_ids"])
    assert "selected_graph_evidence_plan" in binding["binding_query_source"]
    assert c03["broad_fact_link_fallback_used"] is False
    assert c03["label_tag_proof_fallback_used"] is False
    assert c03["graph_candidate_receipt"]["candidate_conservation_pass"] is True
    assert c03["graph_traversal_receipt"]["pass"] is True


def test_missing_claim_eligible_frontier_does_not_become_proof() -> None:
    c03 = expand_c03_graph_bindings(
        section_id="competencies",
        atoms=[
            {
                "fact_id": "fact_does_not_exist_w1_w3",
                "proof_status": "claim_eligible",
                "source_span_ref": "test:missing",
                "skill_tags": ["invented skill label"],
                "metric_refs": [],
                "career_phase_refs": [],
            }
        ],
        repo_root=REPO,
    )
    binding = c03["bindings"][0]
    assert binding["claim_support_allowed"] is False
    assert binding["graph_support_strength"] == "NONE"
    assert binding["broad_fact_link_fallback_used"] is False
    assert binding["label_tag_proof_fallback_used"] is False


def test_missing_proof_frontier_fails_closed() -> None:
    with pytest.raises(C03GraphSelectionError, match="missing_direct_frontier"):
        expand_c03_graph_bindings(
            section_id="competencies",
            atoms=[
                {
                    "fact_id": "fact_does_not_exist_proof_w1_w3",
                    "proof_status": "proof_eligible",
                    "source_span_ref": "test:missing",
                    "skill_tags": ["invented skill label"],
                    "metric_refs": [],
                    "career_phase_refs": [],
                }
            ],
            repo_root=REPO,
        )


def test_sqlite_authority_gate_rejects_explicit_section_block(tmp_path: Path) -> None:
    db_path = tmp_path / "c03_authority.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=REPO, db_path=db_path)
    baseline = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=db_path,
        max_skills_per_fact=1,
    )
    assert baseline["selected_candidates"]
    skill_id = baseline["selected_candidates"][0]["skill_id"]
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            INSERT INTO section_eligibility (
                node_id, section_id, allowed, claim_policy, reason, blocked_reason
            ) VALUES (?, ?, 0, 'blocked', 'test', 'w1_w3_test_block')
            ON CONFLICT(node_id, section_id) DO UPDATE SET
                allowed=0, claim_policy='blocked', blocked_reason='w1_w3_test_block'
            """,
            (skill_id, "executive_summary"),
        )
        conn.commit()
    finally:
        conn.close()

    out = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        pillar_hints=["pillar_agentic_runtime_governance"],
        repo_root=REPO,
        db_path=db_path,
        max_skills_per_fact=3,
    )
    assert skill_id not in {row["skill_id"] for row in out["selected_candidates"]}
    blocked = [
        row
        for row in out["candidate_decision_ledger"]
        if row["candidate_id"] == skill_id
    ]
    assert blocked
    assert blocked[0]["decision"] == "rejected"
    assert blocked[0]["authority_pass"] is False
    assert "w1_w3_test_block" in blocked[0]["authority"]["reason_codes"]


def test_graph_expansion_source_has_no_legacy_claim_fallbacks() -> None:
    source = inspect.getsource(expand_c03_graph_bindings)
    assert "eligible_links" not in source
    assert "capability_tag_label" not in source
