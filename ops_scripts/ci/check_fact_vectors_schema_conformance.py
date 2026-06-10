"""CHECK-RG-FV-SCHEMA - fact_vectors metadata schema conformance gate.

Samples Chroma ``fact_vectors`` metadata and validates it against
apps_rg/config/domain_contract/fact_vectors_schema.yaml. Advisory by default;
fail-closed via APPS_RG_FACT_VECTORS_SCHEMA_FAIL_CLOSED=1.

Bypass: APPS_RG_FACT_VECTORS_SCHEMA_BYPASS=1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BYPASS_ENV = "APPS_RG_FACT_VECTORS_SCHEMA_BYPASS"
FAIL_CLOSED_ENV = "APPS_RG_FACT_VECTORS_SCHEMA_FAIL_CLOSED"
DEFAULT_COLLECTION = "fact_vectors"
DEFAULT_CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "fact_vectors_schema.yaml"
REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "fact_vectors_schema_conformance_gate.json"


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def load_schema(schema_path: Path) -> dict[str, Any]:
    with schema_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return dict(data)


def _value_present(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def _type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) or (isinstance(value, str) and value.strip().isdigit())
    if expected_type == "number":
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False
    if expected_type == "boolean":
        return isinstance(value, bool) or str(value).strip().lower() in {"true", "false", "1", "0"}
    return True


def _iso8601(value: Any) -> bool:
    if not _value_present(value):
        return False
    raw = str(value).strip()
    try:
        datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_metadata(metadata: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata_schema = dict(schema.get("metadata_schema") or {})
    for key, spec_obj in metadata_schema.items():
        spec = dict(spec_obj or {})
        value = metadata.get(key)
        if spec.get("required") and not _value_present(value):
            errors.append(f"{key}:missing_required")
            continue
        if not _value_present(value):
            continue
        expected_type = str(spec.get("type") or "")
        if expected_type and not _type_matches(value, expected_type):
            errors.append(f"{key}:type:{expected_type}")
        allowed_values = spec.get("allowed_values") or []
        if allowed_values and str(value) not in {str(v) for v in allowed_values}:
            errors.append(f"{key}:allowed_values:{sorted(str(v) for v in allowed_values)}")
        if spec.get("format") == "iso8601" and not _iso8601(value):
            errors.append(f"{key}:format:iso8601")
    return errors


def collect_metadata_sample(
    *,
    chroma_path: Path,
    collection_name: str,
    limit: int,
) -> tuple[int | None, list[dict[str, Any]], str]:
    try:
        from agentic_core.L4_state.utils.client.chroma_client import (
            chromadb_module as chromadb,
        )
    except ImportError as exc:
        return None, [], f"chromadb_adapter_import_failed:{exc}"

    try:
        client = chromadb.PersistentClient(path=str(chroma_path))
        collection = client.get_collection(collection_name)
        total = int(collection.count())
        sample = collection.get(limit=max(1, int(limit)), include=["metadatas"])
        metadatas = [dict(item or {}) for item in (sample.get("metadatas") or [])]
        return total, metadatas, "ok"
    except Exception as exc:  # guardian: allow-broad-except -- gate reports advisory diagnostics.
        return None, [], f"{type(exc).__name__}:{exc}"


def build_report(
    *,
    chroma_path: Path,
    collection_name: str,
    schema_path: Path,
    limit: int,
) -> dict[str, Any]:
    schema = load_schema(schema_path)
    total, metadatas, detail = collect_metadata_sample(
        chroma_path=chroma_path,
        collection_name=collection_name,
        limit=limit,
    )
    failures = []
    for index, metadata in enumerate(metadatas):
        errors = validate_metadata(metadata, schema)
        if errors:
            failures.append(
                {
                    "sample_index": index,
                    "id": str(metadata.get("chunk_id") or metadata.get("source_document_id") or ""),
                    "errors": errors,
                }
            )
    ok = total is not None and total > 0 and bool(metadatas) and not failures
    if total is None:
        summary = detail
    elif not metadatas:
        summary = "no_metadata_sample"
    elif failures:
        summary = f"{len(failures)} sample rows failed schema"
    else:
        summary = f"{len(metadatas)} sampled rows conform"
    return {
        "gate": "CHECK-RG-FV-SCHEMA",
        "collection": collection_name,
        "chroma_path": str(chroma_path),
        "schema_path": str(schema_path),
        "sample_limit": limit,
        "total_count": total,
        "sample_count": len(metadatas),
        "ok": ok,
        "detail": summary,
        "collection_detail": detail,
        "failures": failures,
        "required_fields": sorted(
            key
            for key, spec in (schema.get("metadata_schema") or {}).items()
            if dict(spec or {}).get("required")
        ),
    }


def _write_report(report: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"  Report: {REPORT_PATH}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chroma-path",
        type=Path,
        default=Path(os.environ.get("CHROMA_PERSIST_DIR", str(DEFAULT_CHROMA_PATH))),
    )
    parser.add_argument("--collection", default=os.environ.get("APPS_RG_FACT_VECTORS_COLLECTION", DEFAULT_COLLECTION))
    parser.add_argument("--schema-path", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--limit", type=int, default=int(os.environ.get("APPS_RG_FACT_VECTORS_SCHEMA_SAMPLE", "50")))
    parser.add_argument("--strict", action="store_true", help=f"Exit non-zero on mismatch (or set {FAIL_CLOSED_ENV}=1)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if _env_truthy(BYPASS_ENV):
        print(f"{BYPASS_ENV}=1 - skipping CHECK-RG-FV-SCHEMA")
        return 0

    strict = bool(args.strict or _env_truthy(FAIL_CLOSED_ENV))
    print("[CHECK-RG-FV-SCHEMA] apps_rg fact_vectors metadata schema conformance")
    report = build_report(
        chroma_path=Path(args.chroma_path),
        collection_name=str(args.collection or DEFAULT_COLLECTION),
        schema_path=Path(args.schema_path),
        limit=max(1, int(args.limit)),
    )
    report["advisory"] = not strict
    _write_report(report)
    if report["ok"]:
        print(f"  OK: {report['detail']}")
        return 0
    print(f"  ERROR: {report['detail']}")
    if strict:
        print(f"{FAIL_CLOSED_ENV}=1 or --strict - exiting non-zero")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
