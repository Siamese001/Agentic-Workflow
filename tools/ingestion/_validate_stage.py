"""Post-stage validator for the ChromaDB ingestion pipeline.

Runs after each ``tools/ingestion/ingest_*.py`` stage completes, samples
chunks from the target collection(s), and confirms:
    1. The collection exists and is non-empty.
    2. Every sampled chunk's metadata passes the ChunkMetadataV1 contract.
    3. The collection's declared ``embedding_dim`` matches the sample
       embedding length.

Invoked by ``tools/ingestion/pipeline.py`` (W2.3). CLI usable:

    python -m tools.ingestion._validate_stage --stage code

Exit codes:
    0 - all checks passed
    1 - at least one check failed (details on stdout)
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable

import chromadb

from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str
from agentic_core.L4_state.utils.chunk_metadata import (
    CHUNK_METADATA_VERSION,
    validate as validate_chunk_metadata,
)

# Stage → target ChromaDB collections. One stage may write multiple.
STAGE_COLLECTIONS: dict[str, tuple[str, ...]] = {
    "code": ("repo_code_chunks",),
    # Per-root code stages (W3.1) all write the same collection.
    "code_apps_rg": ("repo_code_chunks",),
    "code_apps_lic": ("repo_code_chunks",),
    "code_apps_eval": ("repo_code_chunks",),
    "code_apps_exec": ("repo_code_chunks",),
    "code_apps_research": ("repo_code_chunks",),
    "code_apps_shared": ("repo_code_chunks",),
    "code_apps_uw": ("repo_code_chunks",),
    "code_system_learning": ("repo_code_chunks",),
    "code_infrastructure": ("repo_code_chunks",),
    "code_tools": ("repo_code_chunks",),
    "code_ops_scripts": ("repo_code_chunks",),
    "docs": ("docs",),
    "docs_windsurf_rules": ("docs",),
    "docs_windsurf_skills": ("docs",),
    "docs_agents_md": ("docs",),
    "adg": ("repo_adg_graph",),
    "tests": ("repo_tests_guardrails",),
    "traces": ("traces",),
    "runtime": ("repo_runtime_evidence",),
    "history": ("repo_incidents_rca",),
    "web_to_chroma": ("agentic_best_practices",),
    "web_to_chroma_enhanced": ("agentic_best_practices",),
    # W5.1: tools/generate/ingestion/* canonical collection names.
    "gen_symbols": ("symbols",),
    "gen_code_chunks": ("code_chunks",),
    "gen_arch_docs": ("arch_docs",),
    "gen_process_docs": ("process_docs",),
    "gen_tests_guardrails": ("tests_guardrails",),
    "gen_runtime_evidence": ("runtime_evidence",),
    "gen_incidents_rca": ("incidents_rca",),
    "gen_repo_evidence": ("repo_evidence",),
    "gen_ext_knowledge": ("ext_knowledge",),
    "gen_ext_authority": ("ext_authority",),
    "gen_curated_agent_docs": ("process_docs",),
    "gen_agent_framework_docs": ("process_docs",),
}

DEFAULT_SAMPLE = 10


def _validate_collection(
    client: chromadb.PersistentClient,
    name: str,
    sample_size: int,
) -> tuple[bool, list[str]]:
    """Validate a single collection. Returns (ok, error_lines)."""
    errors: list[str] = []
    try:
        names = {c.name for c in client.list_collections()}
    except (OSError, RuntimeError) as exc:
        return False, [f"list_collections failed: {exc}"]

    if name not in names:
        return False, [f"collection {name!r} does not exist"]

    col = client.get_collection(name)
    try:
        count = col.count()
    except Exception as exc:  # guardian: allow-broad-exception -- Chroma rust binding raises opaque types
        return False, [f"count() raised {type(exc).__name__}: {exc}"]

    if count == 0:
        return False, [f"collection {name!r} is empty"]

    sample_n = min(sample_size, count)
    result = col.get(limit=sample_n, include=["metadatas", "embeddings"])
    # ChromaDB returns embeddings as a numpy 2-D array; truthiness check
    # raises. Use explicit None.
    metas_raw = result.get("metadatas")
    metas: Iterable[dict] = metas_raw if metas_raw is not None else []
    embs_raw = result.get("embeddings")
    embs = embs_raw if embs_raw is not None else []

    col_meta = col.metadata or {}
    declared_dim = col_meta.get("embedding_dim")
    declared_model = col_meta.get("embedding_model")

    drift_count = 0
    for i, meta in enumerate(metas):
        meta_errors = validate_chunk_metadata(meta or {})
        if meta_errors:
            drift_count += 1
            if drift_count <= 3:  # cap verbosity
                errors.append(f"chunk[{i}] metadata drift: {meta_errors[:4]}")
        # Per-chunk declared vs stored embedding model/dim
        stored_model = (meta or {}).get("embedding_model")
        if declared_model and stored_model and stored_model != declared_model:
            errors.append(f"chunk[{i}] embedding_model {stored_model!r} != collection {declared_model!r}")
        stored_dim = (meta or {}).get("embedding_dim")
        if declared_dim and stored_dim and stored_dim != declared_dim:
            errors.append(f"chunk[{i}] embedding_dim {stored_dim} != collection {declared_dim}")
        # Sampled embedding vector dim vs declared dim
        if len(embs) and i < len(embs) and embs[i] is not None:
            emb_vec = embs[i]
            got = len(emb_vec.tolist() if hasattr(emb_vec, "tolist") else list(emb_vec))
            if declared_dim and got != declared_dim:
                errors.append(f"chunk[{i}] actual vector dim {got} != collection declared {declared_dim}")

    if drift_count > 3:
        errors.append(f"... and {drift_count - 3} more chunks with metadata drift")

    print(
        f"  {name}: count={count} sampled={sample_n} "
        f"model={declared_model} dim={declared_dim} "
        f"drift={drift_count}/{sample_n}"
    )
    return (not errors), errors


def _build_sparse_sidecars(collections: tuple[str, ...]) -> None:
    """Build BM25 sparse sidecars for the given collections (W4.1).

    Best-effort: import failures, empty collections, and per-collection
    errors are logged but do not fail the stage — the dense path still
    works. Sparse sidecars are consumed by HybridSearchEngine when
    `enable_lexical=True` is passed to `search()`.
    """
    try:
        from tools.generate.ingestion.build_sparse_index import build_for_collection
    except ImportError as exc:
        print(f"  sparse: builder unavailable ({exc})")
        return
    for name in collections:
        try:
            build_for_collection(name, dry_run=False)
        except (
            Exception
        ) as exc:  # guardian: allow-broad-exception -- best-effort sidecar build, must not fail stage
            print(f"  sparse: {name} build failed: {exc}")


def validate_stage(stage: str, sample_size: int = DEFAULT_SAMPLE) -> int:
    """Validate every collection associated with ``stage``. Returns exit code."""
    collections = STAGE_COLLECTIONS.get(stage)
    if not collections:
        print(f"validate_stage: unknown stage {stage!r}; skipping.")
        return 0

    store = canonical_persist_dir_str()
    print(f"validate_stage: stage={stage} store={store} version={CHUNK_METADATA_VERSION}")
    try:
        client = chromadb.PersistentClient(path=store)
    except (OSError, RuntimeError) as exc:
        print(f"  FAIL: cannot open Chroma store at {store}: {exc}")
        return 1

    overall_ok = True
    for name in collections:
        ok, errs = _validate_collection(client, name, sample_size)
        if not ok:
            overall_ok = False
            for line in errs:
                print(f"  FAIL {name}: {line}")

    # W4.1: build BM25 sparse sidecars for every validated collection so
    # hybrid retrieval (HybridSearchEngine.search(enable_lexical=True))
    # has parity across all canonical collections. Skipped if validation
    # itself failed — a failed stage shouldn't pollute the sparse index.
    if overall_ok:
        _build_sparse_sidecars(collections)

    return 0 if overall_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=sorted(STAGE_COLLECTIONS))
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE)
    args = parser.parse_args()
    return validate_stage(args.stage, args.sample)


if __name__ == "__main__":
    sys.exit(main())
