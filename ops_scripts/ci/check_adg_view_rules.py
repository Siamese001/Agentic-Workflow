#!/usr/bin/env python3
"""Manifest view-rule executor for the ADG three-graph harness.

Plan: ``.claude/plans/adg-three-graph-harness-e57cc7.md`` (W3.P1).

Executes a single ``view_rule`` block from
``ops_scripts/ci/adg_gate_manifest.yaml`` against the latest static ADG
snapshot. View rules are simple SQL-backed assertions that don't justify a
dedicated check_*.py script — count floors, scalar matches, regex assertions
on a single value.

Supported rule kinds
--------------------
``scalar`` — execute a SELECT that returns a single column from a single row,
then assert one or more of:

    expect:        <value>     — exact match
    expect_min:    <int|float> — value must be >= this
    expect_max:    <int|float> — value must be <= this
    expect_regex:  <pattern>   — regex.search must match str(value)
    expect_in:     [v1, v2]    — value must be in the list

Output
------
Emits a normalized GateResult (per agentic_core.adg.ci.gate_result) to
stdout JSON when ``--json-out`` is specified, and prints a one-liner.
Exit 0 on PASS, 1 on FAIL, 0 on SKIP.

Usage
-----
    python ops_scripts/ci/check_adg_view_rules.py --gate-id static.mv_count_floor
    python ops_scripts/ci/check_adg_view_rules.py --gate-id static.no_null_triplet --strict
    python ops_scripts/ci/check_adg_view_rules.py --list  # show all view-rule gates
"""

from __future__ import annotations

# Reads SQLite directly via manifest-defined SQL. Mode is determined per-gate
# by manifest evidence_mode field.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.ci.gate_result import GateResult  # noqa: E402

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "adg"
MANIFEST_PATH = REPO_ROOT / "ops_scripts" / "ci" / "adg_gate_manifest.yaml"


def _latest_snapshot() -> Path | None:
    """Return the latest ADG SQLite snapshot via canonical resolver."""
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


def _load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"manifest not found at {MANIFEST_PATH}")
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


def _find_gate(manifest: dict[str, Any], gate_id: str) -> dict[str, Any]:
    for gate in manifest.get("gates", []):
        if gate.get("gate_id") == gate_id:
            return gate
    raise KeyError(f"gate_id {gate_id!r} not in manifest")


def _execute_scalar(
    snapshot: Path, sql: str
) -> tuple[Any | None, str | None]:
    """Run sql, return (scalar_value, error_or_None)."""
    try:
        con = sqlite3.connect(str(snapshot))
        try:
            cur = con.execute(sql)
            row = cur.fetchone()
        finally:
            con.close()
    except sqlite3.Error as exc:
        return None, f"sqlite_error: {exc}"
    if row is None:
        return None, "no_rows_returned"
    if len(row) > 1:
        return None, f"scalar_rule_returned_{len(row)}_columns_expected_1"
    return row[0], None


def _evaluate_scalar(
    value: Any, rule: dict[str, Any]
) -> tuple[bool, str]:
    """Apply expect_* assertions; return (ok, fail_reason)."""
    if "expect" in rule:
        expected = rule["expect"]
        if value != expected:
            return False, f"value={value!r} != expect={expected!r}"
    if "expect_min" in rule:
        if value is None:
            return False, "value_is_None_expect_min"
        try:
            if float(value) < float(rule["expect_min"]):
                return False, f"value={value} < expect_min={rule['expect_min']}"
        except (TypeError, ValueError):
            return False, f"value_not_numeric: {value!r}"
    if "expect_max" in rule:
        if value is None:
            return False, "value_is_None_expect_max"
        try:
            if float(value) > float(rule["expect_max"]):
                return False, f"value={value} > expect_max={rule['expect_max']}"
        except (TypeError, ValueError):
            return False, f"value_not_numeric: {value!r}"
    if "expect_regex" in rule:
        pattern = rule["expect_regex"]
        if not re.search(pattern, str(value)):
            return False, f"value={value!r} does not match expect_regex={pattern!r}"
    if "expect_in" in rule:
        if value not in rule["expect_in"]:
            return False, f"value={value!r} not in expect_in={rule['expect_in']}"
    return True, ""


def run_gate(
    gate: dict[str, Any], snapshot: Path | None, *, strict: bool = False
) -> GateResult:
    """Execute one manifest gate; return a finalized GateResult."""
    started = datetime.now(timezone.utc)
    snap_id = snapshot.stem if snapshot else ""

    base = {
        "gate_id": str(gate["gate_id"]),
        "bucket": str(gate["bucket"]),
        "evidence_mode": str(gate.get("evidence_mode", "inventory")),
        "enforcement_mode": str(gate.get("enforcement_mode", "advisory")),
        "snapshot_id": snap_id,
        "input_refs": list(gate.get("reads") or []),
    }

    rule = gate.get("view_rule")
    if not rule:
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason="manifest gate has no view_rule",
        ).finalize()

    if snapshot is None or not snapshot.exists():
        return GateResult(**base, status="SKIP", actual_fail_reason="").finalize()

    kind = str(rule.get("kind", "scalar"))
    if kind != "scalar":
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=f"unsupported view_rule kind: {kind}",
        ).finalize()

    sql = str(rule.get("sql", "")).strip()
    if not sql:
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason="view_rule.sql is empty",
        ).finalize()

    value, err = _execute_scalar(snapshot, sql)
    duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    if err:
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=err,
            counts={},
            duration_ms=duration_ms,
        ).finalize()

    ok, reason = _evaluate_scalar(value, rule)
    counts = {"observed_value": _coerce_int(value)} if value is not None else {}

    if ok:
        status = "PASS"
        actual_fail = ""
    else:
        # Status depends on enforcement_mode + strict.
        enforcement = base["enforcement_mode"]
        if enforcement == "advisory" and not strict:
            status = "WARN"
            actual_fail = ""
        else:
            status = "FAIL"
            actual_fail = reason

    return GateResult(
        **base,
        status=status,
        actual_fail_reason=actual_fail,
        counts=counts,
        sample_failures=[{"value": _safe_jsonable(value), "reason": reason}] if not ok else [],
        thresholds={
            k: rule[k]
            for k in ("expect", "expect_min", "expect_max", "expect_regex", "expect_in")
            if k in rule
        },
        duration_ms=duration_ms,
    ).finalize()


def _coerce_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _safe_jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gate-id",
        type=str,
        default=None,
        help="manifest gate_id to execute (must be a view_rule gate)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list all view_rule gates in the manifest and exit",
    )
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        manifest = _load_manifest()
    except FileNotFoundError as exc:
        print(f"[view_rules] ERROR: {exc}")
        return 2

    if args.list:
        rule_gates = [g for g in manifest["gates"] if "view_rule" in g]
        print(f"[view_rules] {len(rule_gates)} view-rule gates in manifest:")
        for g in rule_gates:
            print(f"  - {g['gate_id']:<50} bucket={g['bucket']}")
        return 0

    if not args.gate_id:
        print("[view_rules] ERROR: --gate-id required (or --list)")
        return 2

    try:
        gate = _find_gate(manifest, args.gate_id)
    except KeyError as exc:
        print(f"[view_rules] ERROR: {exc}")
        return 2

    snapshot = args.snapshot or _latest_snapshot()
    result = run_gate(gate, snapshot, strict=args.strict)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(result.to_json(), indent=2), encoding="utf-8"
        )
    else:
        print(json.dumps(result.to_json(), indent=2))

    print(
        f"[view_rules] gate={result.gate_id} status={result.status} "
        f"reason={result.actual_fail_reason or '-'}"
    )

    if result.status == "FAIL":
        return 1
    if result.status == "ERROR":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
