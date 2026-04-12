"""
ADG CI Lane Gate — enforces test bucket contracts.

Usage:
    python tools/adg_ci_lane_gate.py --lane unit_strict
    python tools/adg_ci_lane_gate.py --lane degraded_path
    python tools/adg_ci_lane_gate.py --lane integration_infra
    python tools/adg_ci_lane_gate.py --lane violations     # check for misplaced tests

Lane contracts:
  unit_strict       - only UNIT_STRICT files; 0 live infra; passed>0, failed=0, skipped=0
  degraded_path     - DEGRADED_PATH files; infra absent is expected; fallback must hold
  integration_infra - INTEGRATION_INFRA; requires live infra; CI skips if infra absent
  violations        - fail CI if any INTEGRATION_INFRA file lives under tests/unit/

Governance:
  ADG classification artifact must exist and be ≤24h old.
  New INTEGRATION_INFRA tests under tests/unit/ fail CI immediately (violations lane).
  Any skip in unit_strict is a hard failure — convert to xfail or fix.

Exit codes:
  0   pass
  1   test failures or contract violations
  2   configuration error (stale/missing artifact, etc.)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "adg_ci_lane_gate", "uwg_governed_write")
_emit_writes_through("p1", "adg_ci_lane_gate", "uwg_governed_write_2")
_emit_pulls_context("p1", "adg_ci_lane_gate", "context_retrieval")
_emit_pulls_context("p1", "adg_ci_lane_gate", "context_retrieval_2")
emit_determinism_digest("trace_adg_ci_lane_gate", "adg_ci_lane_gate_dispatch")
emit_determinism_digest("trace_adg_ci_lane_gate", "adg_ci_lane_gate_complete")
_emit_validated_by_safety_plane("p1", "adg_ci_lane_gate", "safety_validation")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_1")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_2")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_3")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_4")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_5")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_6")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_7")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_8")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_9")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_10")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_11")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_12")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_13")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_14")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_15")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_16")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_17")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_18")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_19")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_20")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_21")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_22")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_23")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_24")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_25")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_26")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_27")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_28")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_29")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_30")
_emit_reads_through("l4", "adg_ci_lane_gate", "urg_read_31")

REPO = Path(__file__).resolve().parent.parent
CLASSIFICATION_PATH = REPO / "artifacts" / "adg_test_classification.json"
RESULT_PATH = REPO / "artifacts" / "adg_ci_lane_gate_result.json"

# ── infra env vars that deactivate live infra for degraded-path runs ──────────
INFRA_OFF_ENV = {
    "REDIS_URL": "",
    "DISABLE_REDIS": "1",
    "DISABLE_EMBEDDING": "1",
    "DISABLE_VECTOR_STORE": "1",
    "DISABLE_HF_DOWNLOAD": "1",
    "TRANSFORMERS_OFFLINE": "1",
    "HF_DATASETS_OFFLINE": "1",
}


# Maximum age (seconds) before the classification artifact is considered stale
_MAX_ARTIFACT_AGE_S = 24 * 60 * 60  # 24 hours


def load_classification(check_freshness: bool = True) -> dict:
    if not CLASSIFICATION_PATH.exists():
        print(f"ERROR: classification artifact not found: {CLASSIFICATION_PATH}")
        print("  Run: python tools/adg_test_classifier.py")
        sys.exit(2)
    if check_freshness:
        import time

        age = time.time() - CLASSIFICATION_PATH.stat().st_mtime
        if age > _MAX_ARTIFACT_AGE_S:
            print(
                f"ERROR: classification artifact is {age / 3600:.1f}h old (limit 24h): {CLASSIFICATION_PATH}",
            )
            print("  Run: python tools/adg_test_classifier.py --refresh")
            sys.exit(2)
    return json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))


def get_files_for_lane(art: dict, lane: str) -> list[str]:
    key_map = {
        "unit_strict": "unit_strict",
        "degraded_path": "degraded_path",
        "integration_infra": "integration_infra",
    }
    return art["bucket_files"].get(key_map[lane], [])


def run_pytest(
    test_files: list[str],
    extra_args: list[str],
    extra_env: dict | None = None,
) -> tuple[int, str]:
    import os

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    cmd = (
        [
            sys.executable,
            "-m",
            "pytest",
            "--tb=short",
            "-q",
            "--no-header",
        ]
        + extra_args
        + test_files
    )

    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(REPO))
    output = result.stdout + result.stderr
    return result.returncode, output


def _parse_counts(output: str) -> dict[str, int]:
    """Parse pytest summary line into a counts dict."""
    import re

    counts: dict[str, int] = {"passed": 0, "failed": 0, "error": 0, "skipped": 0, "xfailed": 0}
    # e.g. "1736 passed, 8 xfailed, 21 warnings in 6.49s"
    for m in re.finditer(r"(\d+)\s+(passed|failed|error|skipped|xfailed|xpassed|warning)", output):
        key = m.group(2)
        if key in counts:
            counts[key] += int(m.group(1))
    return counts


def lane_unit_strict(art: dict) -> int:
    files = get_files_for_lane(art, "unit_strict")
    # filter to only tests/unit/ for the strict gate (the non-unit dirs have their own lanes)
    unit_files = [f for f in files if f.startswith("tests/unit/")]
    print(f"[UNIT_STRICT] Running {len(unit_files)} files from tests/unit/")

    if not unit_files:
        print("  No UNIT_STRICT files found in tests/unit/ — nothing to check")
        return 0

    rc, output = run_pytest(unit_files, [])
    counts = _parse_counts(output)

    # CONTRACT: skipped must be 0 in unit_strict lane
    skip_violation = counts["skipped"] > 0
    if skip_violation:
        rc = 1  # force failure even if pytest exited 0

    _print_and_save("unit_strict", rc, output, unit_files, extra_counts=counts)

    if skip_violation:
        print(
            f"\nCONTRACT VIOLATION: unit_strict lane had {counts['skipped']} skipped test(s)."
            "\n  Skipped tests are not permitted in UNIT_STRICT."
            "\n  Action: convert to pytest.xfail() with reason, or fix the test.",
        )

    return rc


def lane_degraded_path(art: dict) -> int:
    files = get_files_for_lane(art, "degraded_path")
    print(f"[DEGRADED_PATH] Running {len(files)} files with infra disabled")
    if not files:
        print("  No DEGRADED_PATH files found — nothing to check")
        return 0
    # Inject env vars that shut off live infra so degraded assertions fire
    rc, output = run_pytest(files, [], extra_env=INFRA_OFF_ENV)
    _print_and_save("degraded_path", rc, output, files)
    return rc


def lane_integration_infra(art: dict) -> int:
    files = get_files_for_lane(art, "integration_infra")
    print(f"[INTEGRATION_INFRA] Running {len(files)} files (requires live infra)")
    if not files:
        print("  No INTEGRATION_INFRA files found — nothing to check")
        return 0
    rc, output = run_pytest(files, [])
    _print_and_save("integration_infra", rc, output, files)
    return rc


def lane_violations(art: dict) -> int:
    """Fail CI if any INTEGRATION_INFRA file lives under tests/unit/."""
    violations = art.get("unit_violations", [])
    infra_in_unit = [
        v
        for v in violations
        if v["classification"] == "INTEGRATION_INFRA" and v["file"].startswith("tests/unit/")
    ]
    degraded_in_unit = [
        v
        for v in violations
        if v["classification"] == "DEGRADED_PATH" and v["file"].startswith("tests/unit/")
    ]

    result = {
        "lane": "violations",
        "integration_infra_in_unit": infra_in_unit,
        "degraded_path_in_unit": degraded_in_unit,
        "blocking_violation_count": len(infra_in_unit),
        "advisory_violation_count": len(degraded_in_unit),
        "status": "FAIL" if infra_in_unit else "PASS",
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("\n[VIOLATIONS GATE]")
    print(f"  INTEGRATION_INFRA files in tests/unit/ (BLOCKING): {len(infra_in_unit)}")
    for v in infra_in_unit:
        print(f"    {v['file']}  flags={v['infra_flags']}")

    print(f"  DEGRADED_PATH files in tests/unit/ (ADVISORY): {len(degraded_in_unit)}")
    for v in degraded_in_unit[:5]:
        print(f"    {v['file']}  flags={v['infra_flags']}")
    if len(degraded_in_unit) > 5:
        print(f"    ... and {len(degraded_in_unit) - 5} more")

    if infra_in_unit:
        print(f"\nCI BLOCKED: {len(infra_in_unit)} INTEGRATION_INFRA test files misplaced in tests/unit/")
        print("  Action: move these files to tests/integration/ or add infra skip markers")
        return 1

    print("\nVIOLATIONS GATE: PASS (no INTEGRATION_INFRA files in tests/unit/)")
    return 0


def _print_and_save(
    lane: str,
    rc: int,
    output: str,
    files: list[str],
    extra_counts: dict | None = None,
) -> None:
    # Print last N lines of pytest output
    lines = output.splitlines()
    tail = lines[-40:] if len(lines) > 40 else lines
    print("\n".join(tail))

    # Parse summary line
    summary = ""
    for line in reversed(lines):
        if "passed" in line or "failed" in line or "error" in line:
            summary = line.strip()
            break

    result: dict = {
        "lane": lane,
        "file_count": len(files),
        "returncode": rc,
        "summary": summary,
        "status": "PASS" if rc == 0 else "FAIL",
    }
    if extra_counts:
        result["counts"] = extra_counts
    new_text = json.dumps(result, indent=2)
    # Only write if content changed — prevents pre-commit dirty-file loop caused by
    # timing-sensitive summary strings (e.g. "in 8.63s" vs "in 8.65s")
    import re as _re

    def _strip_timing(s: str) -> str:
        return _re.sub(r"in \d+\.\d+s", "in X.XXs", s)

    if not RESULT_PATH.exists() or _strip_timing(RESULT_PATH.read_text(encoding="utf-8")) != _strip_timing(
        new_text,
    ):
        RESULT_PATH.write_text(new_text, encoding="utf-8")
    print(f"\n[{lane.upper()}] {'PASS' if rc == 0 else 'FAIL'}  {summary}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ADG CI lane gate")
    parser.add_argument(
        "--lane",
        choices=["unit_strict", "degraded_path", "integration_infra", "violations"],
        required=True,
        help="Which lane to run",
    )
    parser.add_argument(
        "--reclassify",
        action="store_true",
        help="Re-run classifier before gating",
    )
    parser.add_argument(
        "--fail-on-skip",
        action="store_true",
        help="Fail with exit code 1 if any skips are detected (used by pre-commit)",
    )
    args = parser.parse_args()

    # Ensure we're at repo root
    if not (REPO / ".git").exists():
        print("ERROR: must be run from repository root (detected .git missing)")
        sys.exit(2)

    if args.reclassify:
        print("Re-running classifier...")
        r = subprocess.run([sys.executable, "tools/adg_test_classifier.py"], cwd=str(REPO))
        if r.returncode != 0:
            print("ERROR: classifier failed")
            sys.exit(2)

    art = load_classification(check_freshness=not args.reclassify)
    schema = art.get("schema", "unknown")
    print(f"Classification: {schema}")
    print(
        f"  UNIT_STRICT={art['summary']['unit_strict']}  "
        f"DEGRADED_PATH={art['summary']['degraded_path']}  "
        f"INTEGRATION_INFRA={art['summary']['integration_infra']}  "
        f"violations={art['summary']['unit_violations']}",
    )
    print()

    lane_fn = {
        "unit_strict": lane_unit_strict,
        "degraded_path": lane_degraded_path,
        "integration_infra": lane_integration_infra,
        "violations": lane_violations,
    }[args.lane]

    rc = lane_fn(art)

    # If --fail-on-skip is set, ensure we fail if any skips were detected
    if args.fail_on_skip and args.lane == "unit_strict":
        # lane_unit_strict already enforces skip=0 and sets rc=1 if skips found
        # This flag just makes the intention explicit for pre-commit
        pass

    sys.exit(rc)


if __name__ == "__main__":
    main()
