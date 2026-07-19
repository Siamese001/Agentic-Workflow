from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from apps_rg.runtime.graph_skill_embedding_projection import (
    GraphSkillEmbeddingContractError,
    GraphSkillEmbeddingIndex,
    build_embedding_projection,
    rehydrate_assertion_candidates,
    validate_embedding_projection,
)


def _assertion(assertion_id: str, section: str) -> dict:
    row = {
        "schema_version": "apps_rg.c03_skill_assertion.v1",
        "assertion_id": assertion_id,
        "skill_id": assertion_id,
        "semantic_card": {"label": assertion_id, "allowed_phrases": [assertion_id]},
        "embedding_text": assertion_id,
        "fact_links": [f"fact_{assertion_id}"],
        "source_lineage": [{"source_id": f"fact_{assertion_id}", "sha256": "a" * 64}],
        "lifecycle": "ACTIVE_CONFIRMED",
        "allowed_sections": [section],
        "authority_envelope_sha256": hashlib.sha256(assertion_id.encode()).hexdigest(),
        "skill_row_sha256": hashlib.sha256(f"row:{assertion_id}".encode()).hexdigest(),
    }
    unsigned = dict(row)
    row["assertion_document_sha256"] = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return row


def _corpus() -> dict:
    assertions = [_assertion("skill_a", "headline"), _assertion("skill_b", "competencies")]
    payload = {
        "schema_version": "apps_rg.c03_skill_assertion_corpus.v1",
        "source_digests": {"graph_sha256": "1" * 64},
        "counts": {
            "canonical_skill_count": 2,
            "eligible_assertion_count": 2,
            "non_retrieval_eligible_count": 0,
        },
        "assertions": assertions,
        "exclusions": [],
    }
    payload["corpus_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def _model_manifest() -> dict:
    return {
        "model_id": "BAAI/bge-m3",
        "revision": "test-revision",
        "artifact_sha256": "2" * 64,
        "dimension": 3,
        "normalization": "l2",
    }


def test_projection_is_byte_deterministic_and_vector_complete(tmp_path: Path) -> None:
    corpus = _corpus()
    vectors = {"skill_a": [1.0, 0.0, 0.0], "skill_b": [0.0, 1.0, 0.0]}
    first = tmp_path / "first.sqlite"
    second = tmp_path / "second.sqlite"

    one = build_embedding_projection(first, corpus, vectors, _model_manifest())
    two = build_embedding_projection(second, corpus, vectors, _model_manifest())

    assert first.read_bytes() == second.read_bytes()
    assert one == two
    assert one["vector_count"] == 2
    assert validate_embedding_projection(first, corpus=corpus) == []


def test_query_returns_only_assertion_ids_and_similarity_without_writes(tmp_path: Path) -> None:
    corpus = _corpus()
    path = tmp_path / "projection.sqlite"
    build_embedding_projection(
        path,
        corpus,
        {"skill_a": [1.0, 0.0, 0.0], "skill_b": [0.0, 1.0, 0.0]},
        _model_manifest(),
    )
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    with GraphSkillEmbeddingIndex(path, expected_corpus_sha256=corpus["corpus_sha256"]) as index:
        result = index.query([1.0, 0.0, 0.0], k=5, section_id="headline")

    assert result == [{"assertion_id": "skill_a", "similarity": 1.0}]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_projection_rejects_missing_nonfinite_or_unnormalized_vectors(tmp_path: Path) -> None:
    corpus = _corpus()
    with pytest.raises(GraphSkillEmbeddingContractError, match="parity"):
        build_embedding_projection(
            tmp_path / "missing.sqlite",
            corpus,
            {"skill_a": [1.0, 0.0, 0.0]},
            _model_manifest(),
        )
    with pytest.raises(GraphSkillEmbeddingContractError, match="finite"):
        build_embedding_projection(
            tmp_path / "nan.sqlite",
            corpus,
            {"skill_a": [math.nan, 0.0, 0.0], "skill_b": [0.0, 1.0, 0.0]},
            _model_manifest(),
        )
    with pytest.raises(GraphSkillEmbeddingContractError, match="normalized"):
        build_embedding_projection(
            tmp_path / "norm.sqlite",
            corpus,
            {"skill_a": [2.0, 0.0, 0.0], "skill_b": [0.0, 1.0, 0.0]},
            _model_manifest(),
        )


def test_rehydration_fails_closed_on_stale_or_unauthorized_assertion() -> None:
    corpus = _corpus()
    graph = {
        "skill_rows": [
            {
                "skill_id": "skill_a",
                "retrieval_eligible": True,
                "fact_id_links": ["fact_skill_a"],
                "allowed_sections": ["headline"],
            }
        ]
    }
    graph["skill_rows"][0]["_assertion_skill_row_sha256"] = corpus["assertions"][0][
        "skill_row_sha256"
    ]

    hydrated = rehydrate_assertion_candidates(
        [{"assertion_id": "skill_a", "similarity": 1.0}],
        corpus=corpus,
        graph_payload=graph,
        section_id="headline",
    )
    assert hydrated[0]["assertion_id"] == "skill_a"

    with pytest.raises(GraphSkillEmbeddingContractError, match="section"):
        rehydrate_assertion_candidates(
            [{"assertion_id": "skill_a", "similarity": 1.0}],
            corpus=corpus,
            graph_payload=graph,
            section_id="competencies",
        )
    with pytest.raises(GraphSkillEmbeddingContractError, match="orphan"):
        rehydrate_assertion_candidates(
            [{"assertion_id": "skill_b", "similarity": 0.5}],
            corpus=corpus,
            graph_payload=graph,
            section_id="competencies",
        )

