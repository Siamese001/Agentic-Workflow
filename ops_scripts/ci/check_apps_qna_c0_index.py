"""CI gate: verify apps_qna C0 canonical Chroma and flat fallback health.

Checks:
1. Canonical Chroma persist directory exists.
2. Canonical collection ``apps_qna_interview_cards`` exists.
3. Chroma metadata is BGE-M3, cosine, 1024 dimensions.
4. Chroma vector count is the expected apps_qna C0 corpus size.
5. Chroma sample read returns at least one migrated row.
6. External flat fallback at C:/AgenticEmbeddings remains readable.

Exit codes:
    0: All checks passed
    1: One or more checks failed

Usage:
    python ops_scripts/ci/check_apps_qna_c0_index.py [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

INDEX_DIR = Path("C:/AgenticEmbeddings/indexes/apps_qna_interview_cards")
REQUIRED_FILES = ("index.json", "manifest.json", "meta.json")

CHROMA_COLLECTION_NAME = "apps_qna_interview_cards"
EXPECTED_SCHEMA_VERSION = "1"
EXPECTED_MODEL = "BAAI/bge-m3"
EXPECTED_DIMS = 1024
EXPECTED_VECTOR_COUNT = 110
EXPECTED_DISTANCE = "cosine"

CheckContext = dict[str, Any]
CheckFn = Callable[[CheckContext], tuple[bool, str]]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _expected_check_exception(exc: Exception) -> bool:
    if isinstance(exc, (ImportError, AttributeError, RuntimeError, TypeError, ValueError, OSError, KeyError)):
        return True
    return type(exc).__name__ in {"ChromaError", "InvalidCollectionException", "NotFoundError"}


def _manifest_from_context(context: CheckContext) -> dict[str, Any] | None:
    manifest = context.get("flat_manifest")
    return manifest if isinstance(manifest, dict) else None


def _collection_from_context(context: CheckContext) -> Any | None:
    return context.get("chroma_collection")


def check_chroma_persist_dir(context: CheckContext) -> tuple[bool, str]:
    from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir

    persist_dir = canonical_persist_dir()
    context["chroma_persist_dir"] = persist_dir
    if not persist_dir.exists():
        return False, f"Canonical Chroma persist dir not found: {persist_dir}"
    return True, f"Canonical Chroma persist dir exists: {persist_dir}"


def check_chroma_collection(context: CheckContext) -> tuple[bool, str]:
    from agentic_core.L4_state.utils.client.chroma_client import chromadb_module as chromadb

    persist_dir = context.get("chroma_persist_dir")
    if not isinstance(persist_dir, Path):
        return False, "Skipped: canonical Chroma persist dir unavailable"
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
    context["chroma_collection"] = collection
    return True, f"Chroma collection exists: {CHROMA_COLLECTION_NAME}"


def check_chroma_metadata(context: CheckContext) -> tuple[bool, str]:
    collection = _collection_from_context(context)
    if collection is None:
        return False, "Skipped: Chroma collection unavailable"
    metadata = getattr(collection, "metadata", None) or {}
    model = metadata.get("embedding_model")
    dims = _as_int(metadata.get("embedding_dim", metadata.get("embedding_dimension")))
    distance = metadata.get("hnsw:space")
    if model != EXPECTED_MODEL or dims != EXPECTED_DIMS or distance != EXPECTED_DISTANCE:
        return (
            False,
            "Wrong Chroma metadata: "
            f"embedding_model={model}, embedding_dim={dims}, hnsw:space={distance}",
        )
    return True, f"Chroma metadata correct: {model}, {dims} dims, {distance}"


def check_chroma_vector_count(context: CheckContext) -> tuple[bool, str]:
    collection = _collection_from_context(context)
    if collection is None:
        return False, "Skipped: Chroma collection unavailable"
    count = int(collection.count())
    if count != EXPECTED_VECTOR_COUNT:
        return False, f"Wrong Chroma vector count: {count} (expected {EXPECTED_VECTOR_COUNT})"
    return True, f"Chroma vector count correct: {count}"


def check_chroma_sample_get(context: CheckContext) -> tuple[bool, str]:
    collection = _collection_from_context(context)
    if collection is None:
        return False, "Skipped: Chroma collection unavailable"
    sample = collection.get(limit=1, include=["metadatas"])
    ids = sample.get("ids") or []
    if not ids:
        return False, "Chroma sample read returned no ids"
    metadatas = sample.get("metadatas") or []
    metadata = metadatas[0] if metadatas and isinstance(metadatas[0], dict) else {}
    if metadata.get("embedding_model") != EXPECTED_MODEL:
        return False, f"Chroma sample row missing embedding_model={EXPECTED_MODEL}"
    return True, f"Chroma sample read OK: {ids[0]}"


def check_flat_index_exists(context: CheckContext) -> tuple[bool, str]:
    if not INDEX_DIR.exists():
        return False, f"Flat fallback index directory not found: {INDEX_DIR}"
    return True, f"Flat fallback index directory exists: {INDEX_DIR}"


def check_flat_required_files(context: CheckContext) -> tuple[bool, str]:
    missing = [filename for filename in REQUIRED_FILES if not (INDEX_DIR / filename).exists()]
    if missing:
        return False, f"Flat fallback required files missing: {', '.join(missing)}"
    context["flat_manifest"] = _load_json(INDEX_DIR / "manifest.json")
    return True, f"Flat fallback required files present: {', '.join(REQUIRED_FILES)}"


def check_flat_schema_version(context: CheckContext) -> tuple[bool, str]:
    manifest = _manifest_from_context(context)
    if manifest is None:
        return False, "Skipped: flat fallback manifest unavailable"
    schema_version = str(manifest.get("schema_version"))
    if schema_version != EXPECTED_SCHEMA_VERSION:
        return False, f"Unexpected flat schema_version: {schema_version} (expected {EXPECTED_SCHEMA_VERSION})"
    return True, f"Flat schema version correct: {schema_version}"


def check_flat_embedding_model(context: CheckContext) -> tuple[bool, str]:
    manifest = _manifest_from_context(context)
    if manifest is None:
        return False, "Skipped: flat fallback manifest unavailable"
    embedder_id = manifest.get("embedder_id", "")
    model_version = manifest.get("model_version", "")
    if embedder_id != EXPECTED_MODEL or model_version != EXPECTED_MODEL:
        return (
            False,
            f"Wrong flat embedding model: embedder_id={embedder_id}, model_version={model_version}",
        )
    return True, f"Flat embedding model correct: {embedder_id}"


def check_flat_dimensions(context: CheckContext) -> tuple[bool, str]:
    manifest = _manifest_from_context(context)
    if manifest is None:
        return False, "Skipped: flat fallback manifest unavailable"
    dims = _as_int(manifest.get("dims"))
    if dims != EXPECTED_DIMS:
        return False, f"Wrong flat dimensions: {dims} (expected {EXPECTED_DIMS})"
    return True, f"Flat dimensions correct: {dims}"


def check_flat_vector_count(context: CheckContext) -> tuple[bool, str]:
    manifest = _manifest_from_context(context)
    if manifest is None:
        return False, "Skipped: flat fallback manifest unavailable"
    count = _as_int(manifest.get("vector_count"))
    if count != EXPECTED_VECTOR_COUNT:
        return False, f"Wrong flat vector count: {count} (expected {EXPECTED_VECTOR_COUNT})"
    return True, f"Flat vector count correct: {count}"


def check_flat_sample_vector(context: CheckContext) -> tuple[bool, str]:
    index_data = _load_json(INDEX_DIR / "index.json")
    vectors = index_data.get("vectors", [])
    if not vectors:
        return False, "Flat fallback index has no vectors"
    first = vectors[0]
    if not isinstance(first, dict) or "id" not in first or "embedding" not in first:
        return False, "Flat fallback vector missing required fields (id, embedding)"
    embedding = first.get("embedding", [])
    if not isinstance(embedding, list) or len(embedding) != EXPECTED_DIMS:
        return False, f"Flat fallback first vector has wrong dimensions: {len(embedding)}"
    return True, f"Flat fallback sample vector OK: {len(vectors)} vectors available"


def _run_check(context: CheckContext, check_id: str, target: str, check_fn: CheckFn) -> dict[str, Any]:
    try:
        passed, message = check_fn(context)
    except Exception as exc:  # noqa: BLE001
        if not _expected_check_exception(exc):
            raise
        passed = False
        message = f"Check raised expected retrieval exception: {exc}"
    return {
        "check_id": check_id,
        "target": target,
        "passed": passed,
        "message": message,
    }


def run_all_checks() -> tuple[bool, list[dict[str, Any]]]:
    context: CheckContext = {}
    checks: tuple[tuple[str, str, CheckFn], ...] = (
        ("CHROMA_PERSIST_DIR", "primary_chroma", check_chroma_persist_dir),
        ("CHROMA_COLLECTION", "primary_chroma", check_chroma_collection),
        ("CHROMA_METADATA", "primary_chroma", check_chroma_metadata),
        ("CHROMA_VECTOR_COUNT", "primary_chroma", check_chroma_vector_count),
        ("CHROMA_SAMPLE_GET", "primary_chroma", check_chroma_sample_get),
        ("FLAT_INDEX_EXISTS", "flat_fallback", check_flat_index_exists),
        ("FLAT_REQUIRED_FILES", "flat_fallback", check_flat_required_files),
        ("FLAT_SCHEMA_VERSION", "flat_fallback", check_flat_schema_version),
        ("FLAT_EMBEDDING_MODEL", "flat_fallback", check_flat_embedding_model),
        ("FLAT_DIMENSIONS", "flat_fallback", check_flat_dimensions),
        ("FLAT_VECTOR_COUNT", "flat_fallback", check_flat_vector_count),
        ("FLAT_SAMPLE_VECTOR", "flat_fallback", check_flat_sample_vector),
    )
    results = [_run_check(context, check_id, target, check_fn) for check_id, target, check_fn in checks]
    return all(result["passed"] for result in results), results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify apps_qna C0 canonical Chroma and flat fallback health")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args(argv)

    all_passed, results = run_all_checks()
    report = {
        "passed": all_passed,
        "checks": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for result in results if result["passed"]),
            "failed": sum(1 for result in results if not result["passed"]),
            "primary_chroma_passed": all(
                result["passed"] for result in results if result["target"] == "primary_chroma"
            ),
            "flat_fallback_passed": all(
                result["passed"] for result in results if result["target"] == "flat_fallback"
            ),
        },
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if all_passed else "FAIL"
        print(f"apps_qna C0 index check: {status}")
        print(f"  Total: {report['summary']['total']}")
        print(f"  Passed: {report['summary']['passed']}")
        print(f"  Failed: {report['summary']['failed']}")
        print(f"  Primary Chroma passed: {report['summary']['primary_chroma_passed']}")
        print(f"  Flat fallback passed: {report['summary']['flat_fallback_passed']}")
        print()
        for result in results:
            icon = "PASS" if result["passed"] else "FAIL"
            print(f"  [{icon}] {result['target']}::{result['check_id']}: {result['message']}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
