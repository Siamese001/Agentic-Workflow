from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_rg.evals.c03_graph_embedding_qualification import (
    QUALIFICATION_THRESHOLDS,
    evaluate_graph_embedding_qualification,
    freeze_query_qrels,
    reciprocal_rank_fusion,
)
from apps_rg.fact_inventory.c03_skill_assertion_corpus import canonical_sha256


def _authority() -> tuple[dict, dict]:
    graph_rows = [
        {
            "skill_id": "skill_a",
            "retrieval_eligible": True,
            "fact_id_links": ["fact_a"],
            "allowed_sections": ["competencies"],
        },
        {
            "skill_id": "skill_b",
            "retrieval_eligible": True,
            "fact_id_links": ["fact_b"],
            "allowed_sections": ["competencies"],
        },
    ]
    graph = {"skill_rows": graph_rows}
    assertions = []
    for row in graph_rows:
        assertion = {
            "assertion_id": row["skill_id"],
            "skill_id": row["skill_id"],
            "embedding_text": row["skill_id"].replace("_", " "),
            "semantic_card": {"evidence_summaries": [row["fact_id_links"][0]]},
            "fact_links": row["fact_id_links"],
            "source_lineage": [
                {"source_id": row["fact_id_links"][0], "sha256": "a" * 64}
            ],
            "lifecycle": "ACTIVE",
            "allowed_sections": row["allowed_sections"],
            "authority_envelope_sha256": "b" * 64,
            "skill_row_sha256": canonical_sha256(row),
        }
        unsigned = dict(assertion)
        assertion["assertion_document_sha256"] = canonical_sha256(unsigned)
        assertions.append(assertion)
    corpus = {
        "source_digests": {"graph_sha256": canonical_sha256(graph)},
        "assertions": assertions,
        "exclusions": [],
    }
    corpus["corpus_sha256"] = canonical_sha256(corpus)
    return graph, corpus


def test_query_qrel_freeze_binds_exact_fixture_bytes(tmp_path: Path) -> None:
    jd = tmp_path / "role_jd.txt"
    brief = tmp_path / "role_brief.txt"
    jd.write_bytes(b"Role JD\r\nexact bytes")
    brief.write_bytes(b"Operator brief\n")
    fixture = {
        "schema_version": "1",
        "archetypes": [
            {
                "slug": "role",
                "label": "Role",
                "jd_path": jd.name,
                "brief_path": brief.name,
                "expected_role_family_ids": ["ROLE"],
                "expected_pillar_ids": ["pillar_role"],
                "weight_override": {"track_data": 1.0},
                "expected_skill_ids": ["skill_a"],
                "excluded_skill_ids": ["skill_b"],
                "priority_sections_w14": ["competencies"],
            }
        ],
    }
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(fixture), encoding="utf-8")

    frozen = freeze_query_qrels(manifest, repository_root=tmp_path)

    query = frozen["queries"][0]
    assert query["jd"]["sha256"] == hashlib.sha256(jd.read_bytes()).hexdigest()
    assert query["brief"]["sha256"] == hashlib.sha256(brief.read_bytes()).hexdigest()
    assert query["query_text"] == "Role JD\nexact bytes\nOperator brief\n"
    unsigned = dict(frozen)
    assert unsigned.pop("query_qrel_sha256") == canonical_sha256(unsigned)


def test_reciprocal_rank_fusion_is_deterministic() -> None:
    fused = reciprocal_rank_fusion(
        [["skill_b", "skill_a"], ["skill_a", "skill_b"]],
        assertion_ids={"skill_a", "skill_b"},
        rank_constant=60,
    )

    assert fused == ["skill_a", "skill_b"]


def test_qualification_requires_exact_authority_and_vector_parity() -> None:
    graph, corpus = _authority()
    query_qrels = {
        "queries": [
            {
                "query_id": "role",
                "query_text": "skill a",
                "relevant_assertion_ids": ["skill_a"],
                "excluded_assertion_ids": [],
            }
        ]
    }
    query_qrels["query_qrel_sha256"] = canonical_sha256(query_qrels)
    dense = {
        "role": [
            {"assertion_id": "skill_a", "similarity": 1.0},
            {"assertion_id": "skill_b", "similarity": 0.0},
        ]
    }
    thresholds = dict(QUALIFICATION_THRESHOLDS)
    thresholds.update(
        {
            "retrieval_k": 2,
            "exact_macro_recall_at_k_min": 1.0,
            "exact_micro_recall_at_k_min": 1.0,
            "fact_vector_macro_recall_at_k_min": 0.0,
            "fact_vector_micro_recall_at_k_min": 0.0,
            "dense_macro_recall_at_k_min": 1.0,
            "dense_micro_recall_at_k_min": 1.0,
            "hybrid_macro_recall_at_k_min": 1.0,
            "hybrid_micro_recall_at_k_min": 1.0,
        }
    )

    report = evaluate_graph_embedding_qualification(
        graph_payload=graph,
        corpus=corpus,
        query_qrels=query_qrels,
        dense_rankings=dense,
        thresholds=thresholds,
        projection_issues=[],
    )

    assert report["status"] == "PASS"
    assert report["structural_metrics"] == {
        "authority_eligibility_accuracy": 1.0,
        "exact_path_accuracy": 1.0,
        "assertion_vector_parity": 1.0,
        "stale_candidate_count": 0,
        "orphan_candidate_count": 0,
        "unauthorized_candidate_count": 0,
        "authority_bypass_count": 0,
    }

    dense["role"].append({"assertion_id": "orphan", "similarity": -1.0})
    blocked = evaluate_graph_embedding_qualification(
        graph_payload=graph,
        corpus=corpus,
        query_qrels=query_qrels,
        dense_rankings=dense,
        thresholds=thresholds,
        projection_issues=[],
    )
    assert blocked["status"] == "FAIL"
    assert blocked["structural_metrics"]["orphan_candidate_count"] == 1
