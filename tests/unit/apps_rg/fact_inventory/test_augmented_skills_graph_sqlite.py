"""apps-test-model: APP CONTRACT.

SQLite materialization + C0.3 context assembly for augmented skills graph.
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    C03_SQLITE_MATERIALIZER_CODE_VERSION,
    apply_operator_archive_promotions,
    build_skill_rows_by_id,
    canonical_node_type,
    collect_high_and_exec_summary_counts,
    confidence_grade_for_skill_row,
    derive_confidence_grade,
    has_valid_human_confirmed_archive_promotion,
    infer_node_type_from_id,
    load_graph_metadata_row,
    load_augmented_skills_graph,
    load_candidate_fact_promotion_registry,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
    resolve_confidence_grade,
    validate_hardened_materialized_sqlite,
    validate_materialized_sqlite,
)
from apps_rg.runtime.c03_graph_sqlite_context import (
    PROOF_CLASSIFICATION,
    assemble_c03_graph_sqlite_context,
    enrich_c03_bound_with_sqlite_context,
    ensure_c03_graph_sqlite,
    query_partner_architecture_competency_candidates,
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
    assert "c03_skill_selection_features" in tables
    assert "c03_role_family_skill_weights" in tables
    assert "graph_paths" in tables
    assert "graph_neighborhoods" in tables
    assert "graph_sibling_links" in tables
    assert "resume_metric_usage" in tables
    assert "section_evidence_budget" in tables
    assert "graph_selection_rejections" in tables
    assert "graph_metadata" in tables


def test_materializer_code_version_written_to_metadata(sqlite_db: Path) -> None:
    conn = open_graph_sqlite(repo_root=REPO, db_path=sqlite_db)
    try:
        meta = load_graph_metadata_row(conn)
    finally:
        conn.close()
    summary = meta["graph_count_summary"]
    assert (
        summary["c03_sqlite_materializer_code_version"]
        == C03_SQLITE_MATERIALIZER_CODE_VERSION
    )

    val = validate_materialized_sqlite(repo_root=REPO, db_path=sqlite_db)
    assert val["c03_sqlite_materializer_code_version"] == C03_SQLITE_MATERIALIZER_CODE_VERSION


def test_ensure_c03_graph_sqlite_rebuilds_stale_materializer_version(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        raw = conn.execute(
            "SELECT graph_count_summary FROM graph_metadata ORDER BY materialized_at DESC LIMIT 1"
        ).fetchone()[0]
        summary = json.loads(raw)
        summary["c03_sqlite_materializer_code_version"] = "stale-test-version"
        conn.execute(
            """
            UPDATE graph_metadata
            SET graph_count_summary = ?
            """,
            (json.dumps(summary, sort_keys=True),),
        )
        conn.commit()
    finally:
        conn.close()

    ensured = ensure_c03_graph_sqlite(REPO, sqlite_db)
    assert ensured == sqlite_db
    conn = open_graph_sqlite(repo_root=REPO, db_path=sqlite_db)
    try:
        meta = load_graph_metadata_row(conn)
    finally:
        conn.close()
    assert (
        meta["graph_count_summary"]["c03_sqlite_materializer_code_version"]
        == C03_SQLITE_MATERIALIZER_CODE_VERSION
    )


def test_run_materialize_cli_smoke_skip_parity(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["APPS_RG_AUGMENTED_SKILLS_GRAPH_SQLITE_PATH"] = str(tmp_path / "cli_graph.sqlite")
    env["APPS_RG_AUGMENTED_SKILLS_GRAPH_SQLITE_RECEIPT_DIR"] = str(tmp_path / "receipts")
    proc = subprocess.run(
        [
            sys.executable,
            "apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py",
            "--skip-parity",
        ],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "cli_graph.sqlite").is_file()
    receipt = tmp_path / "receipts/augmented_skills_graph_sqlite_closeout_receipt.json"
    assert receipt.is_file()
    data = json.loads(receipt.read_text(encoding="utf-8"))
    assert data["STATUS"] == "PASS"
    assert data["C03_SQLITE_MATERIALIZER_CODE_VERSION"] == C03_SQLITE_MATERIALIZER_CODE_VERSION


def test_validate_materialized_passes(sqlite_db: Path) -> None:
    graph = load_augmented_skills_graph(repo_root=REPO)
    out = validate_materialized_sqlite(graph=graph, repo_root=REPO, db_path=sqlite_db)
    assert out["status"] == "PASS"
    assert out["node_count"] >= int(graph["graph_metadata"]["node_count"])
    unique_edges = len(
        {str(e["edge_id"]) for e in graph["graph_edges"] if isinstance(e, dict) and e.get("edge_id")}
    )
    assert out["edge_count"] >= unique_edges
    assert out["skill_fact_link_count"] > 0
    assert out["c03_skill_selection_feature_count"] > 0
    assert out["c03_role_family_skill_weight_count"] > 0
    assert out["graph_path_count"] > 0
    assert out["graph_neighborhood_count"] > 0
    assert out["graph_sibling_link_count"] > 0
    assert out["section_evidence_budget_count"] > 0
    assert out["validated_edges_missing_rationale_count"] == 0
    assert out["broad_skills_ledger_status"] == "non_authority"


def test_graph_edges_preserve_notes_and_reverse_view(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        row = conn.execute(
            """
            SELECT rationale, projection_behavior, external_claim_policy, validation_status
            FROM graph_edges
            WHERE edge_id = 'edge_identity_epoch_epoch_actuarial_financial_engineering'
            """
        ).fetchone()
        reverse = conn.execute(
            """
            SELECT source_node_id, target_node_id, edge_type, rationale
            FROM graph_edges_reverse
            WHERE edge_id = 'edge_identity_epoch_epoch_actuarial_financial_engineering'
            """
        ).fetchone()
    finally:
        conn.close()
    assert row == (
        "Identity grounded in career epoch",
        "graph_traversal",
        "skill_projection_not_proof",
        "validated",
    )
    assert reverse == (
        "epoch_actuarial_financial_engineering",
        "identity_amit_ayer_governed_ai_platform_leader",
        "identity_supported_by_epoch_reverse",
        "Identity grounded in career epoch",
    )


def test_graph_path_index_tables_are_materialized(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        skill_fact_path = conn.execute(
            """
            SELECT path_signature, proof_fact_ids_json, path_score
            FROM graph_paths
            WHERE start_node_id = 'skill_runtime_gate_mesh_design'
              AND end_node_id = 'fact_engineering_platform_001'
            ORDER BY path_depth ASC, path_score DESC
            LIMIT 1
            """
        ).fetchone()
        sibling = conn.execute(
            """
            SELECT sibling_node_id, sibling_reason, shared_parent_node_id
            FROM graph_sibling_links
            WHERE node_id = 'skill_runtime_gate_mesh_design'
            ORDER BY sibling_score DESC, sibling_node_id
            LIMIT 1
            """
        ).fetchone()
        neighborhood_count = conn.execute(
            """
            SELECT COUNT(*) FROM graph_neighborhoods
            WHERE center_node_id = 'skill_runtime_gate_mesh_design'
            """
        ).fetchone()[0]
        budget = conn.execute(
            """
            SELECT max_metric_reuse, required_node_types_json, preferred_edge_types_json
            FROM section_evidence_budget
            WHERE section_id = 'executive_summary'
              AND role_family_key = 'SVP_ENGINEERING_AI_PLATFORM'
            """
        ).fetchone()
    finally:
        conn.close()
    assert skill_fact_path is not None
    assert skill_fact_path[0] == "skill_runtime_gate_mesh_design->fact_engineering_platform_001"
    assert "fact_engineering_platform_001" in json.loads(skill_fact_path[1])
    assert float(skill_fact_path[2]) > 0
    assert sibling is not None
    assert sibling[0].startswith("skill_")
    assert sibling[1] in ("shared_fact", "shared_parent:capability_domain_contains_skill", "shared_parent:epoch_contains_skill")
    assert sibling[2]
    assert neighborhood_count > 0
    assert budget is not None
    assert int(budget[0]) == 1
    assert "skill" in json.loads(budget[1])
    assert "skill_supported_by_fact" in json.loads(budget[2])


def test_c03_skill_selection_features_are_generated_from_json(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        row = conn.execute(
            """
            SELECT skill_id, metric_bucket, skill_family, source_fact_count, source_authority
            FROM c03_skill_selection_features
            WHERE skill_id = 'skill_c03_metric_heterogeneity_selection'
            """
        ).fetchone()
        blank_buckets = conn.execute(
            """
            SELECT COUNT(*) FROM c03_skill_selection_features
            WHERE metric_bucket IS NULL OR metric_bucket = ''
            """
        ).fetchone()[0]
    finally:
        conn.close()
    assert row is not None
    assert row[1] == "risk_governance"
    assert row[2]
    assert int(row[3]) >= 1
    assert row[4] == "augmented_skills_graph"
    assert blank_buckets == 0


def test_partner_architecture_competency_candidates_view(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        rows = query_partner_architecture_competency_candidates(
            conn,
            role_family_key="ANTHROPIC_PARTNERSHIPS_APPLIED_AI",
            limit=20,
        )
        skill_ids = {str(row["skill_id"]) for row in rows}
        forbidden_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM v_partner_architecture_competency_candidates
            WHERE LOWER(COALESCE(fact_id, '')) LIKE '%insurtech%'
               OR LOWER(COALESCE(fact_id, '')) LIKE '%ey%'
            """
        ).fetchone()[0]
    finally:
        conn.close()
    assert rows
    assert "skill_partner_joint_solution_development" in skill_ids
    assert "skill_sr_w12_industry_reference_architecture" in skill_ids
    assert "skill_partner_ai_architecture_advisory" in skill_ids
    assert "skill_sr_w12_joint_ai_solution_development" in skill_ids
    assert len(skill_ids) >= 5
    assert forbidden_count == 0


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
    assert rec["partner_architecture_sqlite_query_status"] == "AVAILABLE"
    assert isinstance(rec["partner_architecture_candidate_rows"], list)


def test_c03_sqlite_context_keeps_resume_skill_source_trace(sqlite_db: Path) -> None:
    bundle = assemble_c03_graph_sqlite_context(
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        repo_root=REPO,
        db_path=sqlite_db,
    )
    fact_links = bundle["receipt"]["selected_fact_links"]
    resume_skill_ids = {
        str(link["skill_id"])
        for link in fact_links
        if link.get("claim_eligibility") and link.get("external_eligible")
    }
    rows_by_id = build_skill_rows_by_id(load_augmented_skills_graph(repo_root=REPO))
    resume_sourced = [
        rows_by_id[sid]
        for sid in resume_skill_ids
        if sid in rows_by_id and rows_by_id[sid].get("source_resume_files")
    ]
    assert resume_sourced, "C0.3 apps_rg context must resolve to actual resume-backed skills"
    assert all(row.get("fact_id_links") for row in resume_sourced)


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
