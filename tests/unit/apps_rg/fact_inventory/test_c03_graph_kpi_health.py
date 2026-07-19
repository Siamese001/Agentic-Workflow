"""apps-test-model: APP CONTRACT."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import canonical_node_type
from apps_rg.fact_inventory.c03_graph_kpi_health import (
    build_c03_graph_health_receipt,
    compute_operational_cohort_digest,
    load_health_policy,
    main,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    collect_canonical_graph_issues,
)

GENERATED_AT = "2026-07-18T16:00:00Z"
def _canonical_payload() -> dict[str, Any]:
    graph_nodes = [
        {
            "node_id": "domain_platform",
            "node_type": "capability_domain",
            "label": "Platform",
            "source_refs": ["source://domain/platform"],
        },
        {
            "node_id": "epoch_recent",
            "node_type": "career_epoch",
            "label": "Recent",
            "source_refs": ["source://epoch/recent"],
        },
        {
            "node_id": "employment_current",
            "node_type": "employment",
            "label": "Current role",
            "start_date": "2024-01-01",
            "is_current": True,
            "source_refs": ["source://employment/current"],
        },
        {
            "node_id": "fact_shared",
            "node_type": "atomic_proof_fact",
            "label": "Shared fact",
            "source_refs": ["source://fact/shared#L1"],
        },
    ]
    skill_rows: list[dict[str, Any]] = []
    graph_edges: list[dict[str, Any]] = []
    for index, bucket in enumerate(("revenue_growth", "risk_governance", "platform_scale"), 1):
        skill_id = f"skill_{index}"
        graph_nodes.append(
            {
                "node_id": skill_id,
                "node_type": "skill",
                "label": f"Skill {index}",
                "source_refs": [f"source://skill/{index}#L1"],
            }
        )
        skill_rows.append(
            {
                "skill_id": skill_id,
                "fact_id_links": ["fact_shared"],
                "source_snippets": [f"Evidence snippet {index}"],
                "source_resume_files": ["resume.docx"],
                "domain_id": "domain_platform",
                "career_epoch": "epoch_recent",
                "metric_bucket": bucket,
            }
        )
        graph_edges.extend(
            [
                {
                    "edge_id": f"edge_domain_skill_{index}",
                    "edge_type": "capability_domain_contains_skill",
                    "source_node_id": "domain_platform",
                    "target_node_id": skill_id,
                },
                {
                    "edge_id": f"edge_skill_fact_{index}",
                    "edge_type": "skill_supported_by_fact",
                    "source_node_id": skill_id,
                    "target_node_id": "fact_shared",
                },
            ]
        )
    for node in graph_nodes:
        node["support_level"] = "DIRECT_FROM_RESUME_ARCHIVE"
        node["visibility_rule"] = "role_family_match"
        node["external_claim_policy"] = "derived_supported_with_fact"
    return {
        "metadata": {
            "schema_version": "fixture.canonical.v1",
            "skill_row_count": len(skill_rows),
        },
        "graph_metadata": {
            "schema_version": "fixture.graph.v1",
            "node_count": len(graph_nodes),
            "edge_count": len(graph_edges),
        },
        "graph_nodes": graph_nodes,
        "graph_edges": graph_edges,
        "skill_rows": skill_rows,
    }


def _canonical_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_canonical(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_sqlite(path: Path, payload: dict[str, Any], *, ledger_hash: str | None = None) -> None:
    nodes = payload["graph_nodes"]
    edges = payload["graph_edges"]
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
        """
        CREATE TABLE graph_nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT NOT NULL
        );
        CREATE TABLE graph_edges (
            edge_id TEXT PRIMARY KEY,
            source_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            target_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            edge_type TEXT NOT NULL
        );
        CREATE TABLE skill_fact_links (
            skill_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            fact_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            PRIMARY KEY (skill_id, fact_id)
        );
        CREATE TABLE section_eligibility (
            node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            section_id TEXT NOT NULL,
            PRIMARY KEY (node_id, section_id)
        );
        CREATE TABLE c03_skill_selection_features (
            skill_id TEXT PRIMARY KEY REFERENCES graph_nodes(node_id),
            metric_bucket TEXT NOT NULL
        );
        CREATE TABLE c03_role_family_skill_weights (
            skill_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            role_family_key TEXT NOT NULL,
            weight REAL NOT NULL,
            PRIMARY KEY (skill_id, role_family_key)
        );
        CREATE TABLE graph_paths (
            path_id TEXT PRIMARY KEY,
            start_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            end_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            path_depth INTEGER NOT NULL,
            node_path_json TEXT NOT NULL,
            edge_path_json TEXT NOT NULL,
            edge_types_json TEXT NOT NULL
        );
        CREATE TABLE graph_sibling_links (
            node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            sibling_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            shared_parent_node_id TEXT NOT NULL,
            shared_edge_type TEXT NOT NULL,
            PRIMARY KEY (node_id, sibling_node_id)
        );
        CREATE TABLE graph_neighborhoods (
            center_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            neighbor_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            distance INTEGER NOT NULL,
            connecting_path_json TEXT NOT NULL,
            edge_types_json TEXT NOT NULL,
            PRIMARY KEY (center_node_id, neighbor_node_id, distance)
        );
        CREATE TABLE graph_metadata (
            graph_version TEXT PRIMARY KEY,
            materialized_at TEXT NOT NULL,
            ledger_hash TEXT NOT NULL,
            graph_count_summary TEXT NOT NULL
        );
        CREATE VIEW graph_edges_reverse AS
        SELECT edge_id,
               target_node_id AS source_node_id,
               source_node_id AS target_node_id,
               edge_type || '_reverse' AS edge_type
        FROM graph_edges;
        """
    )
    conn.executemany(
        "INSERT INTO graph_nodes(node_id,node_type) VALUES(?,?)",
        [
            (
                row["node_id"],
                canonical_node_type(row["node_type"], node_id=row["node_id"]),
            )
            for row in nodes
        ],
    )
    conn.executemany(
        "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES(?,?,?,?)",
        [(row["edge_id"], row["source_node_id"], row["target_node_id"], row["edge_type"]) for row in edges],
    )
    for row in payload["skill_rows"]:
        conn.execute(
            "INSERT INTO skill_fact_links(skill_id,fact_id) VALUES(?,?)",
            (row["skill_id"], "fact_shared"),
        )
        conn.execute(
            "INSERT INTO section_eligibility(node_id,section_id) VALUES(?,?)",
            (row["skill_id"], "competencies"),
        )
        conn.execute(
            "INSERT INTO c03_skill_selection_features(skill_id,metric_bucket) VALUES(?,?)",
            (row["skill_id"], row["metric_bucket"]),
        )
        conn.execute(
            "INSERT INTO c03_role_family_skill_weights(skill_id,role_family_key,weight) VALUES(?,?,?)",
            (row["skill_id"], "fixture_role", 1.0),
        )
    for edge in edges:
        conn.execute(
            """
            INSERT INTO graph_paths(
                path_id,start_node_id,end_node_id,path_depth,
                node_path_json,edge_path_json,edge_types_json
            ) VALUES(?,?,?,?,?,?,?)
            """,
            (
                f"path_{edge['edge_id']}",
                edge["source_node_id"],
                edge["target_node_id"],
                1,
                json.dumps([edge["source_node_id"], edge["target_node_id"]]),
                json.dumps([edge["edge_id"]]),
                json.dumps([edge["edge_type"]]),
            ),
        )
        conn.executemany(
            """
            INSERT INTO graph_neighborhoods(
                center_node_id,neighbor_node_id,distance,
                connecting_path_json,edge_types_json
            ) VALUES(?,?,?,?,?)
            """,
            [
                (
                    edge["source_node_id"],
                    edge["target_node_id"],
                    1,
                    json.dumps([edge["source_node_id"], edge["target_node_id"]]),
                    json.dumps([edge["edge_type"]]),
                ),
                (
                    edge["target_node_id"],
                    edge["source_node_id"],
                    1,
                    json.dumps([edge["target_node_id"], edge["source_node_id"]]),
                    json.dumps([f"{edge['edge_type']}_reverse"]),
                ),
            ],
        )
    skill_ids = [row["skill_id"] for row in payload["skill_rows"]]
    for node_id in skill_ids:
        for sibling_id in skill_ids:
            if node_id == sibling_id:
                continue
            conn.execute(
                """
                INSERT INTO graph_sibling_links(
                    node_id,sibling_node_id,shared_parent_node_id,shared_edge_type
                ) VALUES(?,?,?,?)
                """,
                (node_id, sibling_id, "domain_platform", "capability_domain_contains_skill"),
            )
    summary = {
        "c03_sqlite_materializer_code_version": "fixture.materializer.v1",
        "graph_index_schema_version": "fixture.path_index.v1",
        "node_count_sqlite": len(nodes),
        "edge_count_sqlite": len(edges),
    }
    conn.execute(
        "INSERT INTO graph_metadata VALUES(?,?,?,?)",
        (
            "fixture.sqlite.graph.v1",
            GENERATED_AT,
            ledger_hash or _canonical_digest(payload),
            json.dumps(summary, sort_keys=True),
        ),
    )
    conn.commit()
    conn.close()


def _operational_evidence() -> dict[str, Any]:
    evidence = {
        "schema_version": "apps_rg.c03_graph_health_operational_evidence.v1",
        "authority_status": "VERIFIED",
        "cohort_id": "fixture-frozen-cohort",
        "decision_safe_regression": {"passed": 3, "total": 3},
        "source_currentness": {"current": 3, "total": 3},
        "source_freshness": {"fresh": 3, "total": 3},
        "hitl_approval": {"approved": 3, "total": 3},
        "write_audit": {"audited": 3, "total": 3},
        "p0_sla": {"within_sla": 2, "total": 2},
        "p1_sla": {"within_sla": 2, "total": 2},
    }
    evidence["cohort_digest"] = compute_operational_cohort_digest(evidence)
    return evidence


def _metric(receipt: dict[str, Any], metric_id: str) -> dict[str, Any]:
    return next(row for row in receipt["metrics"] if row["metric_id"] == metric_id)


def _fixture_paths(tmp_path: Path) -> tuple[Path, Path, dict[str, Any]]:
    payload = _canonical_payload()
    canonical_path = tmp_path / "canonical.json"
    sqlite_path = tmp_path / "graph.sqlite"
    _write_canonical(canonical_path, payload)
    _write_sqlite(sqlite_path, payload)
    return canonical_path, sqlite_path, payload


def test_receipt_is_deterministic_and_does_not_mutate_inputs(tmp_path: Path) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    assert collect_canonical_graph_issues(_payload) == []
    before_names = sorted(path.name for path in tmp_path.iterdir())
    before_canonical = canonical_path.read_bytes()
    before_sqlite = sqlite_path.read_bytes()

    first = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    second = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )

    assert first == second
    assert first["control_plane_status"] == "PASS"
    assert first["graph_data_readiness"] == "PASS"
    assert first["overall_status"] == "PASS"
    sibling = _metric(first, "sibling_integrity")
    assert sibling["status"] == "PASS"
    assert sibling["numerator"] == 6
    assert sibling["denominator"] == 6
    assert sibling["failure_count"] == 0
    assert canonical_path.read_bytes() == before_canonical
    assert sqlite_path.read_bytes() == before_sqlite
    assert sorted(path.name for path in tmp_path.iterdir()) == before_names
    assert not list(tmp_path.glob("graph.sqlite-*"))


def test_operational_cohort_digest_is_recomputed_from_normalized_evidence(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    evidence = _operational_evidence()
    original_digest = evidence["cohort_digest"]
    evidence["decision_safe_regression"]["passed"] = 2

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=evidence,
    )

    metric = _metric(receipt, "decision_safe_regression")
    assert original_digest != compute_operational_cohort_digest(evidence)
    assert metric["status"] == "UNKNOWN"
    assert metric["unknown_reason"] == "operational_evidence_cohort_digest_mismatch"


def test_operational_cohort_digest_normalizes_failure_locator_order() -> None:
    evidence = _operational_evidence()
    evidence["p0_sla"]["failure_locators"] = [{"id": "b"}, {"id": "a"}]
    first = compute_operational_cohort_digest(evidence)
    evidence["p0_sla"]["failure_locators"].reverse()
    assert compute_operational_cohort_digest(evidence) == first


def test_missing_sqlite_blocks_without_creating_or_materializing_it(tmp_path: Path) -> None:
    payload = _canonical_payload()
    canonical_path = tmp_path / "canonical.json"
    sqlite_path = tmp_path / "missing.sqlite"
    _write_canonical(canonical_path, payload)

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
    )

    assert not sqlite_path.exists()
    assert receipt["control_plane_status"] == "BLOCKED"
    assert receipt["overall_status"] == "BLOCKED"
    assert _metric(receipt, "sqlite_artifact_available")["status"] == "BLOCK"
    assert _metric(receipt, "sqlite_foreign_key_integrity")["status"] == "UNKNOWN"
    assert _metric(receipt, "path_integrity")["status"] == "UNKNOWN"


def test_unavailable_authority_dimensions_are_unknown_never_pass(tmp_path: Path) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
    )

    for metric_id in (
        "decision_safe_regression",
        "source_currentness",
        "source_freshness",
        "hitl_approval_coverage",
        "write_audit_coverage",
        "p0_sla_compliance",
        "p1_sla_compliance",
    ):
        metric = _metric(receipt, metric_id)
        assert metric["status"] == "UNKNOWN"
        assert metric["rate"] is None
        assert metric["denominator"] is None
    assert receipt["control_plane_status"] == "UNKNOWN"
    assert receipt["overall_status"] == "UNKNOWN"

    unverified = _operational_evidence()
    unverified["authority_status"] = "UNVERIFIED"
    unverified_receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=unverified,
    )
    assert _metric(unverified_receipt, "decision_safe_regression")["status"] == "UNKNOWN"
    assert _metric(unverified_receipt, "hitl_approval_coverage")["status"] == "UNKNOWN"
    assert _metric(unverified_receipt, "write_audit_coverage")["status"] == "UNKNOWN"


def test_zero_denominator_is_unknown_not_pass(tmp_path: Path) -> None:
    canonical_path, sqlite_path, payload = _fixture_paths(tmp_path)
    payload["skill_rows"] = []
    payload["metadata"]["skill_row_count"] = 0
    _write_canonical(canonical_path, payload)
    sqlite_path.unlink()
    _write_sqlite(sqlite_path, payload)

    evidence = _operational_evidence()
    evidence["p0_sla"] = {"within_sla": 0, "total": 0}
    evidence["cohort_digest"] = compute_operational_cohort_digest(evidence)
    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=evidence,
    )

    metric = _metric(receipt, "claim_evidence_completeness")
    assert metric["numerator"] == 0
    assert metric["denominator"] == 0
    assert metric["rate"] is None
    assert metric["status"] == "UNKNOWN"
    assert _metric(receipt, "p0_sla_compliance")["status"] == "UNKNOWN"


def test_structural_defects_require_migration_and_digest_mismatch_blocks(tmp_path: Path) -> None:
    canonical_path, sqlite_path, payload = _fixture_paths(tmp_path)
    duplicate = dict(payload["graph_nodes"][-1])
    payload["graph_nodes"].append(duplicate)
    payload["graph_metadata"]["node_count"] = len(payload["graph_nodes"])
    _write_canonical(canonical_path, payload)
    sqlite_path.unlink()
    projection_payload = dict(payload)
    projection_payload["graph_nodes"] = payload["graph_nodes"][:-1]
    _write_sqlite(sqlite_path, projection_payload, ledger_hash=_canonical_digest(payload))

    migration_receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    assert _metric(migration_receipt, "duplicate_node_id_rate")["status"] == "MIGRATION_REQUIRED"
    assert migration_receipt["graph_data_readiness"] == "MIGRATION_REQUIRED"
    assert _metric(migration_receipt, "canonical_sqlite_digest_match")["status"] == "BLOCK"
    assert migration_receipt["overall_status"] == "BLOCKED"

    conn = sqlite3.connect(sqlite_path)
    conn.execute("UPDATE graph_metadata SET ledger_hash=?", ("0" * 64,))
    conn.commit()
    conn.close()
    blocked_receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    assert _metric(blocked_receipt, "canonical_sqlite_digest_match")["status"] == "BLOCK"
    assert blocked_receipt["control_plane_status"] == "BLOCKED"
    assert blocked_receipt["overall_status"] == "BLOCKED"


def test_projection_row_tampering_blocks_even_when_ledger_hash_is_unchanged(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    ledger_hash_before = conn.execute("SELECT ledger_hash FROM graph_metadata").fetchone()[0]
    conn.execute(
        "UPDATE graph_edges SET edge_type='tampered_edge_type' WHERE edge_id='edge_skill_fact_1'"
    )
    conn.commit()
    assert conn.execute("SELECT ledger_hash FROM graph_metadata").fetchone()[0] == ledger_hash_before
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )

    metric = _metric(receipt, "canonical_sqlite_digest_match")
    assert metric["status"] == "BLOCK"
    assert metric["failure_count"] == 1
    assert any(
        row.get("binding") == "canonical_projection_semantic_digest"
        for row in metric["sample_failure_locators"]
    )


def test_locking_aware_reader_observes_committed_wal_state(tmp_path: Path) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    writer = sqlite3.connect(sqlite_path)
    try:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute(
            "UPDATE graph_edges SET edge_type='tampered_in_wal' "
            "WHERE edge_id='edge_skill_fact_1'"
        )
        writer.commit()
        sidecars_before = sorted(path.name for path in tmp_path.glob(f"{sqlite_path.name}-*"))

        receipt = build_c03_graph_health_receipt(
            canonical_path=canonical_path,
            sqlite_path=sqlite_path,
            generated_at=GENERATED_AT,
            operational_evidence=_operational_evidence(),
        )

        assert _metric(receipt, "canonical_sqlite_digest_match")["status"] == "BLOCK"
        assert _metric(receipt, "sqlite_read_purity")["status"] == "PASS"
        assert receipt["digests"]["sqlite_sidecars_before"] == sidecars_before
        assert receipt["digests"]["sqlite_sidecars_after"] == sidecars_before
    finally:
        writer.close()


def test_reverse_view_parity_is_multiset_sensitive(tmp_path: Path) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.executescript(
        """
        DROP VIEW graph_edges_reverse;
        CREATE VIEW graph_edges_reverse AS
        SELECT edge_id,
               target_node_id AS source_node_id,
               source_node_id AS target_node_id,
               edge_type || '_reverse' AS edge_type
        FROM graph_edges
        UNION ALL
        SELECT edge_id,
               target_node_id AS source_node_id,
               source_node_id AS target_node_id,
               edge_type || '_reverse' AS edge_type
        FROM graph_edges
        WHERE edge_id = (SELECT MIN(edge_id) FROM graph_edges);
        """
    )
    conn.commit()
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    metric = _metric(receipt, "reverse_view_parity")
    assert metric["status"] == "MIGRATION_REQUIRED"
    assert metric["failure_count"] == 1
    assert metric["sample_failure_locators"][0]["observed_occurrences"] == 2


def test_required_empty_sibling_and_neighborhood_materializations_fail(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute("DELETE FROM graph_sibling_links")
    conn.execute("DELETE FROM graph_neighborhoods")
    conn.commit()
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    sibling = _metric(receipt, "sibling_integrity")
    neighborhood = _metric(receipt, "neighborhood_integrity")
    assert sibling["status"] == "FAIL"
    assert "unknown_reason" not in sibling
    assert sibling["failure_count"] > 0
    assert neighborhood["status"] == "FAIL"
    assert neighborhood["failure_count"] > 0
    assert receipt["graph_data_readiness"] == "NOT_READY"


def test_sibling_integrity_fails_when_a_reciprocal_pair_is_partially_truncated(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        """
        DELETE FROM graph_sibling_links
        WHERE (node_id = ? AND sibling_node_id = ?)
           OR (node_id = ? AND sibling_node_id = ?)
        """,
        ("skill_1", "skill_2", "skill_2", "skill_1"),
    )
    conn.commit()
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    sibling = _metric(receipt, "sibling_integrity")

    assert sibling["status"] == "FAIL"
    assert sibling["numerator"] == 4
    assert sibling["denominator"] == 6
    assert sibling["failure_count"] == 2
    assert sibling["sample_failure_locators"] == [
        {
            "node_id": "skill_1",
            "reasons": ["expected_sibling_missing"],
            "shared_edge_type": "capability_domain_contains_skill",
            "shared_parent_node_id": "domain_platform",
            "sibling_node_id": "skill_2",
        },
        {
            "node_id": "skill_2",
            "reasons": ["expected_sibling_missing"],
            "shared_edge_type": "capability_domain_contains_skill",
            "shared_parent_node_id": "domain_platform",
            "sibling_node_id": "skill_1",
        },
    ]


def test_sibling_integrity_rejects_unexpected_rows_with_expected_set_denominator(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        """
        INSERT INTO graph_sibling_links(
            node_id,sibling_node_id,shared_parent_node_id,shared_edge_type
        ) VALUES(?,?,?,?)
        """,
        (
            "skill_1",
            "epoch_recent",
            "domain_platform",
            "capability_domain_contains_skill",
        ),
    )
    conn.commit()
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    sibling = _metric(receipt, "sibling_integrity")

    assert sibling["status"] == "FAIL"
    assert sibling["numerator"] == 6
    assert sibling["denominator"] == 6
    assert sibling["rate"] == 1.0
    assert sibling["failure_count"] == 1
    assert sibling["sample_failure_locators"] == [
        {
            "node_id": "skill_1",
            "reasons": [
                "reciprocal_link_missing",
                "shared_parent_edges_missing",
                "unexpected_sibling_row",
            ],
            "shared_edge_type": "capability_domain_contains_skill",
            "shared_parent_node_id": "domain_platform",
            "sibling_node_id": "epoch_recent",
        }
    ]


def test_claim_evidence_requires_declared_fact_links_bound_by_graph_edges(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, payload = _fixture_paths(tmp_path)
    payload["graph_edges"] = [
        edge for edge in payload["graph_edges"] if edge["edge_id"] != "edge_skill_fact_1"
    ]
    payload["graph_metadata"]["edge_count"] = len(payload["graph_edges"])
    _write_canonical(canonical_path, payload)

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
    )
    metric = _metric(receipt, "claim_evidence_completeness")
    assert metric["status"] == "FAIL"
    assert metric["numerator"] == 2
    assert metric["denominator"] == 3
    failure = next(row for row in metric["sample_failure_locators"] if row["skill_id"] == "skill_1")
    assert failure["missing_graph_fact_bindings"] == ["fact_shared"]
    assert payload["skill_rows"][0]["source_snippets"]


def test_explicit_endpoint_closure_is_diagnostic_when_registered_derivations_are_required() -> None:
    policy = load_health_policy()
    assert policy["metrics"]["explicit_endpoint_closure"]["required"] is False
    assert policy["metrics"]["registered_endpoint_closure"]["required"] is True


def test_current_canonical_missing_source_refs_are_measured_not_filled() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    canonical_path = repo_root / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
    sqlite_path = repo_root / "artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite"
    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
    )
    metric = _metric(receipt, "graph_node_source_ref_completeness")
    skill_node_metric = _metric(receipt, "skill_row_node_coverage")

    assert metric["denominator"] - metric["numerator"] == 84
    assert metric["failure_count"] == 84
    assert metric["status"] != "PASS"
    assert (skill_node_metric["numerator"], skill_node_metric["denominator"]) == (250, 254)
    assert {row["skill_id"] for row in skill_node_metric["sample_failure_locators"]} == {
        "skill_cpq_deal_velocity_automation",
        "skill_meddpicc_sales_qualification",
        "skill_nps_customer_health_scoring",
        "skill_saas_arr_ltv_cac_metrics",
    }
    assert skill_node_metric["status"] == "FAIL"


def test_cli_prints_by_default_and_writes_only_for_explicit_output(
    tmp_path: Path,
    capsys: Any,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(_operational_evidence()), encoding="utf-8")
    output_path = tmp_path / "receipts/health.json"
    args = [
        "--canonical",
        str(canonical_path),
        "--sqlite",
        str(sqlite_path),
        "--operational-evidence",
        str(evidence_path),
        "--generated-at",
        GENERATED_AT,
    ]

    assert main(args) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["overall_status"] == "PASS"
    assert not output_path.exists()

    assert main([*args, "--output", str(output_path)]) == 0
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["overall_status"] == "PASS"
    assert json.loads(capsys.readouterr().out) == written
