#!/usr/bin/env python3
"""
V15 Coverage Scoreboard — Deterministic Phase Gate.

Reads v15_gap_analysis.json and computes A–E layer percentages and
status counts.  Returns exit code 1 if gate thresholds are not met
for the specified phase.

Usage:
    python v15_coverage_scoreboard.py --phase P0
    python v15_coverage_scoreboard.py --phase P1
    python v15_coverage_scoreboard.py --phase P3 --json

Phase thresholds:
    P0: FAIL == 0
    P1: D_RUNTIME_WIRED >= 80%
    P2: MISSING == 0
    P3: E_CI_ENFORCED >= 95% (excl. process-only §14)
    P4: COMPLIANT >= 87
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_GAP_JSON = Path("docs/reports/plans/v15_gap_analysis.json")

# Canonical layer keys — every sub-capability MUST use exactly these.
CANONICAL_LAYER_KEYS = frozenset(
    {
        "A_TYPES_DEFINED",
        "B_CONTRACT_ENFORCER",
        "C_TEST_COVERAGE",
        "D_RUNTIME_WIRED",
        "E_CI_ENFORCED",
    },
)


class SchemaValidationError(Exception):
    """Raised when gap JSON does not conform to canonical layer schema."""


def validate_sub_capability_schema(
    sub: dict,
    *,
    allow_legacy: bool = False,
) -> list[str]:
    """Validate a sub-capability's layer schema.

    Returns list of error strings (empty = valid).
    """
    errors: list[str] = []
    sub_id = sub.get("id", "?")
    layers = sub.get("layers")

    if layers is None:
        if sub.get("coverage") is not None and not allow_legacy:
            errors.append(
                f"{sub_id}: has legacy 'coverage' key but no 'layers'. "
                "Use --allow-legacy-schema or migrate to canonical 'layers'.",
            )
            return errors
        if sub.get("coverage") is not None and allow_legacy:
            layers = sub["coverage"]
        else:
            errors.append(f"{sub_id}: missing 'layers' key")
            return errors

    present = set(layers.keys())
    missing = CANONICAL_LAYER_KEYS - present
    extra = present - CANONICAL_LAYER_KEYS
    if missing:
        errors.append(f"{sub_id}: missing canonical layer keys: {sorted(missing)}")
    if extra:
        errors.append(f"{sub_id}: unexpected layer keys: {sorted(extra)}")
    return errors


# Phase gate thresholds
PHASE_GATES: dict[str, dict[str, object]] = {
    "P0": {"metric": "FAIL_count", "op": "==", "threshold": 0},
    "P1": {"metric": "D_RUNTIME_WIRED_pct", "op": ">=", "threshold": 80.0},
    "P2": {"metric": "MISSING_count", "op": "==", "threshold": 0},
    "P3": {"metric": "E_CI_ENFORCED_pct", "op": ">=", "threshold": 95.0},
    "P4": {"metric": "COMPLIANT_count", "op": ">=", "threshold": 87},
}


def load_gap_json(path: Path) -> dict:
    """Load and return parsed gap analysis JSON."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_scoreboard(
    data: dict,
    *,
    allow_legacy: bool = False,
) -> dict:
    """Compute A–E layer stats and status counts from gap JSON.

    Raises SchemaValidationError if any sub-capability has invalid schema
    and allow_legacy is False.
    """
    capabilities = data.get("capabilities", [])

    # Schema validation pass
    schema_errors: list[str] = []
    for cap in capabilities:
        for sub in cap.get("sub_capabilities", []):
            schema_errors.extend(
                validate_sub_capability_schema(sub, allow_legacy=allow_legacy),
            )
    if schema_errors:
        raise SchemaValidationError(
            f"{len(schema_errors)} schema error(s):\n" + "\n".join(f"  {e}" for e in schema_errors),
        )

    status_counts: dict[str, int] = {}
    layer_totals: dict[str, int] = dict.fromkeys(CANONICAL_LAYER_KEYS, 0)
    layer_true: dict[str, int] = dict.fromkeys(CANONICAL_LAYER_KEYS, 0)
    total_subs = 0

    for cap in capabilities:
        for sub in cap.get("sub_capabilities", []):
            total_subs += 1
            status = sub.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1

            layers = sub.get("layers")
            if layers is None and allow_legacy:
                layers = sub.get("coverage", {})
            if layers is None:
                layers = {}
            for layer_key in CANONICAL_LAYER_KEYS:
                layer_totals[layer_key] += 1
                if layers.get(layer_key, False):
                    layer_true[layer_key] += 1

    layer_pct: dict[str, float] = {}
    for k in layer_totals:
        if layer_totals[k] > 0:
            layer_pct[k] = round(100.0 * layer_true[k] / layer_totals[k], 2)
        else:
            layer_pct[k] = 0.0

    return {
        "total_sub_capabilities": total_subs,
        "by_status": status_counts,
        "by_layer": {
            k: {
                "true_count": layer_true[k],
                "total": layer_totals[k],
                "pct_complete": layer_pct[k],
            }
            for k in layer_totals
        },
        "FAIL_count": status_counts.get("FAIL", 0),
        "MISSING_count": status_counts.get("MISSING", 0),
        "COMPLIANT_count": status_counts.get("COMPLIANT", 0),
        "PARTIAL_count": status_counts.get("PARTIAL", 0),
        "D_RUNTIME_WIRED_pct": layer_pct.get("D_RUNTIME_WIRED", 0.0),
        "E_CI_ENFORCED_pct": layer_pct.get("E_CI_ENFORCED", 0.0),
    }


def check_gate(
    scoreboard: dict,
    phase: str,
    *,
    raw_data: dict | None = None,
) -> tuple[bool, str]:
    """Check if phase gate passes. Returns (passed, message).

    For P0: uses _p0_meta.evidence_fail_count from *raw_data* exclusively.
    Baseline-inherited FAIL counts are ignored for P0 gating.
    Raises SchemaValidationError if _p0_meta is missing for P0.
    """
    gate = PHASE_GATES.get(phase)
    if gate is None:
        return False, f"Unknown phase: {phase}"

    # P0 special path: evidence-only gating
    if phase == "P0":
        if raw_data is None:
            raise SchemaValidationError(
                "P0 gate requires raw_data (regenerated artifact) to read _p0_meta",
            )
        p0_meta = raw_data.get("_p0_meta")
        if p0_meta is None:
            raise SchemaValidationError(
                "P0 gate requires _p0_meta in regenerated artifact. Run v15_gap_regenerate_p0.py first.",
            )
        if "evidence_fail_count" not in p0_meta:
            raise SchemaValidationError(
                "P0 gate requires _p0_meta.evidence_fail_count. Regeneration script is outdated.",
            )
        actual = p0_meta["evidence_fail_count"]
        threshold = 0
        passed = actual == threshold
        status = "PASS" if passed else "FAIL"
        msg = (
            f"{status}: P0 gate — evidence_fail_count = {actual} "
            f"(threshold: == {threshold}, "
            f"evaluated_ids={p0_meta.get('evaluated_ids', '?')}, "
            f"source=evidence_only)"
        )
        return passed, msg

    # All other phases: use scoreboard metrics
    metric_name = gate["metric"]
    op = gate["op"]
    threshold = gate["threshold"]
    actual = scoreboard.get(metric_name, None)

    if actual is None:
        return False, f"Metric '{metric_name}' not found in scoreboard"

    if op == "==":
        passed = actual == threshold
    elif op == ">=":
        passed = actual >= threshold
    elif op == "<=":
        passed = actual <= threshold
    else:
        return False, f"Unknown operator: {op}"

    status = "PASS" if passed else "FAIL"
    msg = f"{status}: {phase} gate — {metric_name} = {actual} (threshold: {op} {threshold})"
    return passed, msg


def main() -> int:
    parser = argparse.ArgumentParser(description="V15 Coverage Scoreboard")
    parser.add_argument(
        "--phase",
        required=True,
        choices=list(PHASE_GATES.keys()),
        help="Phase to check gate for",
    )
    parser.add_argument(
        "--gap-json",
        type=Path,
        default=None,
        help="Path to v15_gap_analysis.json (default: auto-detect)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--allow-legacy-schema",
        action="store_true",
        dest="allow_legacy",
        help="Accept legacy 'coverage' key instead of canonical 'layers'",
    )
    args = parser.parse_args()

    # Resolve gap JSON path
    gap_path = args.gap_json
    if gap_path is None:
        # Try relative to script, then relative to cwd
        script_root = Path(__file__).resolve().parents[2]
        gap_path = script_root / DEFAULT_GAP_JSON
        if not gap_path.exists():
            gap_path = Path.cwd() / DEFAULT_GAP_JSON

    if not gap_path.exists():
        print(f"ERROR: Gap analysis JSON not found at {gap_path}", file=sys.stderr)
        return 1

    data = load_gap_json(gap_path)
    try:
        scoreboard = compute_scoreboard(data, allow_legacy=args.allow_legacy)
        passed, message = check_gate(scoreboard, args.phase, raw_data=data)
    except SchemaValidationError as exc:
        print(f"SCHEMA ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json_output:
        output = {
            "phase": args.phase,
            "passed": passed,
            "message": message,
            "scoreboard": scoreboard,
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("V15 Coverage Scoreboard")
        print("=" * 60)
        print(f"Total sub-capabilities: {scoreboard['total_sub_capabilities']}")
        print()
        print("Status counts:")
        for status, count in sorted(scoreboard["by_status"].items()):
            print(f"  {status}: {count}")
        print()
        print("Layer coverage:")
        for layer, info in scoreboard["by_layer"].items():
            print(f"  {layer}: {info['true_count']}/{info['total']} ({info['pct_complete']}%)")
        print()
        print("-" * 60)
        print(message)
        print("-" * 60)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
