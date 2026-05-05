"""CI gate — PublicTrustReceipt JSON schema validation for apps_underwriting_ai.

D5.2 — Schema validation gate.
Plan: apps-underwriting-ai-deferred-scope-e8b2f4 D5.2.

Validates:
  1. The JSON Schema file exists and parses cleanly.
  2. The schema declares all 15 required fields from the PublicTrustReceipt dataclass.
  3. demo_mode is declared as required and constrained to const: true.
  4. Each demo fixture's expected PublicTrustReceipt shape (synthesised from
     fixture fields) validates against the schema.

Runs in < 2 seconds (no network, no LLM).

Exit codes:
  0 — all checks pass
  1 — one or more checks failed

Bypass: UNDERWRITING_PTR_SCHEMA_BYPASS=1
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = (
    REPO_ROOT / "apps_underwriting_ai" / "schemas" / "public_trust_receipt.schema.json"
)
FIXTURE_DIR = REPO_ROOT / "apps_underwriting_ai" / "fixtures"

_REQUIRED_FIELDS = {
    "route_family",
    "underwriting_route_mode",
    "evidence_contract_status",
    "documents_received_count",
    "documents_missing_count",
    "contradiction_flags_count",
    "demo_scorer_version",
    "demo_policy_hash",
    "replay_key_prefix",
    "exit_disposition",
    "hitl_posture",
    "generated_rationale_used",
    "deterministic_rationale_fallback_used",
    "demo_packet_id",
    "demo_mode",
}

_FIXTURE_NAMES = [
    "demo_approve_packet.yaml",
    "demo_refer_packet.yaml",
    "demo_missing_evidence_packet.yaml",
    "demo_decline_packet.yaml",
]


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- CI gate must report, not crash
        print(f"  ERROR: cannot load JSON from {path}: {exc}")
        return None


def _load_yaml(path: Path) -> dict | None:
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- CI gate must report, not crash
        print(f"  ERROR: cannot load YAML from {path}: {exc}")
        return None


def _build_sample_ptr(fixture: dict) -> dict:
    """Build a minimal PublicTrustReceipt sample from fixture fields for validation."""
    c0 = fixture.get("expected_c0", {})
    submitted = fixture.get("submitted_documents", [])
    missing_flags = c0.get("missing_evidence_flags", [])
    contradiction_flags = c0.get("contradiction_flags", [])
    return {
        "route_family": "R3R4_MANAGED_WORKFLOW",
        "underwriting_route_mode": "FULL_DECISION_PACKET",
        "evidence_contract_status": c0.get("c0_state", "UNKNOWN"),
        "documents_received_count": len(submitted),
        "documents_missing_count": len(missing_flags),
        "contradiction_flags_count": len(contradiction_flags),
        "demo_scorer_version": "deterministic_risk_scorer_v1",
        "demo_policy_hash": fixture.get("demo_policy_hash", ""),
        "replay_key_prefix": "",
        "exit_disposition": "UNKNOWN",
        "hitl_posture": fixture.get("expected_hitl_posture", "HITL_NONE"),
        "generated_rationale_used": False,
        "deterministic_rationale_fallback_used": True,
        "demo_packet_id": fixture.get("demo_packet_id", ""),
        "demo_mode": True,
    }


def _validate_against_schema(instance: dict, schema: dict) -> list[str]:
    """Validate instance against schema using jsonschema if available, else manual check."""
    errors: list[str] = []
    try:
        import jsonschema  # noqa: PLC0415

        validator = jsonschema.Draft202012Validator(schema)
        for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
            errors.append(f"  schema_error: {err.message} (path: {list(err.path)})")
        return errors
    except ImportError:
        pass

    required = set(schema.get("required", []))
    missing = required - set(instance.keys())
    for key in sorted(missing):
        errors.append(f"  missing_required_field: {key}")

    props = schema.get("properties", {})
    demo_mode_prop = props.get("demo_mode", {})
    if "const" in demo_mode_prop and instance.get("demo_mode") != demo_mode_prop["const"]:
        errors.append(
            f"  demo_mode must be {demo_mode_prop['const']!r}; "
            f"got {instance.get('demo_mode')!r}"
        )
    return errors


def run_checks() -> list[str]:
    errors: list[str] = []

    if not SCHEMA_PATH.exists():
        return [f"MISSING_SCHEMA: {SCHEMA_PATH} not found"]

    schema = _load_json(SCHEMA_PATH)
    if schema is None:
        return ["PARSE_ERROR: schema JSON failed to load"]

    declared_required = set(schema.get("required", []))
    missing_from_schema = _REQUIRED_FIELDS - declared_required
    if missing_from_schema:
        errors.append(
            f"SCHEMA_MISSING_FIELDS: {sorted(missing_from_schema)} "
            "not listed in schema 'required'"
        )

    demo_mode_prop = schema.get("properties", {}).get("demo_mode", {})
    if demo_mode_prop.get("const") is not True:
        errors.append(
            "DEMO_MODE_NOT_CONST: schema must declare demo_mode with const: true"
        )

    for fname in _FIXTURE_NAMES:
        fpath = FIXTURE_DIR / fname
        if not fpath.exists():
            errors.append(f"MISSING_FIXTURE: {fname}")
            continue
        fixture = _load_yaml(fpath)
        if fixture is None:
            errors.append(f"FIXTURE_PARSE_ERROR: {fname}")
            continue
        sample_ptr = _build_sample_ptr(fixture)
        validation_errors = _validate_against_schema(sample_ptr, schema)
        for verr in validation_errors:
            errors.append(f"FIXTURE_VALIDATION_ERROR [{fname}]: {verr}")

    return errors


def main() -> int:
    if os.environ.get("UNDERWRITING_PTR_SCHEMA_BYPASS") == "1":
        print("WARNING: UNDERWRITING_PTR_SCHEMA_BYPASS=1 — gate bypassed.")
        return 0

    print(f"[check_underwriting_public_trust_receipt_schema] schema={SCHEMA_PATH.name}")
    errors = run_checks()

    if not errors:
        print(
            f"  OK: schema valid, all {len(_REQUIRED_FIELDS)} required fields declared, "
            f"all {len(_FIXTURE_NAMES)} fixture samples validate."
        )
        return 0

    for err in errors:
        print(f"  {err}")
    print(f"\n  FAIL: {len(errors)} error(s) found.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
