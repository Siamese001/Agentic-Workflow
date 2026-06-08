#!/usr/bin/env python3
"""
validate_deferred_scope_marker.py — Validate a DEFERRED_SCOPE marker string.

Standalone validator for the marker contract defined in
`.claude/rules/deferred-scope-capture.md`. Importable as a library and
runnable as a CLI. Used by:
  - pre-commit hook `ops_scripts/ci/check_deferred_scope_markers.py`
  - post-agent hook `post_agent_deferred_scope_capture.py` (duplicates logic)
  - manual marker authoring / audit

CLI:
    python -m tools.priority.validate_deferred_scope_marker \\
        --marker "DEFERRED_SCOPE: plan=foo wave=W1 phase=W1.1 layer=L5 fan_in=12 surface=Security coverage_gap_pct=85.4 est_tokens=12000 reason=example"

Exits 0 on valid, 2 on malformed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass

MARKER_PREFIX_RE = re.compile(r"^\s*DEFERRED_SCOPE:\s*(?P<body>.+?)\s*$", re.IGNORECASE)
KV_RE = re.compile(r"(\w+)=((?:\"[^\"]*\")|(?:\S+))")
REASON_RE = re.compile(r"reason=(.+?)(?:\s+(?:\w+)=|\s*$)", re.IGNORECASE)

REQUIRED_FIELDS: tuple[str, ...] = (
    "plan",
    "wave",
    "phase",
    "layer",
    "fan_in",
    "surface",
    "coverage_gap_pct",
    "est_tokens",
    "reason",
)

VALID_SURFACES = {"Execution", "Write", "Security", "State", "Observability", "None"}
VALID_LAYER_PREFIX = ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_")


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    fields: dict[str, str]
    errors: list[str]


def parse_marker(marker_line: str) -> dict[str, str]:
    """Parse a DEFERRED_SCOPE line into a kv dict. Returns {} if prefix missing."""
    match = MARKER_PREFIX_RE.match(marker_line)
    if not match:
        return {}
    body = match.group("body")

    fields: dict[str, str] = {}
    reason_match = REASON_RE.search(body)
    if reason_match:
        fields["reason"] = reason_match.group(1).strip().strip('"')
        body_without_reason = body[: reason_match.start()]
    else:
        body_without_reason = body

    for kv_match in KV_RE.finditer(body_without_reason):
        key = kv_match.group(1).lower()
        value = kv_match.group(2).strip('"')
        fields[key] = value

    return fields


def validate(marker_line: str) -> ValidationResult:
    """Validate a marker line. Returns ValidationResult with detailed errors."""
    fields = parse_marker(marker_line)
    errors: list[str] = []

    if not fields:
        errors.append("marker does not match DEFERRED_SCOPE: prefix pattern")
        return ValidationResult(valid=False, fields={}, errors=errors)

    # Required fields present
    missing = [f for f in REQUIRED_FIELDS if f not in fields]
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    # Type / range validation
    if "fan_in" in fields:
        try:
            fi = int(fields["fan_in"])
            if fi < 0:
                errors.append(f"fan_in must be >= 0, got {fi}")
        except ValueError:
            errors.append(f"fan_in must be integer, got '{fields['fan_in']}'")

    if "est_tokens" in fields:
        try:
            et = int(fields["est_tokens"])
            if et < 0:
                errors.append(f"est_tokens must be >= 0, got {et}")
        except ValueError:
            errors.append(f"est_tokens must be integer, got '{fields['est_tokens']}'")

    if "coverage_gap_pct" in fields:
        try:
            gp = float(fields["coverage_gap_pct"])
            if not 0.0 <= gp <= 100.0:
                errors.append(f"coverage_gap_pct must be 0.0-100.0, got {gp}")
        except ValueError:
            errors.append(f"coverage_gap_pct must be float, got '{fields['coverage_gap_pct']}'")

    if "layer" in fields:
        layer = fields["layer"].strip().upper()
        if not layer.startswith(VALID_LAYER_PREFIX):
            errors.append(f"layer must start with L0-L6 or L_, got '{fields['layer']}'")

    if "surface" in fields:
        surface = fields["surface"].strip()
        surface_norm = surface[0].upper() + surface[1:].lower() if surface else ""
        if surface_norm not in VALID_SURFACES:
            errors.append(f"surface must be one of {sorted(VALID_SURFACES)}, got '{surface}'")

    if "plan" in fields:
        plan = fields["plan"]
        if not plan or plan == "NEW:" or plan.startswith("(") or plan.endswith(")"):
            errors.append(f"plan must be a real slug or NEW:<slug>, got '{plan}'")

    if "reason" in fields and not fields["reason"].strip():
        errors.append("reason must not be empty")

    return ValidationResult(valid=not errors, fields=fields, errors=errors)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate_deferred_scope_marker",
        description="Validate a DEFERRED_SCOPE marker line against the schema.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--marker", help="Full marker line to validate")
    group.add_argument(
        "--stdin",
        action="store_true",
        help="Read one marker line from stdin",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON result instead of human-readable output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    marker_line = args.marker if args.marker else sys.stdin.readline().rstrip("\n")
    result = validate(marker_line)

    if args.json:
        print(
            json.dumps(
                {
                    "valid": result.valid,
                    "fields": result.fields,
                    "errors": result.errors,
                },
                indent=2,
            )
        )
    else:
        status = "VALID" if result.valid else "INVALID"
        print(f"{status}: {marker_line}")
        if result.fields:
            for k, v in sorted(result.fields.items()):
                print(f"  {k} = {v}")
        if result.errors:
            print("errors:")
            for e in result.errors:
                print(f"  - {e}")

    return 0 if result.valid else 2


if __name__ == "__main__":
    sys.exit(main())
