#!/usr/bin/env python3
"""Fort Knox mutation-rejection gate — Constitutional §32.

Runs `scripts/generate_mutation_rejection_report.py` and asserts:
- `overall_verdict == "PASS"` — every adversarial mutation was rejected
- `clean_bundle_unchanged == true` — no collateral damage to the clean
  report during the mutation sweep

This is the Critic Agent / Adversarial Code Review counterpart to the
clean-bundle gate. Separation of duties: a SINGLE script that produces
both the clean report and the mutation report would be its own trust
root — forbidden by the hostile-verifier doctrine.

Fail-closed: exit 1 on any tamper accepted or clean-bundle drift.
Fail-open only via `FORTKNOX_DISCIPLINE_BYPASS=1`.

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


def main() -> int:
    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        print("[check_fortknox_mutation_rejection] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)")
        return 0

    repo = _repo_root()
    runner = repo / "scripts" / "generate_mutation_rejection_report.py"
    report = repo / "artifacts" / "certification" / "fortknox_mutation_rejection_report.json"

    if not runner.exists():
        print(f"[check_fortknox_mutation_rejection] FATAL: runner missing at {runner}", file=sys.stderr)
        return 2

    try:
        proc = subprocess.run(
            [sys.executable, str(runner)],
            cwd=str(repo),
            capture_output=True,
            text=True,
            check=False,
            shell=False,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("[check_fortknox_mutation_rejection] FAIL: runner timed out (600s)", file=sys.stderr)
        return 1

    if proc.returncode != 0:
        print("[check_fortknox_mutation_rejection] FAIL: runner exit != 0", file=sys.stderr)
        print(proc.stdout[-2000:], file=sys.stderr)
        print(proc.stderr[-2000:], file=sys.stderr)
        return 1

    if not report.exists():
        print(f"[check_fortknox_mutation_rejection] FAIL: report not emitted at {report}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"[check_fortknox_mutation_rejection] FAIL: report unreadable: {exc}", file=sys.stderr)
        return 1

    verdict = payload.get("overall_verdict")
    clean_unchanged = payload.get("clean_bundle_unchanged")

    if verdict != "PASS":
        print(
            f"[check_fortknox_mutation_rejection] FAIL: overall_verdict={verdict!r} "
            f"(expected PASS). At least one mutation was not rejected.",
            file=sys.stderr,
        )
        return 1

    if clean_unchanged is not True:
        print(
            f"[check_fortknox_mutation_rejection] FAIL: clean_bundle_unchanged={clean_unchanged!r} "
            f"(expected true). Mutation run contaminated the clean report.",
            file=sys.stderr,
        )
        return 1

    mutations = payload.get("mutations_attempted") or payload.get("mutation_count")
    print(f"[check_fortknox_mutation_rejection] PASS — mutations={mutations!r} all rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
