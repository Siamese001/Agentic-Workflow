"""Offline builder for immutable C0.3 assertion and BGE-M3 vector generations."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.c03_graph_authority_reconciliation import (
    reconcile_graph_authority,
)
from apps_rg.fact_inventory.c03_skill_assertion_corpus import (
    build_skill_assertion_corpus,
    canonical_sha256,
    validate_skill_assertion_corpus,
)
from apps_rg.runtime.graph_skill_embedding_projection import (
    build_embedding_projection,
    validate_embedding_projection,
)

MODEL_ID = "BAAI/bge-m3"
MODEL_DIMENSION = 1024


class SkillEmbeddingBuildError(RuntimeError):
    """Raised when offline generation cannot preserve exact authority."""


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_local_model_manifest(model_path: Path | str) -> dict[str, Any]:
    root = Path(model_path).resolve()
    if not root.is_dir():
        raise SkillEmbeddingBuildError(f"local BGE-M3 directory missing: {root}")
    files: list[dict[str, Any]] = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda p: p.as_posix()):
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
        )
    if not files:
        raise SkillEmbeddingBuildError("local BGE-M3 directory contains no files")
    revision = root.name
    manifest: dict[str, Any] = {
        "schema_version": "apps_rg.local_embedding_model_manifest.v1",
        "model_id": MODEL_ID,
        "revision": revision,
        "dimension": MODEL_DIMENSION,
        "normalization": "l2",
        "file_count": len(files),
        "total_bytes": sum(int(row["size"]) for row in files),
        "files": files,
    }
    manifest["artifact_sha256"] = canonical_sha256(manifest)
    return manifest


def encode_bge_m3(
    texts: list[str],
    *,
    model_path: Path | str,
    device: str,
    batch_size: int = 16,
) -> tuple[dict[str, Any], list[list[float]]]:
    if not texts:
        raise SkillEmbeddingBuildError("cannot embed an empty assertion corpus")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    try:
        import torch
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SkillEmbeddingBuildError("BGE-M3 runtime dependencies are unavailable") from exc
    if device.startswith("cuda") and not torch.cuda.is_available():
        raise SkillEmbeddingBuildError("CUDA requested but unavailable")
    model = SentenceTransformer(str(Path(model_path).resolve()), device=device, local_files_only=True)
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    if tuple(vectors.shape) != (len(texts), MODEL_DIMENSION):
        raise SkillEmbeddingBuildError(
            f"BGE-M3 shape mismatch: expected {(len(texts), MODEL_DIMENSION)}, "
            f"observed {tuple(vectors.shape)}"
        )
    runtime = {
        "device": str(model.device),
        "torch_version": str(torch.__version__),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_name": (
            str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else None
        ),
        "fallback_used": False,
        "vector_count": len(texts),
        "dimension": MODEL_DIMENSION,
    }
    return runtime, [[float(value) for value in row] for row in vectors]


def _write_immutable_json(path: Path, payload: dict[str, Any]) -> str:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    data = rendered.encode("utf-8")
    if path.exists():
        if path.read_bytes() != data:
            raise SkillEmbeddingBuildError(f"immutable artifact collision: {path}")
        return hashlib.sha256(data).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.staging-{os.getpid()}")
    staging.write_bytes(data)
    os.replace(staging, path)
    return hashlib.sha256(data).hexdigest()


def _repository_path(path: Path, *, repository_root: Path) -> str:
    try:
        return path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as exc:
        raise SkillEmbeddingBuildError(f"source path escapes repository root: {path}") from exc


def build_assertion_embedding_generation(
    *,
    repository_root: Path,
    graph_path: Path,
    candidate_fact_path: Path,
    base_resume_path: Path,
    model_path: Path,
    output_dir: Path,
    device: str,
) -> dict[str, Any]:
    graph_bytes = graph_path.read_bytes()
    graph = json.loads(graph_bytes)
    if reconcile_graph_authority(graph) != graph:
        raise SkillEmbeddingBuildError("canonical graph requires reconciliation before embedding")
    candidate_fact_bytes = candidate_fact_path.read_bytes()
    base_resume_bytes = base_resume_path.read_bytes()
    facts = json.loads(candidate_fact_bytes)
    resume = json.loads(base_resume_bytes)
    corpus = build_skill_assertion_corpus(
        graph_payload=graph,
        candidate_fact_payload=facts,
        base_resume_payload=resume,
    )
    issues = validate_skill_assertion_corpus(corpus, graph_payload=graph)
    if issues:
        raise SkillEmbeddingBuildError("assertion corpus invalid: " + ", ".join(issues))

    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = output_dir / f"graph_skill_assertions.{corpus['corpus_sha256']}.json"
    corpus_file_sha256 = _write_immutable_json(corpus_path, corpus)

    model_manifest = build_local_model_manifest(model_path)
    model_manifest_path = output_dir / (
        f"bge_m3_model_manifest.{model_manifest['artifact_sha256']}.json"
    )
    model_manifest_file_sha256 = _write_immutable_json(model_manifest_path, model_manifest)

    assertion_rows = sorted(corpus["assertions"], key=lambda row: row["assertion_id"])
    runtime, vectors = encode_bge_m3(
        [str(row["embedding_text"]) for row in assertion_rows],
        model_path=model_path,
        device=device,
    )
    vectors_by_assertion = {
        str(row["assertion_id"]): vector
        for row, vector in zip(assertion_rows, vectors, strict=True)
    }
    staging_db = output_dir / f".graph_skill_embeddings.build-{os.getpid()}.sqlite"
    projection = build_embedding_projection(
        staging_db,
        corpus,
        vectors_by_assertion,
        model_manifest,
    )
    projection_path = output_dir / (
        f"graph_skill_embeddings.{projection['generation_sha256']}.sqlite"
    )
    if projection_path.exists():
        if _file_sha256(projection_path) != projection["sqlite_sha256"]:
            staging_db.unlink(missing_ok=True)
            raise SkillEmbeddingBuildError(f"immutable projection collision: {projection_path}")
        staging_db.unlink()
    else:
        os.replace(staging_db, projection_path)
    projection_issues = validate_embedding_projection(projection_path, corpus=corpus)
    if projection_issues:
        raise SkillEmbeddingBuildError(
            "embedding projection invalid: " + ", ".join(projection_issues)
        )

    manifest: dict[str, Any] = {
        "schema_version": "apps_rg.graph_skill_embedding_generation_manifest.v1",
        "graph": {
            "path": _repository_path(graph_path, repository_root=repository_root),
            "file_sha256": hashlib.sha256(graph_bytes).hexdigest(),
            "canonical_sha256": canonical_sha256(graph),
        },
        "candidate_fact_ledger": {
            "path": _repository_path(candidate_fact_path, repository_root=repository_root),
            "file_sha256": hashlib.sha256(candidate_fact_bytes).hexdigest(),
            "canonical_sha256": canonical_sha256(facts),
        },
        "base_resume": {
            "path": _repository_path(base_resume_path, repository_root=repository_root),
            "file_sha256": hashlib.sha256(base_resume_bytes).hexdigest(),
            "canonical_sha256": canonical_sha256(resume),
        },
        "assertion_corpus": {
            "path": corpus_path.name,
            "corpus_sha256": corpus["corpus_sha256"],
            "file_sha256": corpus_file_sha256,
            "assertion_count": len(assertion_rows),
            "exclusion_count": len(corpus["exclusions"]),
        },
        "model": {
            "path": model_manifest_path.name,
            "model_id": model_manifest["model_id"],
            "revision": model_manifest["revision"],
            "artifact_sha256": model_manifest["artifact_sha256"],
            "manifest_file_sha256": model_manifest_file_sha256,
            "dimension": model_manifest["dimension"],
        },
        "projection": {
            "path": projection_path.name,
            **projection,
        },
        "runtime_proof": runtime,
        "network_used": False,
        "fallback_used": False,
    }
    manifest["manifest_sha256"] = canonical_sha256(manifest)
    active_manifest_path = output_dir / "graph_skill_embedding_manifest.json"
    rendered_manifest = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    staging_manifest = active_manifest_path.with_name(
        f".{active_manifest_path.name}.staging-{os.getpid()}"
    )
    staging_manifest.write_text(rendered_manifest, encoding="utf-8", newline="\n")
    os.replace(staging_manifest, active_manifest_path)
    return manifest


__all__ = [
    "MODEL_DIMENSION",
    "MODEL_ID",
    "SkillEmbeddingBuildError",
    "build_assertion_embedding_generation",
    "build_local_model_manifest",
    "encode_bge_m3",
]
