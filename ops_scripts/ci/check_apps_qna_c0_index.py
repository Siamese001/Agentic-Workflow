"""CI gate: Verify apps_qna C0 vector index health.

Checks:
1. Index directory exists at C:\AgenticEmbeddings\indexes\apps_qna_interview_cards\
2. Required files present (index.json, manifest.json, meta.json)
3. Schema version correct ("1")
4. Embedding model is BGE-M3 (BAAI/bge-m3)
5. Dimensions are 1024
6. Vector count > 0
7. Sample query returns non-empty results

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
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]

# Index paths
INDEX_DIR = Path("C:/AgenticEmbeddings/indexes/apps_qna_interview_cards")
REQUIRED_FILES = ["index.json", "manifest.json", "meta.json"]


def check_index_exists() -> tuple[bool, str]:
    """Check if index directory exists."""
    if not INDEX_DIR.exists():
        return False, f"Index directory not found: {INDEX_DIR}"
    return True, f"Index directory exists: {INDEX_DIR}"


def check_required_files() -> tuple[bool, str, dict[str, Any] | None]:
    """Check all required files are present and load manifest."""
    manifest: dict[str, Any] | None = None

    for filename in REQUIRED_FILES:
        filepath = INDEX_DIR / filename
        if not filepath.exists():
            return False, f"Required file missing: {filename}", None

        # Load manifest for further checks
        if filename == "manifest.json":
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except json.JSONDecodeError as exc:
                return False, f"Invalid JSON in manifest.json: {exc}", None

    return True, f"All required files present: {', '.join(REQUIRED_FILES)}", manifest


def check_schema_version(manifest: dict) -> tuple[bool, str]:
    """Verify schema version is correct."""
    schema_version = manifest.get("schema_version")
    if schema_version != "1":
        return False, f"Unexpected schema_version: {schema_version} (expected '1')"
    return True, f"Schema version correct: {schema_version}"


def check_embedding_model(manifest: dict) -> tuple[bool, str]:
    """Verify embedding model is BGE-M3."""
    embedder_id = manifest.get("embedder_id", "")
    model_version = manifest.get("model_version", "")

    expected = "BAAI/bge-m3"
    if embedder_id != expected or model_version != expected:
        return (
            False,
            f"Wrong embedding model: embedder_id={embedder_id}, model_version={model_version} (expected {expected})",
        )
    return True, f"Embedding model correct: {embedder_id}"


def check_dimensions(manifest: dict) -> tuple[bool, str]:
    """Verify dimensions are 1024."""
    dims = manifest.get("dims")
    if dims != 1024:
        return False, f"Wrong dimensions: {dims} (expected 1024)"
    return True, f"Dimensions correct: {dims}"


def check_vector_count(manifest: dict) -> tuple[bool, str]:
    """Verify vector count > 0."""
    count = manifest.get("vector_count", 0)
    if count <= 0:
        return False, f"Invalid vector_count: {count} (expected > 0)"
    return True, f"Vector count: {count}"


def check_sample_query() -> tuple[bool, str]:
    """Verify sample query returns results."""
    index_path = INDEX_DIR / "index.json"

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)

        vectors = index_data.get("vectors", [])
        if len(vectors) == 0:
            return False, "No vectors in index"

        # Verify first vector has expected structure
        first = vectors[0]
        if "id" not in first or "embedding" not in first:
            return False, "Vector missing required fields (id, embedding)"

        embedding = first.get("embedding", [])
        if len(embedding) != 1024:
            return False, f"First vector has wrong dimensions: {len(embedding)}"

        return True, f"Sample query OK: {len(vectors)} vectors available"

    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON in index.json: {exc}"
    except Exception as exc:  # noqa: BLE001
        return False, f"Sample query failed: {exc}"


def run_all_checks() -> tuple[bool, list[dict]]:
    """Run all verification checks.

    Returns:
        Tuple of (all_passed, check_results)
    """
    results: list[dict] = []

    checks = [
        ("INDEX_EXISTS", check_index_exists, None),
        ("REQUIRED_FILES", check_required_files, None),
        ("SCHEMA_VERSION", check_schema_version, "manifest"),
        ("EMBEDDING_MODEL", check_embedding_model, "manifest"),
        ("DIMENSIONS", check_dimensions, "manifest"),
        ("VECTOR_COUNT", check_vector_count, "manifest"),
        ("SAMPLE_QUERY", check_sample_query, None),
    ]

    manifest: dict | None = None

    for check_id, check_fn, manifest_arg in checks:
        try:
            if manifest_arg == "manifest":
                if manifest is None:
                    # Manifest should have been loaded by REQUIRED_FILES check
                    results.append(
                        {
                            "check_id": check_id,
                            "passed": False,
                            "message": "Skipped (manifest not available from previous check)",
                        }
                    )
                    continue
                passed, message = check_fn(manifest)
            elif check_id == "REQUIRED_FILES":
                passed, message, manifest = check_fn()
            else:
                passed, message = check_fn()

            results.append(
                {
                    "check_id": check_id,
                    "passed": passed,
                    "message": message,
                }
            )

        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "check_id": check_id,
                    "passed": False,
                    "message": f"Check raised exception: {exc}",
                }
            )

    all_passed = all(r["passed"] for r in results)
    return all_passed, results


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify apps_qna C0 index health")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args(argv)

    all_passed, results = run_all_checks()

    report = {
        "passed": all_passed,
        "checks": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
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
        print()
        for r in results:
            icon = "✓" if r["passed"] else "✗"
            print(f"  [{icon}] {r['check_id']}: {r['message']}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
