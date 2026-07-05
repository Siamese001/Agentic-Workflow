#!/usr/bin/env python3
"""Validate the apps_rg L6 observability registry contract.

This guard is intentionally registry-only. It proves that the apps_eval
microstep registry, artifact-role registry, and L6 evidence-class enum agree
before a runtime/eval lane tries to consume them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = REPO_ROOT / "apps_eval" / "registries"
ARTIFACT_CONTRACT = REGISTRY_DIR / "apps_rg_artifact_contract.json"
MICROSTEP_CONTRACT = REGISTRY_DIR / "apps_rg_stage_microstep_contract.json"
LANE_CONTRACT = REGISTRY_DIR / "apps_rg_lane_contract.json"

EXPECTED_EVIDENCE_CLASSES = {
    "CONTRACT_ONLY_ADVISORY",
    "APPS_EVAL_BOUND_PROOF",
    "FAILURE_TERMINAL_ADVISORY",
}


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _rows(microstep_contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(dict(row) for row in microstep_contract.get("global_microsteps", []))
    rows.extend(dict(row) for row in microstep_contract.get("cross_run_microsteps", []))
    for template in microstep_contract.get("lane_microstep_templates", []):
        row = dict(template)
        row["microstep_id"] = str(row.get("microstep_id_template") or "")
        rows.append(row)
    return rows


def _validate_roles(
    rows: list[Mapping[str, Any]],
    artifact_roles: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    known_roles = set(artifact_roles)
    for row in rows:
        role = str(row.get("artifact_role") or "")
        microstep_id = str(row.get("microstep_id") or row.get("microstep_id_template") or "<missing>")
        if role not in known_roles:
            issues.append(f"unknown artifact_role {role!r} on microstep {microstep_id}")
    return issues


def _validate_l6_microsteps(rows: list[Mapping[str, Any]]) -> list[str]:
    issues: list[str] = []
    required_fields = ("required", "severity", "artifact_role", "gate_id")
    for row in rows:
        if str(row.get("stage_id") or "") != "L6":
            continue
        microstep_id = str(row.get("microstep_id") or row.get("microstep_id_template") or "<missing>")
        missing = [field for field in required_fields if row.get(field) in (None, "")]
        if missing:
            issues.append(f"L6 microstep {microstep_id} missing fields: {', '.join(missing)}")
    return issues


def _validate_package_semantics(artifact_roles: Mapping[str, Any]) -> list[str]:
    issues: list[str] = []
    legacy = artifact_roles.get("lane_l6_shadow_eval_package")
    governed = artifact_roles.get("l6_v40_shadow_eval_package")
    if not isinstance(legacy, Mapping):
        issues.append("lane_l6_shadow_eval_package role is missing")
        return issues
    if not isinstance(governed, Mapping):
        issues.append("l6_v40_shadow_eval_package role is missing")
        return issues
    if legacy.get("source_artifact_schema") == governed.get("source_artifact_schema"):
        issues.append("legacy lane package and governed v40 package must use distinct schemas")
    if legacy.get("required") is not True:
        issues.append("lane_l6_shadow_eval_package must remain required lane evidence")
    if governed.get("required") is not False:
        issues.append("l6_v40_shadow_eval_package must remain optional governed L6 evidence")
    legacy_paths = set(str(path) for path in legacy.get("relative_paths", []))
    governed_paths = set(str(path) for path in governed.get("relative_paths", []))
    overlap = sorted(legacy_paths & governed_paths)
    if overlap:
        issues.append(f"legacy and governed package relative paths overlap: {overlap}")
    return issues


def _validate_trace_advisory(
    rows: list[Mapping[str, Any]],
    artifact_roles: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    trace_role = artifact_roles.get("trace_reconciliation")
    if not isinstance(trace_role, Mapping):
        return ["trace_reconciliation role is missing"]
    if trace_role.get("required") is not False:
        issues.append("trace_reconciliation artifact role must remain optional")
    for row in rows:
        if str(row.get("artifact_role") or "") != "trace_reconciliation":
            continue
        microstep_id = str(row.get("microstep_id") or "<missing>")
        if row.get("required") is not False:
            issues.append(f"{microstep_id} must remain advisory required=false")
        if str(row.get("severity") or "") != "WARN":
            issues.append(f"{microstep_id} must remain WARN severity")
        if "x3" in str(row.get("gate_id") or "").lower():
            issues.append(f"{microstep_id} must not masquerade as an X3 runtime gate")
    return issues


def _validate_evidence_classes(microstep_contract: Mapping[str, Any]) -> list[str]:
    from agentic_core.L6_observability.shadow_eval.microsteps import EVIDENCE_CLASSES

    registry_classes = set(str(item) for item in microstep_contract.get("evidence_class_enum", []))
    observed = set(EVIDENCE_CLASSES)
    if registry_classes != EXPECTED_EVIDENCE_CLASSES:
        return [
            "registry evidence class enum mismatch: "
            f"expected={sorted(EXPECTED_EVIDENCE_CLASSES)} observed={sorted(registry_classes)}"
        ]
    if observed != EXPECTED_EVIDENCE_CLASSES:
        return [f"evidence class enum mismatch: expected={sorted(EXPECTED_EVIDENCE_CLASSES)} observed={sorted(observed)}"]
    return []


def validate_contract() -> dict[str, Any]:
    artifact_contract = _load_json(ARTIFACT_CONTRACT)
    microstep_contract = _load_json(MICROSTEP_CONTRACT)
    _load_json(LANE_CONTRACT)
    artifact_roles = artifact_contract.get("artifact_roles", {})
    if not isinstance(artifact_roles, Mapping):
        raise ValueError("artifact_contract.artifact_roles must be an object")
    rows = _rows(microstep_contract)
    issues: list[str] = []
    issues.extend(_validate_roles(rows, artifact_roles))
    issues.extend(_validate_l6_microsteps(rows))
    issues.extend(_validate_package_semantics(artifact_roles))
    issues.extend(_validate_trace_advisory(rows, artifact_roles))
    issues.extend(_validate_evidence_classes(microstep_contract))
    return {
        "status": "PASS" if not issues else "FAIL",
        "issue_count": len(issues),
        "issues": issues,
        "microstep_rows_checked": len(rows),
        "artifact_roles_checked": len(artifact_roles),
        "evidence_classes": sorted(EXPECTED_EVIDENCE_CLASSES),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()
    payload = validate_contract()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"apps_rg L6 observability contract: {payload['status']}")
        for issue in payload["issues"]:
            print(f"- {issue}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
