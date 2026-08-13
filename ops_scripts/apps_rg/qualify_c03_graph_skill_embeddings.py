"""Qualify the immutable C0.3 BGE-M3 assertion projection offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps_rg.evals.c03_graph_embedding_qualification import (
    QUALIFICATION_THRESHOLDS,
    evaluate_graph_embedding_qualification,
    freeze_query_qrels,
)
from apps_rg.fact_inventory.c03_skill_assertion_corpus import canonical_sha256
from apps_rg.fact_inventory.c03_skill_embedding_builder import (
    build_local_model_manifest,
    encode_bge_m3,
)
from apps_rg.runtime.graph_skill_embedding_projection import (
    GraphSkillEmbeddingIndex,
    validate_embedding_projection,
)


class QualificationRunnerError(RuntimeError):
    """Raised when an input artifact does not match its immutable binding."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise QualificationRunnerError(f"JSON artifact is not an object: {path}")
    return value


def _require_digest(path: Path, expected: str, *, label: str) -> None:
    observed = _sha256(path)
    if observed != expected:
        raise QualificationRunnerError(
            f"{label} digest mismatch: expected {expected}, observed {observed}"
        )


def _write_immutable_json(path: Path, payload: dict[str, Any]) -> str:
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != data:
            raise QualificationRunnerError(f"immutable artifact collision: {path}")
        return hashlib.sha256(data).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.staging-{os.getpid()}")
    staging.write_bytes(data)
    os.replace(staging, path)
    return hashlib.sha256(data).hexdigest()


def _publish_active_manifest(path: Path, payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.staging-{os.getpid()}")
    staging.write_bytes(data)
    os.replace(staging, path)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-manifest", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--embedding-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def run_qualification(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve()
    graph_path = args.graph.resolve()
    embedding_dir = args.embedding_dir.resolve()
    output_dir = args.output_dir.resolve()
    generation_manifest_path = embedding_dir / "graph_skill_embedding_manifest.json"
    generation = _load_json(generation_manifest_path)
    unsigned_generation = dict(generation)
    generation_digest = str(unsigned_generation.pop("manifest_sha256", ""))
    if generation_digest != canonical_sha256(unsigned_generation):
        raise QualificationRunnerError("embedding generation manifest digest mismatch")

    graph = _load_json(graph_path)
    _require_digest(graph_path, str(generation["graph"]["file_sha256"]), label="graph")
    if canonical_sha256(graph) != generation["graph"]["canonical_sha256"]:
        raise QualificationRunnerError("canonical graph digest mismatch")

    corpus_path = embedding_dir / str(generation["assertion_corpus"]["path"])
    model_manifest_path = embedding_dir / str(generation["model"]["path"])
    projection_path = embedding_dir / str(generation["projection"]["path"])
    _require_digest(
        corpus_path,
        str(generation["assertion_corpus"]["file_sha256"]),
        label="assertion corpus",
    )
    _require_digest(
        model_manifest_path,
        str(generation["model"]["manifest_file_sha256"]),
        label="model manifest",
    )
    _require_digest(
        projection_path,
        str(generation["projection"]["sqlite_sha256"]),
        label="embedding projection",
    )
    corpus = _load_json(corpus_path)
    model_manifest = _load_json(model_manifest_path)
    local_model_manifest = build_local_model_manifest(args.model_path.resolve())
    if local_model_manifest["artifact_sha256"] != model_manifest["artifact_sha256"]:
        raise QualificationRunnerError("local BGE-M3 artifact digest mismatch")

    query_qrels = freeze_query_qrels(
        args.fixture_manifest.resolve(),
        repository_root=repository_root,
    )
    queries = list(query_qrels["queries"])
    runtime_proof, query_vectors = encode_bge_m3(
        [str(query["query_text"]) for query in queries],
        model_path=args.model_path.resolve(),
        device=str(args.device),
        batch_size=len(queries),
    )
    before_projection_sha256 = _sha256(projection_path)
    dense_rankings: dict[str, list[dict[str, Any]]] = {}
    with GraphSkillEmbeddingIndex(
        projection_path,
        expected_corpus_sha256=str(corpus["corpus_sha256"]),
        expected_model_artifact_sha256=str(model_manifest["artifact_sha256"]),
    ) as index:
        for query, vector in zip(queries, query_vectors, strict=True):
            dense_rankings[str(query["query_id"])] = index.query(
                vector,
                k=len(corpus["assertions"]),
            )
    after_projection_sha256 = _sha256(projection_path)
    projection_read_only = before_projection_sha256 == after_projection_sha256
    projection_issues = validate_embedding_projection(projection_path, corpus=corpus)
    if not projection_read_only:
        projection_issues.append("PROJECTION_MUTATED_DURING_QUALIFICATION")

    report = evaluate_graph_embedding_qualification(
        graph_payload=graph,
        corpus=corpus,
        query_qrels=query_qrels,
        dense_rankings=dense_rankings,
        thresholds=QUALIFICATION_THRESHOLDS,
        projection_issues=projection_issues,
    )
    report.pop("qualification_sha256", None)
    report.update(
        {
            "embedding_generation_manifest_sha256": generation_digest,
            "projection": {
                "generation_sha256": generation["projection"]["generation_sha256"],
                "sqlite_sha256_before": before_projection_sha256,
                "sqlite_sha256_after": after_projection_sha256,
                "read_only": projection_read_only,
                "vector_count": generation["projection"]["vector_count"],
                "dimension": generation["projection"]["dimension"],
            },
            "model": {
                "model_id": model_manifest["model_id"],
                "revision": model_manifest["revision"],
                "artifact_sha256": model_manifest["artifact_sha256"],
            },
            "runtime_proof": runtime_proof,
            "network_used": False,
            "fallback_used": False,
            "completion_marker": (
                "GRAPH_EMBEDDINGS_QUALIFIED"
                if report["status"] == "PASS"
                else "GRAPH_EMBEDDING_QUALIFICATION_FAILED"
            ),
        }
    )
    report["qualification_sha256"] = canonical_sha256(report)

    output_dir.mkdir(parents=True, exist_ok=True)
    query_path = output_dir / (
        f"graph_embedding_query_qrels.{query_qrels['query_qrel_sha256']}.json"
    )
    thresholds_payload: dict[str, Any] = {
        "schema_version": "apps_rg.c03_graph_embedding_qualification_thresholds.v1",
        "thresholds": dict(QUALIFICATION_THRESHOLDS),
    }
    thresholds_payload["thresholds_sha256"] = canonical_sha256(thresholds_payload)
    thresholds_path = output_dir / (
        f"graph_embedding_qualification_thresholds."
        f"{thresholds_payload['thresholds_sha256']}.json"
    )
    report_path = output_dir / (
        f"graph_embedding_qualification.{report['qualification_sha256']}.json"
    )
    query_file_sha256 = _write_immutable_json(query_path, query_qrels)
    thresholds_file_sha256 = _write_immutable_json(thresholds_path, thresholds_payload)
    report_file_sha256 = _write_immutable_json(report_path, report)
    active_manifest: dict[str, Any] = {
        "schema_version": "apps_rg.c03_graph_embedding_qualification_manifest.v1",
        "status": report["status"],
        "completion_marker": report["completion_marker"],
        "query_qrels": {
            "path": query_path.name,
            "sha256": query_qrels["query_qrel_sha256"],
            "file_sha256": query_file_sha256,
        },
        "thresholds": {
            "path": thresholds_path.name,
            "sha256": thresholds_payload["thresholds_sha256"],
            "file_sha256": thresholds_file_sha256,
        },
        "qualification": {
            "path": report_path.name,
            "sha256": report["qualification_sha256"],
            "file_sha256": report_file_sha256,
        },
        "embedding_generation_manifest_sha256": generation_digest,
    }
    active_manifest["manifest_sha256"] = canonical_sha256(active_manifest)
    _publish_active_manifest(output_dir / "graph_embedding_qualification_manifest.json", active_manifest)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    args = _parse_args(argv)
    report = run_qualification(args)
    print(
        json.dumps(
            {
                "status": report["status"],
                "completion_marker": report["completion_marker"],
                "qualification_sha256": report["qualification_sha256"],
                "retrieval_metrics": report["retrieval_metrics"],
                "structural_metrics": report["structural_metrics"],
                "runtime_proof": report["runtime_proof"],
                "failures": report["failures"],
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
