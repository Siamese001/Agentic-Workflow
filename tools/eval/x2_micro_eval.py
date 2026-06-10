"""X2 micro-eval fixture harness.

This module validates deterministic X2 hard-line fixture results. It is a
meta-harness: product validators still own the gate logic, while fixtures record
which gate outputs a hard-line case must produce.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal


REQUIRED_FAMILIES: tuple[str, ...] = (
    "numeric_precision",
    "sentence_boundaries",
    "leakage_self_check_separation",
    "unknown_hard_lines",
    "mock_not_allowed",
)

ExpectedDisposition = Literal["ALLOW", "BLOCK"]


@dataclass(frozen=True, slots=True)
class X2GateObservation:
    gate_id: str
    passed: bool
    severity: Literal["hard", "warn"]
    detail: str = ""


@dataclass(frozen=True, slots=True)
class X2MicroEvalResult:
    fixture_id: str
    family: str
    expected_disposition: str
    observed_disposition: str
    passed: bool
    reason_codes: list[str]
    hard_failed_gate_ids: list[str]


@dataclass(frozen=True, slots=True)
class X2MicroEvalSuiteResult:
    passed: bool
    fixture_count: int
    missing_required_families: list[str]
    results: list[X2MicroEvalResult]


def _require_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _load_gate(raw: Any) -> X2GateObservation:
    if not isinstance(raw, dict):
        raise ValueError("gate observations must be objects")
    severity = raw.get("severity", "hard")
    if severity not in ("hard", "warn"):
        raise ValueError("gate severity must be hard or warn")
    if "pass" in raw:
        passed = bool(raw["pass"])
    elif "passed" in raw:
        passed = bool(raw["passed"])
    else:
        raise ValueError("gate observation must include pass or passed")
    return X2GateObservation(
        gate_id=_require_text(raw, "gate_id"),
        passed=passed,
        severity=severity,
        detail=str(raw.get("detail") or ""),
    )


def evaluate_fixture(payload: dict[str, Any]) -> X2MicroEvalResult:
    fixture_id = _require_text(payload, "fixture_id")
    family = _require_text(payload, "family")
    expected = _require_text(payload, "expected_disposition").upper()
    if family not in REQUIRED_FAMILIES:
        raise ValueError(f"unknown X2 fixture family: {family}")
    if expected not in ("ALLOW", "BLOCK"):
        raise ValueError("expected_disposition must be ALLOW or BLOCK")

    gates_raw = payload.get("gate_observations")
    if not isinstance(gates_raw, list):
        raise ValueError("gate_observations must be a list")
    gates = [_load_gate(g) for g in gates_raw]
    required_gate_ids = {str(g) for g in payload.get("required_gate_ids") or []}
    observed_gate_ids = {g.gate_id for g in gates}
    hard_failed = [g.gate_id for g in gates if g.severity == "hard" and not g.passed]
    observed = "BLOCK" if hard_failed else "ALLOW"

    reasons: list[str] = []
    missing = sorted(required_gate_ids - observed_gate_ids)
    if missing:
        reasons.append("REQUIRED_GATES_MISSING:" + ",".join(missing))
    if expected == "BLOCK" and observed != "BLOCK":
        reasons.append("EXPECTED_BLOCK_NOT_TRIGGERED")
    if expected == "ALLOW" and observed != "ALLOW":
        reasons.append("UNEXPECTED_HARD_FAILURE")

    return X2MicroEvalResult(
        fixture_id=fixture_id,
        family=family,
        expected_disposition=expected,
        observed_disposition=observed,
        passed=not reasons,
        reason_codes=reasons,
        hard_failed_gate_ids=hard_failed,
    )


def _load_fixture_file(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("fixtures"), list):
        return [f for f in payload["fixtures"] if isinstance(f, dict)]
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [f for f in payload if isinstance(f, dict)]
    raise ValueError(f"unsupported fixture JSON shape: {path}")


def load_fixtures(path: Path) -> list[dict[str, Any]]:
    if path.is_file():
        return _load_fixture_file(path)
    if not path.is_dir():
        raise ValueError(f"fixture path not found: {path}")
    fixtures: list[dict[str, Any]] = []
    for file_path in sorted(path.glob("*.json")):
        fixtures.extend(_load_fixture_file(file_path))
    return fixtures


def evaluate_suite(fixtures: list[dict[str, Any]]) -> X2MicroEvalSuiteResult:
    results = [evaluate_fixture(f) for f in fixtures]
    families = {r.family for r in results}
    missing = [family for family in REQUIRED_FAMILIES if family not in families]
    return X2MicroEvalSuiteResult(
        passed=not missing and all(r.passed for r in results),
        fixture_count=len(results),
        missing_required_families=missing,
        results=results,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=Path("data/eval/x2_micro"))
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        result = evaluate_suite(load_fixtures(args.fixtures))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[CONFIG_ERROR] {exc}", file=sys.stderr)
        return 2

    payload = asdict(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        print()
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
