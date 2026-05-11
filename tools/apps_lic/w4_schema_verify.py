"""W4 schema and field-map coverage verification for apps_lic ingress contract.

Produces two artefacts:
  artifacts/apps_lic/apps_lic_ingress_contract_v1_schema.json
      Pydantic-generated JSON Schema (draft 2020-12 via model_json_schema()).
      This is the SSOT for the runtime shape of AppsLicIngressContractV1.

  artifacts/apps_lic/w4_field_map_coverage_result.json
      Machine-readable coverage report consumed by W4 tests and the W4 receipt.

Usage (schema generation):
    python tools/apps_lic/w4_schema_verify.py --generate-schema

Usage (coverage check):
    python tools/apps_lic/w4_schema_verify.py --check-coverage

Usage (both):
    python tools/apps_lic/w4_schema_verify.py

Exit codes:
    0  — all checks pass
    1  — silently_dropped fields detected or coverage < 100%
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACTS_DIR = _REPO_ROOT / "artifacts" / "apps_lic"
_SCHEMA_OUT = _ARTIFACTS_DIR / "apps_lic_ingress_contract_v1_schema.json"
_COVERAGE_OUT = _ARTIFACTS_DIR / "w4_field_map_coverage_result.json"
_FIELD_MAP_PATH = (
    _REPO_ROOT / "apps_lic" / "contracts" / "apps_lic_ingress_field_map.v1.yaml"
)
_CONTRACT_MODULE = "apps_lic.contracts.apps_lic_ingress_contract_v1"
_CONTRACT_CLASS = "AppsLicIngressContractV1"
_PYDANTIC_MODEL_SOURCE = f"{_CONTRACT_MODULE}.{_CONTRACT_CLASS}"
_SCHEMA_GENERATION_COMMAND = (
    "python tools/apps_lic/w4_schema_verify.py --generate-schema"
)

PERMITTED_STATUSES = {"MAPPED", "DERIVED", "REJECTED", "DEFERRED"}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_contract_class() -> Any:
    import importlib

    mod = importlib.import_module(_CONTRACT_MODULE)
    return getattr(mod, _CONTRACT_CLASS)


def _load_field_map() -> dict[str, Any]:
    import yaml  # type: ignore[import]

    with open(_FIELD_MAP_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)  # type: ignore[return-value]


def _walk_schema_properties(
    schema: dict[str, Any],
    defs: dict[str, Any],
    prefix: str = "",
    visited: set[str] | None = None,
) -> list[str]:
    """Recursively collect leaf + branch paths from a JSON Schema object.

    Returns JSON-Pointer-style paths (no leading slash at root; caller adds it).
    Does NOT expand array items — field-map uses the parent pointer for lists.
    """
    if visited is None:
        visited = set()

    paths: list[str] = []
    props = schema.get("properties", {})

    for key, sub in props.items():
        pointer = f"{prefix}/{key}" if prefix else f"/{key}"
        paths.append(pointer)

        # Resolve $ref if present
        if "$ref" in sub:
            ref_name = sub["$ref"].split("/")[-1]
            if ref_name in visited:
                continue
            visited = visited | {ref_name}
            sub = defs.get(ref_name, {})

        # Recurse into object
        if sub.get("type") == "object" or "properties" in sub:
            paths.extend(
                _walk_schema_properties(sub, defs, pointer, visited)
            )
        # anyOf / oneOf pattern (Optional fields → one arm is the real type)
        for combiner in ("anyOf", "oneOf", "allOf"):
            for arm in sub.get(combiner, []):
                arm_resolved = arm
                if "$ref" in arm:
                    ref_name = arm["$ref"].split("/")[-1]
                    if ref_name not in visited:
                        arm_resolved = defs.get(ref_name, {})
                if "properties" in arm_resolved:
                    paths.extend(
                        _walk_schema_properties(
                            arm_resolved, defs, pointer, visited | {ref_name}
                            if "$ref" in arm else visited
                        )
                    )

    return paths


def _collect_schema_pointers(schema: dict[str, Any]) -> list[str]:
    defs = schema.get("$defs", {})
    return _walk_schema_properties(schema, defs)


def _resolve_pointer(pointer: str, mappings: dict[str, Any]) -> str | None:
    """Return the status for a pointer, or None if not covered."""
    if pointer in mappings:
        return mappings[pointer].get("status")
    return None


def _resolve_with_patterns(
    pointer: str,
    mappings: dict[str, Any],
    pattern_mappings: dict[str, Any],
    section_aggregations: dict[str, Any],
) -> str | None:
    # 1. Exact match
    status = _resolve_pointer(pointer, mappings)
    if status is not None:
        return status

    # 2. Section aggregation (parent pointer covers all children implicitly)
    for parent in section_aggregations:
        if pointer.startswith(parent):
            return section_aggregations[parent].get("status")

    # 3. Pattern prefix
    for prefix, entry in pattern_mappings.items():
        if pointer.startswith(prefix):
            return entry.get("status")

    # 4. Parent covered — if a parent pointer is MAPPED/DERIVED, its children
    #    are implicitly covered (the whole subtree travels with the parent).
    parts = pointer.split("/")
    for depth in range(len(parts) - 1, 0, -1):
        parent = "/".join(parts[:depth])
        parent_status = _resolve_pointer(parent, mappings)
        if parent_status in ("MAPPED", "DERIVED", "REJECTED", "DEFERRED"):
            return f"COVERED_BY_PARENT({parent_status})"

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_schema(write: bool = True) -> dict[str, Any]:
    """Generate JSON Schema from AppsLicIngressContractV1 and optionally write."""
    cls = _load_contract_class()
    schema: dict[str, Any] = cls.model_json_schema()
    if write:
        _ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        _SCHEMA_OUT.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[W4] Schema written to {_SCHEMA_OUT}")
    return schema


def check_coverage(
    schema: dict[str, Any] | None = None, write: bool = True
) -> dict[str, Any]:
    """Check field-map coverage against the Pydantic schema.

    Returns a coverage result dict. Writes to _COVERAGE_OUT when write=True.
    """
    if schema is None:
        if _SCHEMA_OUT.exists():
            schema = json.loads(_SCHEMA_OUT.read_text(encoding="utf-8"))
        else:
            schema = generate_schema(write=False)

    field_map = _load_field_map()
    mappings: dict[str, Any] = field_map.get("mappings", {})
    pattern_mappings: dict[str, Any] = field_map.get("pattern_mappings", {})
    section_aggregations: dict[str, Any] = field_map.get("section_aggregations", {})

    schema_pointers = _collect_schema_pointers(schema)

    silently_dropped: list[str] = []
    covered_by_status: dict[str, list[str]] = {
        "MAPPED": [],
        "DERIVED": [],
        "REJECTED": [],
        "DEFERRED": [],
        "COVERED_BY_PARENT": [],
    }

    for pointer in schema_pointers:
        status = _resolve_with_patterns(
            pointer, mappings, pattern_mappings, section_aggregations
        )
        if status is None:
            silently_dropped.append(pointer)
        elif status.startswith("COVERED_BY_PARENT"):
            covered_by_status["COVERED_BY_PARENT"].append(pointer)
        elif status in covered_by_status:
            covered_by_status[status].append(pointer)
        else:
            silently_dropped.append(pointer)

    # runtime_customization_package pointers
    rcp_pointers = [p for p in schema_pointers if p.startswith("/runtime_customization_package")]
    rcp_mapped = [
        p for p in rcp_pointers
        if _resolve_with_patterns(p, mappings, pattern_mappings, section_aggregations)
        in ("MAPPED", "DERIVED", "COVERED_BY_PARENT(MAPPED)", "COVERED_BY_PARENT(DERIVED)")
        or (
            _resolve_with_patterns(p, mappings, pattern_mappings, section_aggregations) or ""
        ).startswith("COVERED_BY_PARENT")
    ]
    rcp_derived = [
        p for p in rcp_pointers
        if _resolve_with_patterns(p, mappings, pattern_mappings, section_aggregations) == "DERIVED"
    ]

    total = len(schema_pointers)
    covered = total - len(silently_dropped)

    result: dict[str, Any] = {
        "schema_path": str(_SCHEMA_OUT.relative_to(_REPO_ROOT)).replace("\\", "/"),
        "pydantic_model_source": _PYDANTIC_MODEL_SOURCE,
        "schema_generation_command": _SCHEMA_GENERATION_COMMAND,
        "schema_regenerated": True,
        "total_pointers": total,
        "covered_pointers": covered,
        "mapped_pointers": len(covered_by_status["MAPPED"]),
        "derived_pointers": len(covered_by_status["DERIVED"]),
        "rejected_pointers": len(covered_by_status["REJECTED"]),
        "deferred_pointers": len(covered_by_status["DEFERRED"]),
        "covered_by_parent_pointers": len(covered_by_status["COVERED_BY_PARENT"]),
        "runtime_customization_package_pointer_count": len(rcp_pointers),
        "mapped_pointer_count": len(covered_by_status["MAPPED"]),
        "derived_pointer_count": len(covered_by_status["DERIVED"]),
        "deferred_pointer_count": len(covered_by_status["DEFERRED"]),
        "silently_dropped_fields": silently_dropped,
        "coverage_pct": round(100.0 * covered / total, 2) if total > 0 else 100.0,
        "status": "PASS" if not silently_dropped else "FAIL",
    }

    if write:
        _ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        _COVERAGE_OUT.write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[W4] Coverage result written to {_COVERAGE_OUT}")
        if silently_dropped:
            print(
                f"[W4] FAIL — {len(silently_dropped)} silently dropped fields: "
                + ", ".join(silently_dropped[:10])
                + ("..." if len(silently_dropped) > 10 else "")
            )
        else:
            print(
                f"[W4] PASS — {covered}/{total} pointers covered "
                f"({result['coverage_pct']}%)"
            )

    return result


def verify_runtime_customization_package_in_schema(
    schema: dict[str, Any] | None = None,
) -> bool:
    """Return True iff runtime_customization_package appears as a property in the schema."""
    if schema is None:
        schema = generate_schema(write=False)
    return "runtime_customization_package" in schema.get("properties", {})


def verify_derived_receipts(field_map: dict[str, Any] | None = None) -> dict[str, bool]:
    """Verify that derived fields have explicit receipts in the field map.

    Required derived fields: payload_digest, package_digest (under rcp).
    """
    if field_map is None:
        field_map = _load_field_map()
    mappings = field_map.get("mappings", {})

    receipts = {
        "/payload_digest": False,
        "/runtime_customization_package/package_digest": False,
    }
    for pointer, required in receipts.items():
        entry = mappings.get(pointer, {})
        if entry.get("status") in ("DERIVED", "MAPPED") and entry.get("reason"):
            receipts[pointer] = True

    return receipts


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="W4: apps_lic ingress contract schema + field-map coverage verification"
    )
    parser.add_argument(
        "--generate-schema",
        action="store_true",
        help="Generate JSON Schema from Pydantic model and write to artifacts/",
    )
    parser.add_argument(
        "--check-coverage",
        action="store_true",
        help="Check field-map coverage against the schema",
    )
    args = parser.parse_args()

    run_all = not (args.generate_schema or args.check_coverage)

    schema: dict[str, Any] | None = None
    if run_all or args.generate_schema:
        schema = generate_schema(write=True)

    if run_all or args.check_coverage:
        result = check_coverage(schema=schema, write=True)
        if result["silently_dropped_fields"]:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
