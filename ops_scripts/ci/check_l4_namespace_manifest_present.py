"""CI gate: check_l4_namespace_manifest_present.py

Plan 03 W5.5 — Verify apps_rg L4 namespace manifest exists and has 10 surfaces.
Validates manifest shape against embedded schema rules.

Fail-closed via: APPS_RG_L4_MANIFEST_GATE_FAIL_CLOSED=1
Bypass via:      APPS_RG_L4_MANIFEST_GATE_BYPASS=1
Report:          artifacts/ci/apps_rg_l4_manifest_gate.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_PATH = REPO_ROOT / "apps_rg" / "config" / "l4_namespace_manifest.yaml"
REQUIRED_SURFACE_COUNT = 10
REQUIRED_APP_ID = "apps_rg"
REQUIRED_SURFACE_FIELDS = {
    "surface_id",
    "surface_type",
    "schema_version",
    "acl_profile",
    "replay_key_pattern",
    "retention_policy",
    "mutation_requires_uwg",
    "read_allowed",
    "write_allowed",
}
VALID_SURFACE_TYPES = {"cache", "vector_index", "filesystem", "in_memory", "telemetry"}


def _load_yaml_simple(path: Path) -> dict:
    """Minimal YAML loader for simple key:value and list structures — no PyYAML dependency."""
    try:
        import yaml  # type: ignore[import]
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)  # type: ignore[no-any-return]
    except ImportError:
        pass
    # Fallback: best-effort line parser for validation
    raise RuntimeError("PyYAML not available; install pyyaml or ensure it is in requirements")


def _validate_manifest(data: dict) -> list[dict]:
    errors: list[dict] = []

    if "l4_namespace" not in data:
        errors.append({"field": "l4_namespace", "error": "Root key 'l4_namespace' missing"})
        return errors

    ns = data["l4_namespace"]

    app_id = ns.get("app_id", "")
    if app_id != REQUIRED_APP_ID:
        errors.append({"field": "app_id", "error": f"Expected '{REQUIRED_APP_ID}', got '{app_id}'"})

    if not ns.get("version"):
        errors.append({"field": "version", "error": "version is required"})

    surfaces = ns.get("surfaces", [])
    if not isinstance(surfaces, list):
        errors.append({"field": "surfaces", "error": "surfaces must be a list"})
        return errors

    if len(surfaces) < REQUIRED_SURFACE_COUNT:
        errors.append({
            "field": "surfaces",
            "error": f"Expected >= {REQUIRED_SURFACE_COUNT} surfaces, found {len(surfaces)}",
        })

    surface_ids: set[str] = set()
    for i, surface in enumerate(surfaces):
        sid = surface.get("surface_id", f"<unknown_{i}>")
        if sid in surface_ids:
            errors.append({"field": f"surfaces[{i}].surface_id", "error": f"Duplicate surface_id '{sid}'"})
        surface_ids.add(sid)

        for field in REQUIRED_SURFACE_FIELDS:
            if field not in surface:
                errors.append({"field": f"surfaces[{i}].{field}", "error": f"Required field '{field}' missing in surface '{sid}'"})

        stype = surface.get("surface_type", "")
        if stype and stype not in VALID_SURFACE_TYPES:
            errors.append({
                "field": f"surfaces[{i}].surface_type",
                "error": f"Invalid surface_type '{stype}', must be one of {sorted(VALID_SURFACE_TYPES)}",
            })

    return errors


def main() -> int:
    bypass = os.environ.get("APPS_RG_L4_MANIFEST_GATE_BYPASS", "0") == "1"
    fail_closed = os.environ.get("APPS_RG_L4_MANIFEST_GATE_FAIL_CLOSED", "0") == "1"

    if bypass:
        print("BYPASS_RECEIPT: gate=check_l4_namespace_manifest_present reason=APPS_RG_L4_MANIFEST_GATE_BYPASS=1")
        return 0

    violations: list[dict] = []

    if not MANIFEST_PATH.exists():
        violations.append({
            "field": "manifest_file",
            "error": f"L4 namespace manifest not found at {MANIFEST_PATH.relative_to(REPO_ROOT)}",
        })
    else:
        try:
            data = _load_yaml_simple(MANIFEST_PATH)
            violations.extend(_validate_manifest(data))
            surface_count = len(data.get("l4_namespace", {}).get("surfaces", []))
        except Exception as exc:
            violations.append({"field": "manifest_parse", "error": str(exc)})
            surface_count = 0

    report = {
        "gate": "check_l4_namespace_manifest_present",
        "manifest_path": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
        "manifest_exists": MANIFEST_PATH.exists(),
        "violation_count": len(violations),
        "violations": violations,
    }

    out_dir = REPO_ROOT / "artifacts" / "ci"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "apps_rg_l4_manifest_gate.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if violations:
        print(f"[APPS-L4-MANIFEST] ERROR: {len(violations)} manifest violation(s)")
        for v in violations:
            print(f"  {v['field']}: {v['error']}")
        if fail_closed:
            return 1
        print("[APPS-L4-MANIFEST] Advisory mode — set APPS_RG_L4_MANIFEST_GATE_FAIL_CLOSED=1 to enforce")
        return 0

    print(f"[APPS-L4-MANIFEST] OK — manifest valid at {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
