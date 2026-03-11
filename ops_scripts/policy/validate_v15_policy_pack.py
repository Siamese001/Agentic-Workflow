"""V15 Policy Pack Validator.

Validates a V15 policy pack JSON file against the required schema,
checks for duplicate rule_ids, and warns on unknown fields.

Usage:
    python ops_scripts/policy/validate_v15_policy_pack.py --path <policy_pack.json>

Exit codes:
    0 — Valid policy pack
    2 — Schema validation failure (missing/bad fields)
    3 — Duplicate rule_id detected
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.L0_routing.types.integration_contract_types import (
    Finding,
    ResultEnvelope,
)

# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

VALID_APPLIES_TO = frozenset({"PIPE", "POLICY", "HASH", "CLOCK", "GENERAL"})
VALID_SEVERITY = frozenset({"WARN", "SOFT_FAIL", "HARD_FAIL"})

REQUIRED_TOP_LEVEL = {"version", "rules"}
REQUIRED_RULE_FIELDS = {"rule_id", "applies_to", "severity", "description", "enabled"}

KNOWN_TOP_LEVEL = REQUIRED_TOP_LEVEL | {"updated_at"}
KNOWN_RULE_FIELDS = REQUIRED_RULE_FIELDS | {"metadata"}


# ---------------------------------------------------------------------------
# Validation core (importable for tests)
# ---------------------------------------------------------------------------


def validate_policy_pack(data: dict) -> tuple[int, list[str], list[str]]:
    """Validate a parsed policy pack dict.

    Returns:
        (exit_code, errors, warnings)
        exit_code: 0=ok, 2=schema, 3=duplicates
    """
    errors: list[str] = []
    warnings: list[str] = []

    # --- Top-level required fields ---
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in data:
            errors.append(f"Missing required top-level field: '{field}'")

    if errors:
        return 2, errors, warnings

    # --- Top-level unknown fields ---
    for key in sorted(data.keys()):
        if key not in KNOWN_TOP_LEVEL:
            warnings.append(f"Unknown top-level field: '{key}' (forward-compat, ignored)")

    # --- version ---
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append("'version' must be a non-empty string")

    # --- rules ---
    rules = data.get("rules")
    if not isinstance(rules, list):
        errors.append("'rules' must be a list")
        return 2, errors, warnings

    if len(rules) == 0:
        errors.append("'rules' must contain at least one rule")
        return 2, errors, warnings

    # --- Per-rule validation ---
    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []

    for idx, rule in enumerate(rules):
        prefix = f"rules[{idx}]"

        if not isinstance(rule, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        # Required fields
        for field in sorted(REQUIRED_RULE_FIELDS):
            if field not in rule:
                errors.append(f"{prefix}: missing required field '{field}'")

        # Unknown rule fields
        for key in sorted(rule.keys()):
            if key not in KNOWN_RULE_FIELDS:
                warnings.append(f"{prefix}: unknown field '{key}' (forward-compat, ignored)")

        # Type checks
        rule_id = rule.get("rule_id")
        if rule_id is not None:
            if not isinstance(rule_id, str) or not rule_id.strip():
                errors.append(f"{prefix}: 'rule_id' must be a non-empty string")
            else:
                if rule_id in seen_ids:
                    duplicate_ids.append(rule_id)
                seen_ids.add(rule_id)

        applies_to = rule.get("applies_to")
        if applies_to is not None and applies_to not in VALID_APPLIES_TO:
            errors.append(
                f"{prefix}: 'applies_to' must be one of {sorted(VALID_APPLIES_TO)}, got '{applies_to}'",
            )

        severity = rule.get("severity")
        if severity is not None and severity not in VALID_SEVERITY:
            errors.append(
                f"{prefix}: 'severity' must be one of {sorted(VALID_SEVERITY)}, got '{severity}'",
            )

        description = rule.get("description")
        if description is not None and not isinstance(description, str):
            errors.append(f"{prefix}: 'description' must be a string")

        enabled = rule.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            errors.append(f"{prefix}: 'enabled' must be a boolean")

    # --- Duplicate check (separate exit code) ---
    if duplicate_ids:
        for dup in sorted(set(duplicate_ids)):
            errors.append(f"Duplicate rule_id: '{dup}'")
        return 3, errors, warnings

    if errors:
        return 2, errors, warnings

    # --- Ordering recommendation ---
    rule_ids = [r.get("rule_id", "") for r in rules if isinstance(r, dict)]
    if rule_ids != sorted(rule_ids):
        warnings.append("Rules are not sorted by rule_id (recommended for stable diffs)")

    return 0, errors, warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_validator_envelope(
    pack_path: str,
    exit_code: int,
    errors: list[str],
    warnings: list[str],
) -> ResultEnvelope:
    """Build a ResultEnvelope for the policy pack validator run."""
    env = ResultEnvelope(tool="policy_pack_validator", exit_code=exit_code)
    env.inputs["policy_pack"] = {
        "path": Path(pack_path).name,
        "present": Path(pack_path).is_file(),
    }

    for w in warnings:
        env.findings.append(
            Finding(
                code="SCHEMA_WARN",
                severity="WARN",
                message=w,
            ),
        )
    for e in errors:
        env.findings.append(
            Finding(
                code="SCHEMA_ERROR" if exit_code == 2 else "DUPLICATE_RULE_ID",
                severity="ERROR",
                message=e,
            ),
        )

    return env


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a V15 policy pack JSON file.")
    parser.add_argument("--path", type=str, required=True, help="Path to policy pack JSON")
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Optional: write JSON result envelope to this path",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_file():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        env = build_validator_envelope(args.path, 2, [f"File not found: {path.name}"], [])
        if args.json_out:
            env.write_json(Path(args.json_out))
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        env = build_validator_envelope(args.path, 2, [f"Invalid JSON: {e}"], [])
        if args.json_out:
            env.write_json(Path(args.json_out))
        return 2

    if not isinstance(data, dict):
        print("ERROR: Top-level must be a JSON object", file=sys.stderr)
        env = build_validator_envelope(args.path, 2, ["Top-level must be a JSON object"], [])
        if args.json_out:
            env.write_json(Path(args.json_out))
        return 2

    exit_code, errors, warnings = validate_policy_pack(data)

    for w in warnings:
        print(f"WARN: {w}")

    if exit_code == 0:
        rule_count = len(data.get("rules", []))
        print(f"PASS: Policy pack v{data.get('version', '?')} — {rule_count} rules valid")
    else:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)

    if args.json_out:
        env = build_validator_envelope(args.path, exit_code, errors, warnings)
        env.write_json(Path(args.json_out))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
