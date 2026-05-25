"""SQLite materialization + C0.3 context assembly for augmented skills graph."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    apply_operator_archive_promotions,
    build_skill_rows_by_id,
    canonical_node_type,
    collect_high_and_exec_summary_counts,
    confidence_grade_for_skill_row,
    derive_confidence_grade,
    has_valid_human_confirmed_archive_promotion,
    infer_node_type_from_id,
    load_augmented_skills_graph,
    load_candidate_fact_promotion_registry,
    materialize_augmented_skills_graph_sqlite,
    resolve_confidence_grade,
    validate_hardened_materialized_sqlite,
    validate_materialized_sqlite,
)
from apps_rg.runtime.c03_graph_sqlite_context import (
    PROOF_CLASSIFICATION,
    assemble_c03_graph_sqlite_context,
    enrich_c03_bound_with_sqlite_context,
)

REPO = Path(__file__).resolve().parents[4]


@pytest.fixture
def sqlite_db(tmp_path: Path) -> Path:
    db = tmp_path / "test_graph.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=REPO, db_path=db)
    return db


def test_canonical_node_type_mappings() -> None:
    assert canonical_node_type("domain_pillar") == "pillar"
    assert canonical_node_type("skill_row") == "skill"
    assert canonical_node_type("fact_engineering_platform_001") == "fact"
    assert infer_node_type_from_id("exp_insurtech_001") == "employment"
    assert infer_node_type_from_id("bul_insurtech_001") == "locked_bullet"
    assert infer_node_type_from_id("policy_external_claim_policy") == "policy"
    assert infer_node_type_from_id("domain_agentic_systems_architecture") == "capability_domain"


def test_confidence_override_blocked_without_human_confirmation() -> None:
    row = {
        "skill_id": "skill_governed_agentic_systems_architecture",
        "activation_status": "ACTIVE",
        "support_level": "DERIVED_SUPPORTED",
        "fact_id_links": ["fact_engineering_platform_001"],
        "confidence_grade": "HIGH",
        "visibility_rule": "role_family_match",
        "external_claim_policy": "derived_supported_with_fact",
    }
    registry = load_candidate_fact_promotion_registry(repo_root=REPO)
    resolved = resolve_confidence_grade(row, has_fact_link=True, candidate_registry=registry)
    assert resolved["derived_grade"] == "MEDIUM"
    assert resolved["effective_grade"] == "MEDIUM"
    assert resolved["override_blocked_reason"] == (
        "confidence_override_blocked_missing_human_confirmation"
    )
    assert not has_valid_human_confirmed_archive_promotion(row)


def test_confidence_override_allowed_with_human_confirmed_archive_promotion() -> None:
    row = {
        "skill_id": "skill_governed_agentic_systems_architecture",
        "activation_status": "ACTIVE",
        "support_level": "DERIVED_SUPPORTED",
        "fact_id_links": ["fact_engineering_platform_001"],
        "confidence_grade": "HIGH",
        "human_confirmed_archive_promotion": {
            "human_confirmed_by": "reviewer",
            "human_confirmed_at": "2026-05-20T12:00:00Z",
            "source_fact_ids": ["fact_engineering_platform_001"],
            "override_reason": "archive_snippet_verified",
        },
    }
    registry = load_candidate_fact_promotion_registry(repo_root=REPO)
    resolved = resolve_confidence_grade(row, has_fact_link=True, candidate_registry=registry)
    assert resolved["effective_grade"] == "HIGH"
    assert has_valid_human_confirmed_archive_promotion(row)


def test_governance_archive_facts_still_derive_high() -> None:
    row = {
        "skill_id": "skill_capital_regulatory_capital",
        "activation_status": "ACTIVE_CONFIRMED",
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "fact_id_links": ["fact_governance_003"],
        "visibility_rule": "role_family_match",
        "external_claim_policy": "atomic_fact_default_external_proof",
    }
    registry = load_candidate_fact_promotion_registry(repo_root=REPO)
    assert (
        confidence_grade_for_skill_row(row, has_fact_link=True, candidate_registry=registry)
        == "HIGH"
    )


def test_candidate_facts_do_not_auto_promote_to_high() -> None:
    row = {
        "skill_id": "skill_context_engineering",
        "activation_status": "ACTIVE_CONFIRMED",
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "fact_id_links": ["fact_engineering_platform_003"],
        "visibility_rule": "role_family_match",
        "external_claim_policy": "atomic_fact_default_external_proof",
    }
    registry = load_candidate_fact_promotion_registry(repo_root=REPO)
    assert (
        confidence_grade_for_skill_row(row, has_fact_link=True, candidate_registry=registry)
        == "MEDIUM"
    )


def test_operator_archive_promotion_yields_genai_high(tmp_path: Path) -> None:
    graph = load_augmented_skills_graph(repo_root=REPO)
    before = collect_high_and_exec_summary_counts(graph, repo_root=REPO)
    before_high = list(before.get("track_genai_agentic_high_skills") or [])

    payload = json.loads(json.dumps(graph))
    result = apply_operator_archive_promotions(payload)
    if before_high:
        assert len(before_high) >= 9
        row = build_skill_rows_by_id(graph)["skill_governed_agentic_systems_architecture"]
        assert row["confidence_grade"] == "HIGH"
        assert row["activation_status"] == "ACTIVE_CONFIRMED"
        assert has_valid_human_confirmed_archive_promotion(row)
        return
    assert len(result["promoted"]) == 9
    assert result["rejected"] == []

    after = collect_high_and_exec_summary_counts(payload, repo_root=REPO)
    assert len(after.get("track_genai_agentic_high_skills") or []) == 9
    assert after["high_skill_count"] == before["high_skill_count"] + 9
    assert after["executive_summary_allowed_count"] == (
        before["executive_summary_allowed_count"] + 9
    )

    row = build_skill_rows_by_id(payload)["skill_governed_agentic_systems_architecture"]
    assert row["confidence_grade"] == "HIGH"
    assert row["activation_status"] == "ACTIVE_CONFIRMED"
    assert row["support_level"] == "DIRECT_FROM_RESUME_ARCHIVE"
    assert has_valid_human_confirmed_archive_promotion(row)


def test_executive_summary_allows_only_high_confirmed_fact_linked(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        bad = conn.execute(
            """
            SELECT se.node_id, n.confidence, n.activation_status
            FROM section_eligibility se
            JOIN graph_nodes n ON n.node_id = se.node_id
            WHERE se.section_id = 'executive_summary' AND se.allowed = 1
              AND n.node_type = 'skill'
              AND (
                n.confidence != 'HIGH'
                OR n.activation_status NOT IN ('ACTIVE', 'ACTIVE_CONFIRMED')
                OR n.external_eligible != 1
              )
            """
        ).fetchall()
        blocked_high = conn.execute(
            """
            SELECT node_id FROM graph_nodes
            WHERE node_type='skill' AND confidence='HIGH'
              AND (
                activation_status IN (
                  'DRAFT','INTERNAL_ONLY','USER_CONFIRMED_PENDING_SOURCE'
                )
                OR support_level IN (
                  'REPO_EVIDENCE_PORTFOLIO','INTERNAL_ONLY',
                  'USER_CONFIRMED_PENDING_SOURCE'
                )
                OR node_id LIKE '%airline%'
                OR node_id LIKE '%brokerage%'
                OR node_id LIKE '%underwriting%'
                OR node_id LIKE '%claims%'
                OR node_id LIKE '%marketplace%'
              )
            """
        ).fetchall()
    finally:
        conn.close()
    assert bad == []
    assert blocked_high == []


def test_derive_confidence_grade_mapping() -> None:
    assert (
        derive_confidence_grade(
            {
                "activation_status": "ACTIVE_CONFIRMED",
                "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
                "fact_id_links": ["fact_a"],
                "visibility_rule": "role_family_match",
                "external_claim_policy": "atomic_fact_default_external_proof",
            },
            has_fact_link=True,
        )
        == "HIGH"
    )
    assert (
        derive_confidence_grade(
            {
                "activation_status": "ACTIVE",
                "support_level": "DERIVED_SUPPORTED",
                "fact_id_links": ["fact_b"],
                "visibility_rule": "role_family_match",
                "external_claim_policy": "derived_supported_with_fact",
            },
            has_fact_link=True,
        )
        == "MEDIUM"
    )
    assert (
        derive_confidence_grade(
            {
                "activation_status": "DRAFT",
                "support_level": "DERIVED_SUPPORTED",
                "fact_id_links": [],
                "visibility_rule": "role_family_match",
            }
        )
        == "LOW"
    )
    assert (
        derive_confidence_grade(
            {
                "activation_status": "DRAFT",
                "support_level": "REPO_EVIDENCE_PORTFOLIO",
                "fact_id_links": [],
                "visibility_rule": "never_external",
            }
        )
        == "BLOCKED"
    )


def test_validate_hardened_materialized_passes(sqlite_db: Path) -> None:
    graph = load_augmented_skills_graph(repo_root=REPO)
    out = validate_hardened_materialized_sqlite(graph=graph, repo_root=REPO, db_path=sqlite_db)
    assert out["status"] == "PASS"
    assert out["orphan_edge_count"] == 0
    assert out["dup_triple_count"] == 0
    assert out.get("high_skill_count", 0) > 0
    assert out.get("executive_summary_allowed_count", 0) > 0


def test_materialize_creates_six_tables(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        }
    finally:
        conn.close()
    assert "graph_nodes" in tables
    assert "graph_edges" in tables
    assert "skill_fact_links" in tables
    assert "section_eligibility" in tables
    assert "role_family_projection" in tables
    assert "graph_metadata" in tables


def test_validate_materialized_passes(sqlite_db: Path) -> None:
    graph = load_augmented_skills_graph(repo_root=REPO)
    out = validate_materialized_sqlite(graph=graph, repo_root=REPO, db_path=sqlite_db)
    assert out["status"] == "PASS"
    assert out["node_count"] >= int(graph["graph_metadata"]["node_count"])
    unique_edges = len(
        {str(e["edge_id"]) for e in graph["graph_edges"] if isinstance(e, dict) and e.get("edge_id")}
    )
    assert out["edge_count"] == unique_edges
    assert out["skill_fact_link_count"] > 0
    assert out["broad_skills_ledger_status"] == "non_authority"


def test_sqlite_confidence_grade_not_support_level(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        support_high = conn.execute(
            "SELECT COUNT(*) FROM graph_nodes WHERE node_type='skill' AND support_level='HIGH'"
        ).fetchone()[0]
        confidence_high = conn.execute(
            "SELECT COUNT(*) FROM graph_nodes WHERE node_type='skill' AND confidence='HIGH'"
        ).fetchone()[0]
        assert support_high == 0
        assert confidence_high > 0
    finally:
        conn.close()


def test_no_duplicate_node_ids(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        dup = conn.execute(
            "SELECT node_id, COUNT(*) c FROM graph_nodes GROUP BY node_id HAVING c > 1"
        ).fetchall()
    finally:
        conn.close()
    assert dup == []


def test_c03_context_receipt_fields(sqlite_db: Path) -> None:
    bundle = assemble_c03_graph_sqlite_context(
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        repo_root=REPO,
        db_path=sqlite_db,
    )
    rec = bundle["receipt"]
    assert rec["sqlite_db_path"]
    assert rec["graph_version"]
    assert rec["graph_hash"]
    assert rec["proof_classification"] == PROOF_CLASSIFICATION
    assert "broad_skills_ledger_non_authority" in rec["explicit_non_claims"]
    assert rec["c03_integration_status"] == "SQLITE_CONTEXT_AVAILABLE"
    assert isinstance(rec["selected_nodes"], list)
    assert isinstance(rec["section_eligibility"], list)


def test_enrich_c03_bound_attaches_sqlite(sqlite_db: Path) -> None:
    doc = enrich_c03_bound_with_sqlite_context(
        {"section_id": "competencies", "c03_graphrag_bound_status": "BOUND"},
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        repo_root=REPO,
    )
    assert doc.get("c03_sqlite_context_status") in ("ATTACHED", "UNAVAILABLE")
    if doc["c03_sqlite_context_status"] == "ATTACHED":
        assert doc.get("c03_sqlite_proof_classification") == PROOF_CLASSIFICATION
        assert Path(str(doc["c03_sqlite_context_receipt_path"])).name.endswith(".json")
