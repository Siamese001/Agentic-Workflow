#!/usr/bin/env python3
"""ADG Three-Graph Test Runner — manifest-driven harness.

Plan: ``.claude/plans/adg-three-graph-harness-e57cc7.md`` (W1.P3).

Loads ``ops_scripts/ci/adg_gate_manifest.yaml`` and runs every selected
gate in a deterministic order, normalizing each gate's output into the
``GateResult`` shape and emitting a single rollup JSON.

Execution lanes (always in this order)
--------------------------------------
0. preflight       — environmental sanity (snapshot present, schema_version)
1. static          — AST-extracted nodes/edges/mv_*/v_p* surface
2. registry        — registry-bucket edges + nodes + integrity checks
3. runtime         — v_runtime_proof + topology + semconv coverage
4. cross_bucket    — gap thresholds + impossible-states
5. provenance      — DSSE signature
6. schema          — graduation readiness
7. negative_controls — runs against tests/adg/fixtures/negative/ when
                       --suite=negative

Suites
------
quick    — preflight + a smoke subset across each bucket (fastest path)
full     — every gate with suite includes "full"
changed  — git-diff fan-in subset (config/adg_gate_fanin_map.yaml)
negative — runs every gate against the negative-control fixtures

Strict mode
-----------
``--strict`` flips the runner into fail-closed enforcement:
  * Any gate FAIL raises overall_status=FAIL
  * A detected bypass_env on any gate causes that gate to be re-marked
    FAIL (override) UNLESS the gate has ``allowed_to_skip: true``
  * Any gate ERROR raises overall_status=ERROR

Outputs
-------
Stdout: short per-gate one-liner + final summary block.
JSON  : one rollup file at ``--json-out`` (default
        ``docs/reports/adg/three_graph_test_rollup.json``).

Exit codes
----------
0 — overall_status in {PASS, WARN}
1 — overall_status == FAIL
2 — overall_status == ERROR (manifest malformed, missing snapshot, etc.)
"""

from __future__ import annotations

# Reads SQLite indirectly (via gates) and dispatches subprocesses.
__adg_consumer_mode__ = "inventory"

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.ci.gate_result import (  # noqa: E402
    GateResult,
    RollupResult,
    gate_result_from_dict,
)

ARTIFACT_DIR = REPO_ROOT / "artifacts" / "adg"
MANIFEST_PATH = REPO_ROOT / "ops_scripts" / "ci" / "adg_gate_manifest.yaml"
DEFAULT_ROLLUP = REPO_ROOT / "docs" / "reports" / "adg" / "three_graph_test_rollup.json"
VIEW_RULE_RUNNER = REPO_ROOT / "ops_scripts" / "ci" / "check_adg_view_rules.py"

LANE_ORDER = (
    "preflight",
    "static",
    "registry",
    "runtime",
    "cross_bucket",
    "provenance",
    "schema",
)
DEFAULT_TIMEOUT_S = 60


# ---------------------------------------------------------------------------
# Snapshot resolution
# ---------------------------------------------------------------------------


def resolve_snapshot(cli_path: Path | None) -> Path | None:
    """--snapshot wins; else $ADG_SNAPSHOT; else canonical latest resolver."""
    if cli_path:
        return cli_path.expanduser().resolve()
    env = os.environ.get("ADG_SNAPSHOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    return latest_sqlite()


# ---------------------------------------------------------------------------
# Manifest loading + filtering
# ---------------------------------------------------------------------------


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"manifest missing: {MANIFEST_PATH}")
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "gates" not in data:
        raise ValueError("manifest: top-level 'gates' list missing")
    return data


def _resolve_changed_gate_ids() -> set[str]:
    """Map ``git diff`` paths to manifest gate_ids via fan-in map."""
    map_path = REPO_ROOT / "config" / "adg_gate_fanin_map.yaml"
    if not map_path.is_file():
        return set()
    data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return set()
    always = set(data.get("always_gate_ids") or [])
    default = set(data.get("default_gate_ids") or [])
    selected = set(always)
    prefixes: list[tuple[str, list[str]]] = []
    for row in data.get("path_prefixes") or []:
        if isinstance(row, dict) and row.get("prefix") and row.get("gate_ids"):
            prefixes.append((str(row["prefix"]), list(row["gate_ids"])))
    try:
        proc = subprocess.run(  # noqa: S603
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return always | default
    if proc.returncode != 0:
        try:
            proc = subprocess.run(  # noqa: S603
                ["git", "diff", "--name-only", "HEAD~1...HEAD"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return always | default
    paths = [ln.strip().replace("\\", "/") for ln in (proc.stdout or "").splitlines() if ln.strip()]
    if not paths:
        return always | default
    matched = False
    for path in paths:
        for prefix, gate_ids in prefixes:
            if path.startswith(prefix):
                selected.update(gate_ids)
                matched = True
    if not matched:
        selected.update(default)
    return selected


def filter_gates(
    manifest: dict[str, Any],
    *,
    suite: str,
    bucket_filter: str | None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    changed_ids: set[str] | None = None
    if suite == "changed":
        changed_ids = _resolve_changed_gate_ids()
    for gate in manifest["gates"]:
        if bucket_filter and gate.get("bucket") != bucket_filter:
            continue
        suites = gate.get("suite") or ["full"]
        if suite == "changed":
            if changed_ids is not None and gate["gate_id"] not in changed_ids:
                continue
        elif suite not in suites:
            continue
        out.append(gate)
    # Order by lane, then preserve manifest order within a lane.
    return sorted(out, key=lambda g: (LANE_ORDER.index(g["bucket"]) if g["bucket"] in LANE_ORDER else 99))


# ---------------------------------------------------------------------------
# Subprocess gate execution
# ---------------------------------------------------------------------------


def _detect_bypass(gate: dict[str, Any]) -> list[str]:
    """Which bypass_env vars are set in the runner's environment?"""
    detected: list[str] = []
    bypass_env = gate.get("bypass_env")
    if isinstance(bypass_env, str):
        bypass_env = [bypass_env]
    for var in bypass_env or []:
        if os.environ.get(var) in ("1", "true", "yes"):
            detected.append(var)
    return detected


def _run_subprocess_gate(
    gate: dict[str, Any], *, snapshot: Path | None, strict: bool
) -> GateResult:
    """Run a script-backed gate and parse its output.

    The runner contract:
      1. If the gate writes its own GateResult JSON to ``output_artifact`` or
         ``--json-out``, the runner reads that file.
      2. Otherwise, the runner constructs a synthetic GateResult based on
         the subprocess's exit code + last 200 chars of stdout.
    """
    started = datetime.now(timezone.utc)
    script_rel = gate.get("script", "")
    script_path = REPO_ROOT / script_rel
    base = {
        "gate_id": str(gate["gate_id"]),
        "bucket": str(gate["bucket"]),
        "evidence_mode": str(gate.get("evidence_mode", "inventory")),
        "enforcement_mode": str(gate.get("enforcement_mode", "advisory")),
        "snapshot_id": snapshot.stem if snapshot else "",
        "input_refs": list(gate.get("reads") or []),
        "bypass_env_detected": _detect_bypass(gate),
    }

    if not script_path.is_file():
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=f"script_missing:{script_rel}",
        ).finalize()

    # Prefer per-gate JSON output: write to a dedicated rollup-side path so
    # the gate's own output_artifact is preserved (legacy compatibility).
    runner_json_path = (
        REPO_ROOT
        / "artifacts"
        / "windsurf"
        / "three_graph_runner"
        / f"{gate['gate_id'].replace('.', '_')}.json"
    )
    runner_json_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, str(script_path)]
    # Only pass --snapshot / --json-out to gates that accept them.
    # Legacy gates (accepts_runner_flags: false) get a flag-free invocation
    # and the runner reads their declared output_artifact instead.
    accepts_flags = bool(gate.get("accepts_runner_flags", True))
    if accepts_flags:
        cmd.extend(["--json-out", str(runner_json_path)])
        if strict:
            cmd.append("--strict")
        if snapshot is not None:
            cmd.extend(["--snapshot", str(snapshot)])

    timeout_s = int(gate.get("timeout_s", DEFAULT_TIMEOUT_S))
    env = os.environ.copy()
    # Legacy gates (accepts_runner_flags: false) resolve the snapshot via
    # ADG_SNAPSHOT / latest_sqlite — pin the CLI snapshot so plane-2 cannot
    # drift to a different mtime-selected file during certification.
    if snapshot is not None:
        env["ADG_SNAPSHOT"] = str(snapshot.resolve())
    # Activate strict env vars for legacy gates that gate on env not flag.
    if strict:
        strict_env = gate.get("strict_env")
        if isinstance(strict_env, str):
            env.setdefault(strict_env, "1")

    try:
        proc = subprocess.run(  # noqa: S603 — args constructed from manifest
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(REPO_ROOT),
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=f"subprocess_timeout_{timeout_s}s",
        ).finalize()

    duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    # Try to read the structured output the gate wrote.
    parsed: GateResult | None = None
    if runner_json_path.is_file():
        try:
            payload = json.loads(runner_json_path.read_text(encoding="utf-8"))
            parsed = gate_result_from_dict(payload)
        except (OSError, json.JSONDecodeError, ValueError):
            parsed = None

    # Try the legacy output_artifact path next.
    if parsed is None:
        legacy = gate.get("output_artifact")
        if legacy:
            legacy_p = REPO_ROOT / legacy
            if legacy_p.is_file():
                try:
                    raw = legacy_p.read_text(encoding="utf-8")
                    if legacy_p.suffix == ".json":
                        payload = json.loads(raw)
                        if isinstance(payload, dict) and "gate_id" in payload:
                            try:
                                parsed = gate_result_from_dict(payload)
                            except ValueError:
                                parsed = None
                except (OSError, json.JSONDecodeError):
                    parsed = None

    # Fallback: synthesize from exit code.
    if parsed is None:
        status = "PASS" if proc.returncode == 0 else "FAIL"
        reason = "" if status == "PASS" else f"legacy_exit_code:{proc.returncode}"
        tail = (proc.stdout or "")[-200:].strip()
        parsed = GateResult(
            **base,
            status=status,
            actual_fail_reason=reason,
            counts={"exit_code": proc.returncode},
            sample_failures=[{"stdout_tail": tail}] if status != "PASS" else [],
            duration_ms=duration_ms,
        ).finalize()
    else:
        # The gate may not have stamped bypass_env_detected itself.
        if not parsed.bypass_env_detected and base["bypass_env_detected"]:
            parsed.bypass_env_detected = base["bypass_env_detected"]

    return parsed


def _run_view_rule_gate(
    gate: dict[str, Any], *, snapshot: Path | None, strict: bool
) -> GateResult:
    """Delegate to check_adg_view_rules.py for the view_rule kind."""
    started = datetime.now(timezone.utc)
    base = {
        "gate_id": str(gate["gate_id"]),
        "bucket": str(gate["bucket"]),
        "evidence_mode": str(gate.get("evidence_mode", "inventory")),
        "enforcement_mode": str(gate.get("enforcement_mode", "advisory")),
        "snapshot_id": snapshot.stem if snapshot else "",
        "input_refs": list(gate.get("reads") or []),
        "bypass_env_detected": _detect_bypass(gate),
    }

    if not VIEW_RULE_RUNNER.is_file():
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=f"view_rule_runner_missing:{VIEW_RULE_RUNNER}",
        ).finalize()

    runner_json_path = (
        REPO_ROOT
        / "artifacts"
        / "windsurf"
        / "three_graph_runner"
        / f"{gate['gate_id'].replace('.', '_')}.json"
    )
    runner_json_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(VIEW_RULE_RUNNER),
        "--gate-id",
        str(gate["gate_id"]),
        "--json-out",
        str(runner_json_path),
    ]
    if strict:
        cmd.append("--strict")
    if snapshot is not None:
        cmd.extend(["--snapshot", str(snapshot)])

    timeout_s = int(gate.get("timeout_s", DEFAULT_TIMEOUT_S))
    try:
        proc = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(REPO_ROOT),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=f"view_rule_timeout_{timeout_s}s",
        ).finalize()

    duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    if not runner_json_path.is_file():
        tail = (proc.stdout or "")[-200:].strip()
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=f"view_rule_no_output:exit={proc.returncode}",
            sample_failures=[{"stdout_tail": tail}],
            duration_ms=duration_ms,
        ).finalize()
    try:
        payload = json.loads(runner_json_path.read_text(encoding="utf-8"))
        return gate_result_from_dict(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return GateResult(
            **base,
            status="ERROR",
            actual_fail_reason=f"view_rule_malformed_output:{exc}",
            duration_ms=duration_ms,
        ).finalize()


def execute_gate(
    gate: dict[str, Any], *, snapshot: Path | None, strict: bool
) -> GateResult:
    """Dispatch to the right runner based on gate shape."""
    if "view_rule" in gate:
        return _run_view_rule_gate(gate, snapshot=snapshot, strict=strict)
    return _run_subprocess_gate(gate, snapshot=snapshot, strict=strict)


# ---------------------------------------------------------------------------
# Strict-mode bypass enforcement
# ---------------------------------------------------------------------------


def apply_strict_bypass_override(result: GateResult, gate: dict[str, Any]) -> GateResult:
    """In strict mode, if bypass_env was detected and the gate is NOT
    allowed_to_skip, override the result to FAIL.

    Acceptance criterion #10 from the spec:
        "Bypass env vars cannot produce a green strict run."
    """
    if not result.bypass_env_detected:
        return result
    if gate.get("allowed_to_skip"):
        return result
    if result.status in ("PASS", "WARN", "SKIP"):
        # Override to FAIL with a stable reason code.
        # GateResult is immutable in spirit but mutable as a dataclass; we
        # rebuild instead of mutating in place to keep the contract clean.
        rebuilt = GateResult(
            gate_id=result.gate_id,
            bucket=result.bucket,
            evidence_mode=result.evidence_mode,
            enforcement_mode=result.enforcement_mode,
            snapshot_id=result.snapshot_id,
            input_refs=result.input_refs,
            counts=result.counts,
            thresholds=result.thresholds,
            sample_failures=result.sample_failures,
            bypass_env_detected=result.bypass_env_detected,
            expected_fail_reason=result.expected_fail_reason,
            actual_fail_reason="STRICT_BYPASS_DETECTED:"
            + ",".join(result.bypass_env_detected),
            duration_ms=result.duration_ms,
            started_at=result.started_at,
            status="FAIL",
        ).finalize()
        return rebuilt
    return result


# ---------------------------------------------------------------------------
# Rollup
# ---------------------------------------------------------------------------


def build_rollup(
    suite: str,
    snapshot: Path | None,
    started: datetime,
    results: list[GateResult],
    strict: bool,
) -> RollupResult:
    by_bucket: dict[str, dict[str, int]] = {}
    by_status: dict[str, int] = {}
    fail_reasons: list[str] = []

    for r in results:
        b = by_bucket.setdefault(
            r.bucket, {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0, "ERROR": 0}
        )
        b[r.status] = b.get(r.status, 0) + 1
        by_status[r.status] = by_status.get(r.status, 0) + 1
        if r.status == "FAIL":
            fail_reasons.append(f"{r.gate_id}:{r.actual_fail_reason}")
        if r.status == "ERROR":
            fail_reasons.append(f"{r.gate_id}:ERROR:{r.actual_fail_reason}")

    # Status precedence:
    #   * ERROR dominates — surface infrastructure failures regardless of mode
    #   * FAIL — at least one gate detected a real defect
    #   * WARN — at least one gate flagged an intentional advisory (e.g.
    #            aspirational schema fields, topology data unavailable).
    #            WARN is by design NOT a failure; --strict does not promote
    #            it. The per-gate code is responsible for choosing FAIL vs
    #            WARN based on whether the violation is a real invariant
    #            breach or a documented advisory. This avoids conflating
    #            "missing data" with "wrong data" at the rollup level.
    #   * PASS — no gate flagged anything.
    if by_status.get("ERROR", 0) > 0:
        overall = "ERROR"
    elif by_status.get("FAIL", 0) > 0:
        overall = "FAIL"
    elif by_status.get("WARN", 0) > 0:
        overall = "WARN"
    else:
        overall = "PASS"

    return RollupResult(
        suite=suite,
        snapshot_id=snapshot.stem if snapshot else "",
        started_at=started.isoformat(),
        finished_at=datetime.now(timezone.utc).isoformat(),
        strict_mode=strict,
        gates=[r.to_json() for r in results],
        summary_by_bucket=by_bucket,
        summary_by_status=by_status,
        overall_status=overall,
        overall_fail_reasons=fail_reasons[:50],
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        choices=("quick", "full", "changed", "negative"),
        default="quick",
    )
    parser.add_argument(
        "--bucket",
        choices=LANE_ORDER + ("all",),
        default="all",
        help="restrict to one bucket lane (default: all)",
    )
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_ROLLUP)
    parser.add_argument(
        "--gate-id",
        action="append",
        default=None,
        help="run only this manifest gate (may be repeated)",
    )
    args = parser.parse_args(argv)

    started = datetime.now(timezone.utc)

    try:
        manifest = load_manifest()
    except (FileNotFoundError, ValueError) as exc:
        print(f"[adg_runner] ERROR: {exc}")
        return 2

    snapshot = resolve_snapshot(args.snapshot)
    if snapshot is None:
        print(f"[adg_runner] ERROR: no ADG snapshot found in {ARTIFACT_DIR}")
        return 2

    bucket_filter = None if args.bucket == "all" else args.bucket
    gates = filter_gates(manifest, suite=args.suite, bucket_filter=bucket_filter)

    if args.gate_id:
        wanted = set(args.gate_id)
        gates = [g for g in gates if g["gate_id"] in wanted]

    if not gates:
        print(f"[adg_runner] ERROR: no gates matched suite={args.suite} bucket={args.bucket}")
        return 2

    print(
        f"[adg_runner] suite={args.suite} bucket={args.bucket} "
        f"strict={args.strict} snapshot={snapshot.name} gates={len(gates)}"
    )
    print()

    results: list[GateResult] = []
    for gate in gates:
        t0 = time.monotonic()
        result = execute_gate(gate, snapshot=snapshot, strict=args.strict)
        if args.strict:
            result = apply_strict_bypass_override(result, gate)
        elapsed = (time.monotonic() - t0) * 1000
        marker = {
            "PASS": "  OK",
            "WARN": "WARN",
            "SKIP": "SKIP",
            "FAIL": "FAIL",
            "ERROR": " ERR",
        }.get(result.status, "????")
        bypass_note = (
            f" [bypass:{','.join(result.bypass_env_detected)}]"
            if result.bypass_env_detected
            else ""
        )
        print(
            f"  [{marker}] {result.gate_id:<48} bucket={result.bucket:<12} "
            f"{int(elapsed):>4}ms{bypass_note}"
        )
        if result.actual_fail_reason and result.status in ("FAIL", "ERROR"):
            print(f"         reason: {result.actual_fail_reason}")
        results.append(result)

    rollup = build_rollup(args.suite, snapshot, started, results, args.strict)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(rollup.to_json(), indent=2), encoding="utf-8")

    print()
    print("=" * 72)
    print(f"[adg_runner] overall_status = {rollup.overall_status}")
    print(f"[adg_runner] by_status      = {rollup.summary_by_status}")
    try:
        rollup_display = args.json_out.resolve().relative_to(REPO_ROOT)
    except ValueError:
        rollup_display = args.json_out
    print(f"[adg_runner] rollup written = {rollup_display}")
    print("=" * 72)

    if rollup.overall_status == "PASS":
        return 0
    if rollup.overall_status == "WARN":
        return 0
    if rollup.overall_status == "FAIL":
        return 1
    return 2  # ERROR


if __name__ == "__main__":
    sys.exit(main())
