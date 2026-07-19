"""Deterministic qualification for the C0.3 graph-skill embedding projection."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.c03_skill_assertion_corpus import canonical_sha256

QUERY_QREL_SCHEMA_VERSION = "apps_rg.c03_graph_embedding_query_qrels.v1"
QUALIFICATION_SCHEMA_VERSION = "apps_rg.c03_graph_embedding_qualification.v1"

QUALIFICATION_THRESHOLDS: dict[str, float | int] = {
    "retrieval_k": 100,
    "rrf_rank_constant": 60,
    "exact_macro_recall_at_k_min": 0.75,
    "exact_micro_recall_at_k_min": 0.75,
    "fact_vector_macro_recall_at_k_min": 0.65,
    "fact_vector_micro_recall_at_k_min": 0.65,
    "dense_macro_recall_at_k_min": 0.85,
    "dense_micro_recall_at_k_min": 0.90,
    "hybrid_macro_recall_at_k_min": 0.90,
    "hybrid_micro_recall_at_k_min": 0.90,
    "authority_eligibility_accuracy_min": 1.0,
    "exact_path_accuracy_min": 1.0,
    "assertion_vector_parity_min": 1.0,
    "stale_candidate_count_max": 0,
    "orphan_candidate_count_max": 0,
    "unauthorized_candidate_count_max": 0,
    "authority_bypass_count_max": 0,
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class GraphEmbeddingQualificationError(RuntimeError):
    """Raised when qualification inputs cannot be bound exactly."""


def _file_binding(path: Path, *, repository_root: Path) -> tuple[dict[str, Any], bytes]:
    resolved = path if path.is_absolute() else repository_root / path
    data = resolved.read_bytes()
    try:
        relative = resolved.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as exc:
        raise GraphEmbeddingQualificationError(
            f"fixture path escapes repository root: {resolved}"
        ) from exc
    return (
        {
            "path": relative,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        },
        data,
    )


def _normalized_utf8(data: bytes, *, label: str) -> str:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GraphEmbeddingQualificationError(f"{label} is not UTF-8") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n")


def freeze_query_qrels(
    fixture_manifest_path: Path | str,
    *,
    repository_root: Path | str,
) -> dict[str, Any]:
    """Freeze exact fixture bytes and their predeclared relevance judgments."""
    manifest_path = Path(fixture_manifest_path)
    root = Path(repository_root).resolve()
    manifest_bytes = manifest_path.read_bytes()
    fixture = json.loads(manifest_bytes)
    queries: list[dict[str, Any]] = []
    observed_ids: set[str] = set()
    for raw in fixture.get("archetypes") or []:
        if not isinstance(raw, dict):
            raise GraphEmbeddingQualificationError("fixture archetype is not an object")
        query_id = str(raw.get("slug") or "").strip()
        if not query_id or query_id in observed_ids:
            raise GraphEmbeddingQualificationError(f"invalid or duplicate query id: {query_id}")
        observed_ids.add(query_id)
        jd_binding, jd_bytes = _file_binding(Path(str(raw.get("jd_path") or "")), repository_root=root)
        brief_binding, brief_bytes = _file_binding(
            Path(str(raw.get("brief_path") or "")), repository_root=root
        )
        jd_text = _normalized_utf8(jd_bytes, label=f"{query_id} JD")
        brief_text = _normalized_utf8(brief_bytes, label=f"{query_id} brief")
        query_text = jd_text.rstrip("\n") + "\n" + brief_text
        relevant = sorted({str(value) for value in raw.get("expected_skill_ids") or []})
        excluded = sorted({str(value) for value in raw.get("excluded_skill_ids") or []})
        if not relevant:
            raise GraphEmbeddingQualificationError(f"{query_id}: qrels are empty")
        if set(relevant) & set(excluded):
            raise GraphEmbeddingQualificationError(f"{query_id}: qrel/exclusion overlap")
        queries.append(
            {
                "query_id": query_id,
                "label": str(raw.get("label") or query_id),
                "jd": jd_binding,
                "brief": brief_binding,
                "query_text": query_text,
                "query_text_sha256": hashlib.sha256(query_text.encode("utf-8")).hexdigest(),
                "role_family_ids": sorted(
                    {str(value) for value in raw.get("expected_role_family_ids") or []}
                ),
                "pillar_ids": sorted(
                    {str(value) for value in raw.get("expected_pillar_ids") or []}
                ),
                "track_weights": {
                    str(key): float(value)
                    for key, value in sorted((raw.get("weight_override") or {}).items())
                },
                "priority_sections": sorted(
                    {str(value) for value in raw.get("priority_sections_w14") or []}
                ),
                "relevant_assertion_ids": relevant,
                "excluded_assertion_ids": excluded,
            }
        )
    payload: dict[str, Any] = {
        "schema_version": QUERY_QREL_SCHEMA_VERSION,
        "fixture_manifest": {
            "path": manifest_path.resolve().relative_to(root).as_posix(),
            "size": len(manifest_bytes),
            "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        },
        "query_count": len(queries),
        "relevance_judgment_count": sum(
            len(query["relevant_assertion_ids"]) for query in queries
        ),
        "queries": sorted(queries, key=lambda row: row["query_id"]),
    }
    payload["query_qrel_sha256"] = canonical_sha256(payload)
    return payload


def _features(text: str) -> Counter[str]:
    tokens = _TOKEN_RE.findall(text.lower())
    features = tokens + [f"{left}_{right}" for left, right in zip(tokens, tokens[1:])]
    return Counter(features)


def _sparse_rank(query: str, documents: Mapping[str, str]) -> list[str]:
    assertion_ids = sorted(documents)
    document_features = {key: _features(documents[key]) for key in assertion_ids}
    document_frequency: Counter[str] = Counter()
    for features in document_features.values():
        document_frequency.update(features.keys())
    size = len(assertion_ids)
    idf = {
        token: math.log((1.0 + size) / (1.0 + frequency)) + 1.0
        for token, frequency in document_frequency.items()
    }

    def vector(features: Counter[str]) -> dict[str, float]:
        return {
            token: (1.0 + math.log(count)) * idf.get(token, math.log(1.0 + size) + 1.0)
            for token, count in features.items()
            if count > 0
        }

    query_vector = vector(_features(query))
    query_norm = math.sqrt(math.fsum(value * value for value in query_vector.values()))
    scored: list[tuple[float, str]] = []
    for assertion_id in assertion_ids:
        document_vector = vector(document_features[assertion_id])
        document_norm = math.sqrt(
            math.fsum(value * value for value in document_vector.values())
        )
        if not query_norm or not document_norm:
            score = 0.0
        else:
            score = math.fsum(
                value * document_vector.get(token, 0.0)
                for token, value in query_vector.items()
            ) / (query_norm * document_norm)
        scored.append((score, assertion_id))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return [assertion_id for _, assertion_id in scored]


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]],
    *,
    assertion_ids: set[str],
    rank_constant: int,
) -> list[str]:
    if rank_constant <= 0:
        raise GraphEmbeddingQualificationError("RRF rank constant must be positive")
    scores = dict.fromkeys(assertion_ids, 0.0)
    for ranking in rankings:
        seen: set[str] = set()
        for rank, assertion_id in enumerate(ranking, start=1):
            if assertion_id in assertion_ids and assertion_id not in seen:
                scores[assertion_id] += 1.0 / (rank_constant + rank)
                seen.add(assertion_id)
    return sorted(scores, key=lambda assertion_id: (-scores[assertion_id], assertion_id))


def _recall_metrics(
    rankings: Mapping[str, Sequence[str]],
    queries: Sequence[Mapping[str, Any]],
    *,
    k: int,
) -> tuple[dict[str, float | int], list[dict[str, Any]]]:
    per_query: list[dict[str, Any]] = []
    recall_values: list[float] = []
    total_hits = 0
    total_relevant = 0
    for query in queries:
        query_id = str(query["query_id"])
        relevant = {str(value) for value in query.get("relevant_assertion_ids") or []}
        top = list(rankings.get(query_id) or [])[:k]
        hits = sorted(relevant & set(top))
        missing = sorted(relevant - set(top))
        recall = len(hits) / len(relevant) if relevant else 0.0
        recall_values.append(recall)
        total_hits += len(hits)
        total_relevant += len(relevant)
        per_query.append(
            {
                "query_id": query_id,
                "relevant_count": len(relevant),
                "hit_count": len(hits),
                "recall_at_k": recall,
                "hits": hits,
                "missing": missing,
            }
        )
    macro = math.fsum(recall_values) / len(recall_values) if recall_values else 0.0
    micro = total_hits / total_relevant if total_relevant else 0.0
    return (
        {
            "k": k,
            "query_count": len(queries),
            "relevance_judgment_count": total_relevant,
            "hit_count": total_hits,
            "macro_recall_at_k": macro,
            "micro_recall_at_k": micro,
        },
        per_query,
    )


def _validate_query_qrels(query_qrels: Mapping[str, Any]) -> bool:
    unsigned = dict(query_qrels)
    digest = str(unsigned.pop("query_qrel_sha256", ""))
    return bool(digest) and digest == canonical_sha256(unsigned)


def evaluate_graph_embedding_qualification(
    *,
    graph_payload: Mapping[str, Any],
    corpus: Mapping[str, Any],
    query_qrels: Mapping[str, Any],
    dense_rankings: Mapping[str, Sequence[Mapping[str, Any]]],
    thresholds: Mapping[str, float | int],
    projection_issues: Sequence[str],
) -> dict[str, Any]:
    """Evaluate retrieval quality and exact authority/vector parity."""
    queries = [row for row in query_qrels.get("queries") or [] if isinstance(row, dict)]
    assertions = {
        str(row.get("assertion_id") or ""): row
        for row in corpus.get("assertions") or []
        if isinstance(row, dict)
    }
    graph_rows = {
        str(row.get("skill_id") or ""): row
        for row in graph_payload.get("skill_rows") or []
        if isinstance(row, dict)
    }
    assertion_ids = set(assertions)
    graph_digest_matches = (corpus.get("source_digests") or {}).get(
        "graph_sha256"
    ) == canonical_sha256(graph_payload)

    exact_documents = {
        assertion_id: str(row.get("embedding_text") or "")
        for assertion_id, row in assertions.items()
    }
    fact_documents = {
        assertion_id: " ".join(
            str(value) for value in (row.get("semantic_card") or {}).get("evidence_summaries") or []
        )
        for assertion_id, row in assertions.items()
    }
    exact_rankings: dict[str, list[str]] = {}
    fact_rankings: dict[str, list[str]] = {}
    normalized_dense_rankings: dict[str, list[str]] = {}
    stale_ids: set[str] = set()
    orphan_ids: set[str] = set()
    unauthorized_ids: set[str] = set()
    authority_bypass_count = 0
    parity_scores: list[float] = []
    eligible_candidate_rows = 0
    total_candidate_rows = 0

    for query in queries:
        query_id = str(query.get("query_id") or "")
        query_text = str(query.get("query_text") or "")
        exact_rankings[query_id] = _sparse_rank(query_text, exact_documents)
        fact_rankings[query_id] = _sparse_rank(query_text, fact_documents)
        dense_rows = list(dense_rankings.get(query_id) or [])
        dense_ids: list[str] = []
        for candidate in dense_rows:
            total_candidate_rows += 1
            if set(candidate) != {"assertion_id", "similarity"}:
                authority_bypass_count += 1
            assertion_id = str(candidate.get("assertion_id") or "")
            try:
                similarity = float(candidate.get("similarity"))
            except (TypeError, ValueError):
                similarity = math.nan
            if not math.isfinite(similarity):
                authority_bypass_count += 1
            if assertion_id in dense_ids:
                authority_bypass_count += 1
            dense_ids.append(assertion_id)
            assertion = assertions.get(assertion_id)
            graph_row = graph_rows.get(assertion_id)
            if assertion is None or graph_row is None:
                orphan_ids.add(assertion_id)
                continue
            if graph_row.get("retrieval_eligible") is not True:
                unauthorized_ids.add(assertion_id)
                continue
            if (
                assertion.get("skill_row_sha256") != canonical_sha256(graph_row)
                or sorted(assertion.get("fact_links") or [])
                != sorted(graph_row.get("fact_id_links") or [])
            ):
                stale_ids.add(assertion_id)
                continue
            eligible_candidate_rows += 1
        observed = set(dense_ids)
        union = observed | assertion_ids
        parity_scores.append(len(observed & assertion_ids) / len(union) if union else 1.0)
        normalized_dense_rankings[query_id] = dense_ids

    exact_path_hits = 0
    exact_path_total = 0
    for query in queries:
        for assertion_id in query.get("relevant_assertion_ids") or []:
            exact_path_total += 1
            assertion = assertions.get(str(assertion_id))
            graph_row = graph_rows.get(str(assertion_id))
            if assertion is None or graph_row is None:
                continue
            lineage_ids = sorted(
                str(row.get("source_id") or "")
                for row in assertion.get("source_lineage") or []
                if isinstance(row, dict)
            )
            if (
                graph_digest_matches
                and graph_row.get("retrieval_eligible") is True
                and assertion.get("skill_row_sha256") == canonical_sha256(graph_row)
                and sorted(assertion.get("fact_links") or [])
                == sorted(graph_row.get("fact_id_links") or [])
                and lineage_ids == sorted(assertion.get("fact_links") or [])
                and bool(assertion.get("allowed_sections"))
            ):
                exact_path_hits += 1

    hybrid_rankings = {
        str(query.get("query_id") or ""): reciprocal_rank_fusion(
            [
                exact_rankings.get(str(query.get("query_id") or ""), []),
                fact_rankings.get(str(query.get("query_id") or ""), []),
                normalized_dense_rankings.get(str(query.get("query_id") or ""), []),
            ],
            assertion_ids=assertion_ids,
            rank_constant=int(thresholds["rrf_rank_constant"]),
        )
        for query in queries
    }
    k = int(thresholds["retrieval_k"])
    retrieval_metrics: dict[str, dict[str, float | int]] = {}
    per_query: dict[str, list[dict[str, Any]]] = {}
    for name, rankings in (
        ("exact", exact_rankings),
        ("fact_vector", fact_rankings),
        ("dense", normalized_dense_rankings),
        ("hybrid", hybrid_rankings),
    ):
        retrieval_metrics[name], per_query[name] = _recall_metrics(rankings, queries, k=k)

    structural_metrics: dict[str, float | int] = {
        "authority_eligibility_accuracy": (
            eligible_candidate_rows / total_candidate_rows if total_candidate_rows else 0.0
        ),
        "exact_path_accuracy": (
            exact_path_hits / exact_path_total if exact_path_total else 0.0
        ),
        "assertion_vector_parity": min(parity_scores) if parity_scores else 0.0,
        "stale_candidate_count": len(stale_ids),
        "orphan_candidate_count": len(orphan_ids),
        "unauthorized_candidate_count": len(unauthorized_ids),
        "authority_bypass_count": authority_bypass_count,
    }

    failures: list[str] = []
    if not _validate_query_qrels(query_qrels):
        failures.append("QUERY_QREL_DIGEST_MISMATCH")
    if projection_issues:
        failures.extend(f"PROJECTION:{issue}" for issue in projection_issues)
    if not graph_digest_matches:
        failures.append("CORPUS_GRAPH_DIGEST_MISMATCH")
    for mode in ("exact", "fact_vector", "dense", "hybrid"):
        metrics = retrieval_metrics[mode]
        for aggregation in ("macro", "micro"):
            metric_name = f"{aggregation}_recall_at_k"
            threshold_name = f"{mode}_{aggregation}_recall_at_k_min"
            if float(metrics[metric_name]) < float(thresholds[threshold_name]):
                failures.append(f"THRESHOLD:{threshold_name}")
    for metric_name in (
        "authority_eligibility_accuracy",
        "exact_path_accuracy",
        "assertion_vector_parity",
    ):
        if float(structural_metrics[metric_name]) < float(thresholds[f"{metric_name}_min"]):
            failures.append(f"THRESHOLD:{metric_name}_min")
    for metric_name in (
        "stale_candidate_count",
        "orphan_candidate_count",
        "unauthorized_candidate_count",
        "authority_bypass_count",
    ):
        if int(structural_metrics[metric_name]) > int(thresholds[f"{metric_name}_max"]):
            failures.append(f"THRESHOLD:{metric_name}_max")

    report: dict[str, Any] = {
        "schema_version": QUALIFICATION_SCHEMA_VERSION,
        "status": "PASS" if not failures else "FAIL",
        "query_qrel_sha256": str(query_qrels.get("query_qrel_sha256") or ""),
        "corpus_sha256": str(corpus.get("corpus_sha256") or ""),
        "graph_sha256": canonical_sha256(graph_payload),
        "thresholds": dict(thresholds),
        "thresholds_sha256": canonical_sha256(dict(thresholds)),
        "retrieval_metrics": retrieval_metrics,
        "structural_metrics": structural_metrics,
        "per_query": per_query,
        "projection_issues": list(projection_issues),
        "failures": sorted(set(failures)),
    }
    report["qualification_sha256"] = canonical_sha256(report)
    return report


__all__ = [
    "GraphEmbeddingQualificationError",
    "QUALIFICATION_SCHEMA_VERSION",
    "QUALIFICATION_THRESHOLDS",
    "QUERY_QREL_SCHEMA_VERSION",
    "evaluate_graph_embedding_qualification",
    "freeze_query_qrels",
    "reciprocal_rank_fusion",
]
