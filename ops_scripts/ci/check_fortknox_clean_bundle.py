#!/usr/bin/env python3
"""Fort Knox clean-bundle gate — Constitutional §32.

Runs the canonical compiler and the independent bundle verifier, then
asserts both agreed the report is well-formed and the trust level is
not `FAILED`. This is the separation-of-duties backbone: compiler
emits, verifier independently re-derives, gate blocks commit if either
disagrees.

Fail-closed: exit 1 on any compiler/verifier failure or `trust_level ==
"FAILED"`. Fail-open only via `FORTKNOX_DISCIPLINE_BYPASS=1`.

Advisory rule: `.cursor/rules/fortknox-certification-discipline.md`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


def _run(argv: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        argv,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        shell=False,
        timeout=timeout,
    )


def main() -> int:
    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        print("[check_fortknox_clean_bundle] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)")
        return 0

    repo = _repo_root()
    compiler = repo / "tools" / "cert" / "compile_requirement_signoff.py"
    verifier = repo / "ops_scripts" / "ci" / "verify_final_requirement_signoff_bundle.py"
    report = repo / "artifacts" / "certification" / "final_requirement_signoff_report.json"

    for path, label in [(compiler, "compiler"), (verifier, "verifier")]:
        if not path.exists():
            print(f"[check_fortknox_clean_bundle] FATAL: {label} missing at {path}", file=sys.stderr)
            return 2

    # Phase 1: compiler must succeed.
    cproc = _run([sys.executable, str(compiler)], repo)
    if cproc.returncode != 0:
        print("[check_fortknox_clean_bundle] FAIL: compiler exit != 0", file=sys.stderr)
        print(cproc.stdout, file=sys.stderr)
        print(cproc.stderr, file=sys.stderr)
        return 1

    # Phase 2: report must exist and parse.
    if not report.exists():
        print(f"[check_fortknox_clean_bundle] FAIL: report not emitted at {report}", file=sys.stderr)
        return 1
    try:
        payload = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"[check_fortknox_clean_bundle] FAIL: report unreadable: {exc}", file=sys.stderr)
        return 1

    trust_level = payload.get("trust_level")
    if trust_level == "FAILED":
        print(
            f"[check_fortknox_clean_bundle] FAIL: trust_level == FAILED",
            file=sys.stderr,
        )
        return 1

    # Phase 3: independent verifier must agree.
    vproc = _run([sys.executable, str(verifier)], repo)
    if vproc.returncode != 0:
        print("[check_fortknox_clean_bundle] FAIL: bundle verifier exit != 0", file=sys.stderr)
        print(vproc.stdout, file=sys.stderr)
        print(vproc.stderr, file=sys.stderr)
        return 1

    # Verifier may also emit a status JSON or a textual PASS marker.
    combined = (vproc.stdout or "") + (vproc.stderr or "")
    if "bundle_verification_status" in combined and "PASS" not in combined:
        print("[check_fortknox_clean_bundle] FAIL: verifier did not report PASS", file=sys.stderr)
        return 1

    print(f"[check_fortknox_clean_bundle] PASS — trust_level={trust_level!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
