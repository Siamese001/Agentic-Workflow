"""apps-test-model: APP CONTRACT."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from apps_rg.fact_inventory import c03_graph_kpi_health as health_module
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import canonical_node_type
from apps_rg.fact_inventory.c03_graph_kpi_health import (
    build_c03_graph_health_receipt,
    load_health_policy,
    main,
)
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    PRODUCER_REGISTRY_VERSION as OPERATIONAL_PRODUCER_REGISTRY_VERSION,
)
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    SCHEMA_VERSION as OPERATIONAL_EVIDENCE_SCHEMA_VERSION,
)
from apps_rg.fact_inventory.c03_graph_operational_evidence import (
    OperationalTrustContext,
    compute_envelope_integrity,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    compute_sqlite_graph_digest,
    compute_sqlite_schema_digest,
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
            node_type TEXT NOT NULL,
            label TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            activation_status TEXT NOT NULL DEFAULT '',
            support_level TEXT NOT NULL DEFAULT '',
            confidence TEXT NOT NULL DEFAULT '',
            external_eligible INTEGER NOT NULL DEFAULT 0,
            source_authority TEXT NOT NULL DEFAULT 'fixture',
            created_at TEXT NOT NULL DEFAULT '2026-07-18T16:00:00Z',
            updated_at TEXT NOT NULL DEFAULT '2026-07-18T16:00:00Z'
        );
        CREATE TABLE graph_edges (
            edge_id TEXT PRIMARY KEY,
            source_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            target_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            edge_family TEXT NOT NULL DEFAULT '',
            edge_type TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0,
            confidence TEXT NOT NULL DEFAULT '',
            directional INTEGER NOT NULL DEFAULT 1,
            evidence_status TEXT NOT NULL DEFAULT '',
            section_fit TEXT NOT NULL DEFAULT '',
            source_authority TEXT NOT NULL DEFAULT 'fixture',
            rationale TEXT NOT NULL DEFAULT '',
            projection_behavior TEXT NOT NULL DEFAULT '',
            external_claim_policy TEXT NOT NULL DEFAULT '',
            validation_status TEXT NOT NULL DEFAULT '',
            edge_note TEXT NOT NULL DEFAULT '',
            operator_note TEXT NOT NULL DEFAULT '',
            business_story TEXT NOT NULL DEFAULT '',
            technical_story TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE skill_fact_links (
            skill_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            fact_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            support_level TEXT NOT NULL DEFAULT '',
            claim_eligibility INTEGER NOT NULL DEFAULT 0,
            source_trace TEXT NOT NULL DEFAULT '',
            archive_trace TEXT NOT NULL DEFAULT '',
            human_confirmed INTEGER NOT NULL DEFAULT 0,
            external_eligible INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (skill_id, fact_id)
        );
        CREATE TABLE section_eligibility (
            node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            section_id TEXT NOT NULL,
            allowed INTEGER NOT NULL DEFAULT 0,
            claim_policy TEXT NOT NULL DEFAULT '',
            reason TEXT NOT NULL DEFAULT '',
            blocked_reason TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (node_id, section_id)
        );
        CREATE TABLE role_family_projection (
            role_family_id TEXT PRIMARY KEY,
            projection_role_family_key TEXT NOT NULL,
            track_weight_profile TEXT NOT NULL DEFAULT '{}',
            taxonomy_source TEXT NOT NULL DEFAULT '',
            targeting_keywords TEXT NOT NULL DEFAULT '[]',
            proof_policy_note TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE c03_skill_selection_features (
            skill_id TEXT PRIMARY KEY REFERENCES graph_nodes(node_id),
            pillar TEXT NOT NULL DEFAULT '',
            subpillar TEXT NOT NULL DEFAULT '',
            domain_id TEXT NOT NULL DEFAULT '',
            career_track_id TEXT NOT NULL DEFAULT '',
            skill_family TEXT NOT NULL DEFAULT '',
            metric_bucket TEXT NOT NULL,
            role_family_weights TEXT NOT NULL DEFAULT '{}',
            allowed_sections TEXT NOT NULL DEFAULT '[]',
            source_fact_count INTEGER NOT NULL DEFAULT 0,
            confidence TEXT NOT NULL DEFAULT '',
            activation_status TEXT NOT NULL DEFAULT '',
            support_level TEXT NOT NULL DEFAULT '',
            external_eligible INTEGER NOT NULL DEFAULT 0,
            source_authority TEXT NOT NULL DEFAULT 'fixture',
            source_trace TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT '2026-07-18T16:00:00Z'
        );
        CREATE TABLE c03_role_family_skill_weights (
            skill_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            role_family_key TEXT NOT NULL,
            weight REAL NOT NULL,
            source TEXT NOT NULL DEFAULT 'fixture',
            PRIMARY KEY (skill_id, role_family_key)
        );
        CREATE TABLE graph_paths (
            path_id TEXT PRIMARY KEY,
            start_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            end_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            path_depth INTEGER NOT NULL,
            path_signature TEXT NOT NULL DEFAULT '',
            node_path_json TEXT NOT NULL,
            edge_path_json TEXT NOT NULL,
            edge_types_json TEXT NOT NULL,
            proof_fact_ids_json TEXT NOT NULL DEFAULT '[]',
            metric_ids_json TEXT NOT NULL DEFAULT '[]',
            section_ids_json TEXT NOT NULL DEFAULT '[]',
            path_score REAL NOT NULL DEFAULT 0.0,
            novelty_score REAL NOT NULL DEFAULT 0.0,
            proof_strength_score REAL NOT NULL DEFAULT 0.0,
            created_at TEXT NOT NULL DEFAULT '2026-07-18T16:00:00Z'
        );
        CREATE TABLE graph_sibling_links (
            node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            sibling_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            sibling_reason TEXT NOT NULL DEFAULT '',
            shared_parent_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            shared_edge_type TEXT NOT NULL,
            sibling_score REAL NOT NULL DEFAULT 0.0,
            PRIMARY KEY (
                node_id,sibling_node_id,shared_parent_node_id,shared_edge_type
            )
        );
        CREATE TABLE graph_neighborhoods (
            center_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            neighbor_node_id TEXT NOT NULL REFERENCES graph_nodes(node_id),
            distance INTEGER NOT NULL,
            connecting_path_json TEXT NOT NULL,
            edge_types_json TEXT NOT NULL,
            relationship_summary TEXT NOT NULL DEFAULT '',
            neighbor_score REAL NOT NULL DEFAULT 0.0,
            PRIMARY KEY (center_node_id, neighbor_node_id, distance)
        );
        CREATE TABLE section_evidence_budget (
            section_id TEXT NOT NULL,
            role_family_key TEXT NOT NULL,
            max_metric_reuse INTEGER NOT NULL DEFAULT 1,
            max_fact_family_reuse INTEGER NOT NULL DEFAULT 2,
            required_node_types_json TEXT NOT NULL DEFAULT '[]',
            preferred_edge_types_json TEXT NOT NULL DEFAULT '[]',
            forbidden_metric_ids_json TEXT NOT NULL DEFAULT '[]',
            preferred_metric_families_json TEXT NOT NULL DEFAULT '[]',
            PRIMARY KEY (section_id, role_family_key)
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
               edge_type || '_reverse' AS edge_type,
               edge_family,
               weight,
               confidence,
               evidence_status,
               section_fit,
               source_authority,
               rationale,
               projection_behavior,
               external_claim_policy,
               validation_status,
               edge_note,
               operator_note,
               business_story,
               technical_story
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
    summary["sqlite_graph_digest"] = compute_sqlite_graph_digest(conn)
    summary["sqlite_schema_digest"] = compute_sqlite_schema_digest(conn)
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
    return {
        "schema_version": "apps_rg.c03_graph_health_operational_evidence.v1",
        "authority_status": "VERIFIED",
        "cohort_id": "fixture-frozen-cohort",
        "cohort_digest": "d" * 64,
        "decision_safe_regression": {"passed": 3, "total": 3},
        "source_currentness": {"current": 3, "total": 3},
        "source_freshness": {"fresh": 3, "total": 3},
        "hitl_approval": {"approved": 3, "total": 3},
        "write_audit": {"audited": 3, "total": 3},
        "p0_sla": {"within_sla": 2, "total": 2},
        "p1_sla": {"within_sla": 2, "total": 2},
    }


def _untrusted_v2_operational_evidence() -> dict[str, Any]:
    return _v2_operational_evidence(
        candidate_commit_sha="a" * 40,
        canonical_graph_sha256="b" * 64,
        health_policy_sha256="c" * 64,
        health_run_id="fixture-health-run",
    )


def _v2_operational_evidence(
    *,
    candidate_commit_sha: str,
    canonical_graph_sha256: str,
    health_policy_sha256: str,
    health_run_id: str,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "schema_version": OPERATIONAL_EVIDENCE_SCHEMA_VERSION,
        "envelope_id": "fixture-operational-envelope",
        "producer_registry_version": "apps_rg.c03_graph_operational_producer_registry.v1",
        "assembled_at_utc": GENERATED_AT,
        "subject": {
            "candidate_commit_sha": candidate_commit_sha,
            "canonical_graph_sha256": canonical_graph_sha256,
            "health_policy_sha256": health_policy_sha256,
            "health_run_id": health_run_id,
        },
        "bindings": {},
    }
    evidence["integrity_sha256"] = compute_envelope_integrity(evidence)
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
    assert first["control_plane_status"] == "UNKNOWN"
    assert first["graph_data_readiness"] == "PASS"
    assert first["overall_status"] == "UNKNOWN"
    assert len(first["metrics"]) == 39
    assert first["status_counts"] == {"PASS": 32, "UNKNOWN": 7}
    canonical_signatures = _metric(
        first,
        "canonical_projected_edge_signature_integrity",
    )
    sqlite_signatures = _metric(
        first,
        "sqlite_projected_edge_signature_integrity",
    )
    assert (
        canonical_signatures["status"],
        canonical_signatures["numerator"],
        canonical_signatures["denominator"],
    ) == ("PASS", 6, 6)
    assert (
        sqlite_signatures["status"],
        sqlite_signatures["numerator"],
        sqlite_signatures["denominator"],
    ) == ("PASS", 6, 6)
    sibling = _metric(first, "sibling_integrity")
    assert sibling["status"] == "PASS"
    assert sibling["numerator"] == 6
    assert sibling["denominator"] == 6
    assert sibling["failure_count"] == 0
    assert canonical_path.read_bytes() == before_canonical
    assert sqlite_path.read_bytes() == before_sqlite
    assert sorted(path.name for path in tmp_path.iterdir()) == before_names
    assert not list(tmp_path.glob("graph.sqlite-*"))


def test_legacy_self_attested_operational_evidence_is_rejected(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    evidence = _operational_evidence()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=evidence,
    )

    metric = _metric(receipt, "decision_safe_regression")
    assert metric["status"] == "UNKNOWN"
    assert metric["unknown_reason"] == "legacy_or_unsupported_operational_evidence_schema"


def test_v2_operational_evidence_without_out_of_band_trust_is_unknown(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_untrusted_v2_operational_evidence(),
    )

    metric = _metric(receipt, "decision_safe_regression")
    assert metric["status"] == "UNKNOWN"
    assert metric["unknown_reason"] == "operational_trust_context_not_supplied"


def test_v2_envelope_is_verified_only_after_binding_to_actual_health_inputs(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, payload = _fixture_paths(tmp_path)
    candidate_commit_sha = "a" * 40
    health_run_id = "fixture-health-run"
    canonical_graph_sha256 = _canonical_digest(payload)
    health_policy_sha256 = _canonical_digest(load_health_policy())
    evidence = _v2_operational_evidence(
        candidate_commit_sha=candidate_commit_sha,
        canonical_graph_sha256=canonical_graph_sha256,
        health_policy_sha256=health_policy_sha256,
        health_run_id=health_run_id,
    )
    trust_context = OperationalTrustContext(
        artifact_roots={},
        authority_anchors={},
        expected_candidate_commit_sha=candidate_commit_sha,
        expected_canonical_graph_sha256=canonical_graph_sha256,
        expected_health_policy_sha256=health_policy_sha256,
        expected_health_run_id=health_run_id,
        observed_at_utc=datetime(2026, 7, 18, 17, 0, tzinfo=timezone.utc),
    )

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=evidence,
        operational_trust_context=trust_context,
        candidate_commit_sha=candidate_commit_sha,
        run_id=health_run_id,
    )

    metric = _metric(receipt, "decision_safe_regression")
    assert metric["status"] == "UNKNOWN"
    assert metric["unknown_reason"] == "binding_missing"
    assert metric["details"]["envelope_schema_valid"] is True
    assert metric["details"]["envelope_integrity_valid"] is True
    assert metric["details"]["envelope_subject_valid"] is True
    assert receipt["versions"]["operational_trust_context_supplied"] is True


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

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
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
    conn.execute("UPDATE graph_edges SET edge_type='tampered_edge_type' WHERE edge_id='edge_skill_fact_1'")
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
    assert metric["failure_count"] == 2
    assert any(
        row.get("binding") == "canonical_projection_semantic_digest"
        for row in metric["sample_failure_locators"]
    )
    assert any(
        row.get("binding") == "sqlite_projection_logical_digest" for row in metric["sample_failure_locators"]
    )


def test_canonical_signature_metric_reports_exact_wrong_endpoint_types(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, payload = _fixture_paths(tmp_path)
    next(row for row in payload["graph_nodes"] if row["node_id"] == "skill_1")["node_type"] = "metric"
    _write_canonical(canonical_path, payload)

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )

    metric = _metric(receipt, "canonical_projected_edge_signature_integrity")
    assert metric["status"] == "MIGRATION_REQUIRED"
    assert metric["numerator"] == 4
    assert metric["denominator"] == 6
    assert metric["failure_count"] == 2
    assert {
        (
            row["edge_id"],
            row["edge_type"],
            row["source_type"],
            row["target_type"],
        )
        for row in metric["sample_failure_locators"]
    } == {
        ("edge_domain_skill_1", "capability_domain_contains_skill", "capability_domain", "metric"),
        ("edge_skill_fact_1", "skill_supported_by_fact", "metric", "fact"),
    }


def test_sqlite_signature_metric_reports_exact_wrong_endpoint_types(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute("UPDATE graph_nodes SET node_type='metric' WHERE node_id='skill_1'")
    conn.commit()
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )

    metric = _metric(receipt, "sqlite_projected_edge_signature_integrity")
    assert metric["status"] == "MIGRATION_REQUIRED"
    assert metric["numerator"] == 4
    assert metric["denominator"] == 6
    assert metric["failure_count"] == 2
    assert {
        (
            row["edge_id"],
            row["edge_type"],
            row["source_type"],
            row["target_type"],
        )
        for row in metric["sample_failure_locators"]
    } == {
        ("edge_domain_skill_1", "capability_domain_contains_skill", "capability_domain", "metric"),
        ("edge_skill_fact_1", "skill_supported_by_fact", "metric", "fact"),
    }


@pytest.mark.parametrize(
    ("canonical_raw_type", "wrong_projected_type"),
    (("metric", "metric_bucket"), ("metric_bucket", "metric_outcome")),
)
def test_semantic_digest_distinguishes_metric_type_family_members(
    tmp_path: Path,
    canonical_raw_type: str,
    wrong_projected_type: str,
) -> None:
    payload = _canonical_payload()
    payload["graph_nodes"].append(
        {
            "node_id": "semantic_metric_node",
            "node_type": canonical_raw_type,
            "label": "Semantic metric node",
            "source_refs": ["source://metric/semantic"],
            "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
            "visibility_rule": "role_family_match",
            "external_claim_policy": "derived_supported_with_fact",
        }
    )
    payload["graph_metadata"]["node_count"] = len(payload["graph_nodes"])
    canonical_path = tmp_path / "canonical.json"
    sqlite_path = tmp_path / "graph.sqlite"
    _write_canonical(canonical_path, payload)
    _write_sqlite(sqlite_path, payload)

    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        "UPDATE graph_nodes SET node_type=? WHERE node_id='semantic_metric_node'",
        (wrong_projected_type,),
    )
    raw_summary = conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0]
    summary = json.loads(raw_summary)
    summary["sqlite_graph_digest"] = compute_sqlite_graph_digest(conn)
    conn.execute(
        "UPDATE graph_metadata SET graph_count_summary=?",
        (json.dumps(summary, sort_keys=True),),
    )
    conn.commit()
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
    assert metric["sample_failure_locators"][0]["binding"] == ("canonical_projection_semantic_digest")
    assert (
        receipt["digests"]["canonical_graph_semantic_sha256"]
        != receipt["digests"]["sqlite_projection_canonical_semantic_sha256"]
    )


def test_same_count_authority_tampering_blocks_on_full_projection_digest(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        "UPDATE skill_fact_links SET claim_eligibility=1 WHERE skill_id='skill_1' AND fact_id='fact_shared'"
    )
    conn.commit()
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
    assert metric["sample_failure_locators"][0]["binding"] == ("sqlite_projection_logical_digest")
    assert (
        receipt["digests"]["canonical_graph_semantic_sha256"]
        == receipt["digests"]["sqlite_projection_canonical_semantic_sha256"]
    )
    assert (
        receipt["digests"]["sqlite_projection_logical_stored_sha256"]
        != receipt["digests"]["sqlite_projection_logical_recomputed_sha256"]
    )


def test_ranking_table_tampering_is_bound_by_full_projection_digest(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        "UPDATE section_eligibility SET reason='tampered-ranking-policy' "
        "WHERE node_id='skill_1' AND section_id='competencies'"
    )
    conn.commit()
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
    assert metric["sample_failure_locators"][0]["binding"] == ("sqlite_projection_logical_digest")


def test_same_column_view_definition_drift_is_bound_by_schema_digest(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    original_sql = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='view' AND name='graph_edges_reverse'"
    ).fetchone()[0]
    original_columns = tuple(row[1] for row in conn.execute("PRAGMA table_info(graph_edges_reverse)"))
    conn.execute("DROP VIEW graph_edges_reverse")
    conn.execute(f"{original_sql} WHERE 1 = 1")
    drifted_columns = tuple(row[1] for row in conn.execute("PRAGMA table_info(graph_edges_reverse)"))
    assert drifted_columns == original_columns
    conn.commit()
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
    assert metric["sample_failure_locators"][0]["binding"] == ("sqlite_projection_schema_digest")
    assert (
        receipt["digests"]["sqlite_projection_schema_stored_sha256"]
        != receipt["digests"]["sqlite_projection_schema_recomputed_sha256"]
    )


def test_locking_aware_reader_observes_committed_wal_state(tmp_path: Path) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    writer = sqlite3.connect(sqlite_path)
    try:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("UPDATE graph_edges SET edge_type='tampered_in_wal' WHERE edge_id='edge_skill_fact_1'")
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


def test_health_metrics_remain_bound_to_one_wal_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    writer = sqlite3.connect(sqlite_path)
    try:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        writer.execute("PRAGMA wal_autocheckpoint=0")
        real_digest = health_module.compute_sqlite_graph_digest
        committed = False

        def _commit_after_snapshot(conn: sqlite3.Connection) -> str:
            nonlocal committed
            if not committed:
                writer.execute(
                    "UPDATE graph_nodes SET label='committed-after-health-snapshot' WHERE node_id='skill_1'"
                )
                writer.commit()
                committed = True
            return real_digest(conn)

        monkeypatch.setattr(
            health_module,
            "compute_sqlite_graph_digest",
            _commit_after_snapshot,
        )

        receipt = build_c03_graph_health_receipt(
            canonical_path=canonical_path,
            sqlite_path=sqlite_path,
            generated_at=GENERATED_AT,
        )

        assert committed is True
        assert _metric(receipt, "canonical_sqlite_digest_match")["status"] == "PASS"
        assert (
            writer.execute("SELECT label FROM graph_nodes WHERE node_id='skill_1'").fetchone()[0]
            == "committed-after-health-snapshot"
        )
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


def test_path_integrity_fails_when_one_required_direct_path_is_truncated(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute("DELETE FROM graph_paths WHERE path_id='path_edge_domain_skill_1'")
    conn.commit()
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    metric = _metric(receipt, "path_integrity")

    assert metric["status"] == "MIGRATION_REQUIRED"
    assert (metric["numerator"], metric["denominator"]) == (5, 6)
    assert metric["failure_count"] == 1
    assert metric["sample_failure_locators"][0]["reasons"] == ["expected_direct_path_missing"]


def test_neighborhood_integrity_fails_when_one_required_direct_row_is_truncated(
    tmp_path: Path,
) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        "DELETE FROM graph_neighborhoods "
        "WHERE center_node_id='domain_platform' AND neighbor_node_id='skill_1' "
        "AND distance=1"
    )
    conn.commit()
    conn.close()

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        generated_at=GENERATED_AT,
        operational_evidence=_operational_evidence(),
    )
    metric = _metric(receipt, "neighborhood_integrity")

    assert metric["status"] == "FAIL"
    assert (metric["numerator"], metric["denominator"]) == (11, 12)
    assert metric["failure_count"] == 1
    assert metric["sample_failure_locators"][0]["reasons"] == ["expected_direct_neighborhood_missing"]


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


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("operational_evidence_schema_version", OPERATIONAL_EVIDENCE_SCHEMA_VERSION),
        ("operational_producer_registry_version", OPERATIONAL_PRODUCER_REGISTRY_VERSION),
    ],
)
def test_health_policy_rejects_operational_contract_drift(
    tmp_path: Path,
    field: str,
    expected: str,
) -> None:
    policy = load_health_policy()
    assert policy[field] == expected
    policy[field] = f"{expected}.stale"
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    with pytest.raises(ValueError, match="operational"):
        load_health_policy(policy_path)


def _write_policy(tmp_path: Path, policy: dict[str, Any]) -> Path:
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    return policy_path


def test_health_policy_rejects_policy_version_drift(tmp_path: Path) -> None:
    policy = load_health_policy()
    policy["policy_version"] = f"{policy['policy_version']}.stale"

    with pytest.raises(ValueError, match="policy version"):
        load_health_policy(_write_policy(tmp_path, policy))


@pytest.mark.parametrize("registry_drift", ["missing", "extra"])
def test_health_policy_rejects_exact_metric_registry_drift(
    tmp_path: Path,
    registry_drift: str,
) -> None:
    policy = load_health_policy()
    if registry_drift == "missing":
        policy["metrics"].pop("path_integrity")
    else:
        policy["metrics"]["unregistered_metric"] = dict(policy["metrics"]["path_integrity"])

    with pytest.raises(ValueError, match="metric registry drift"):
        load_health_policy(_write_policy(tmp_path, policy))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("plane", "other_plane", "plane"),
        ("operator", ">", "operator"),
        ("target", float("nan"), "target"),
        ("failure_status", "PASS", "failure_status"),
        ("required", 1, "required"),
    ],
    ids=("plane", "operator", "nonfinite-target", "failure-status", "required-type"),
)
def test_health_policy_rejects_malformed_metric_specs(
    tmp_path: Path,
    field: str,
    value: Any,
    message: str,
) -> None:
    policy = load_health_policy()
    policy["metrics"]["path_integrity"][field] = value

    with pytest.raises(ValueError, match=message):
        load_health_policy(_write_policy(tmp_path, policy))


def test_health_policy_rejects_ignored_metric_spec_fields(tmp_path: Path) -> None:
    policy = load_health_policy()
    policy["metrics"]["path_integrity"]["ignored_override"] = True

    with pytest.raises(ValueError, match="fields drift"):
        load_health_policy(_write_policy(tmp_path, policy))


def test_noncanonical_operational_evidence_fails_closed(tmp_path: Path) -> None:
    canonical_path, sqlite_path, _payload = _fixture_paths(tmp_path)
    cyclic_evidence: dict[str, Any] = {}
    cyclic_evidence["self"] = cyclic_evidence

    receipt = build_c03_graph_health_receipt(
        canonical_path=canonical_path,
        sqlite_path=sqlite_path,
        operational_evidence=cyclic_evidence,
        generated_at=GENERATED_AT,
    )

    operational_metrics = [
        _metric(receipt, metric_id)
        for metric_id in (
            "decision_safe_regression",
            "source_currentness",
            "source_freshness",
            "hitl_approval_coverage",
            "write_audit_coverage",
            "p0_sla_compliance",
            "p1_sla_compliance",
        )
    ]
    assert {row["status"] for row in operational_metrics} == {"UNKNOWN"}
    assert {row["unknown_reason"] for row in operational_metrics} == {
        "operational_evidence_not_canonical_json"
    }
    assert receipt["digests"]["operational_evidence_sha256"] is None


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

    assert main(args) == 2
    printed = json.loads(capsys.readouterr().out)
    assert printed["overall_status"] == "UNKNOWN"
    assert _metric(printed, "decision_safe_regression")["unknown_reason"] == (
        "legacy_or_unsupported_operational_evidence_schema"
    )
    assert not output_path.exists()

    assert main([*args, "--output", str(output_path)]) == 2
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["overall_status"] == "UNKNOWN"
    assert json.loads(capsys.readouterr().out) == written
