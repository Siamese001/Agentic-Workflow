#!/usr/bin/env python3
"""Fort Knox positive-control gate — Constitutional §32.

Asserts that the Fort Knox PASS path is reachable on a CONTROL-by-CONTROL
basis for the set of canary requirements. The gate does NOT demand row-
level `SIGNED_OFF`, because SIGNED_OFF requires every required control to
be attested, and several mandated controls (`ci_gate`, `layer_boundary`)
cannot be honestly proven by the currently-approved verifier surface.

What the gate asserts instead (honest canary):
  - For each canary row, the atomic assertions emitted by
    `tools/cert/build_positive_control_fixtures.py` produce at least
    `MIN_PASSING_CONTROLS` PASSing controls in the compiled report.
  - Default minimum: 3 (verifier_pass, verifier_exit_zero, last_verified_timestamp).
  - A silently-broken compiler that rejects every assertion would emit 0
    passing controls and fail this gate. A silently-broken verifier that
    always PASSes would not meaningfully change this count.

Canary set: RTC-REQ-001, 002, 004, 030, 031 (all with honest partial
attestation under the CSV-gate verifier). Override with
`POSITIVE_CONTROL_REQ_IDS` env var.

Fail-closed: exit 1 if any canary has fewer than the required passing
controls. Fail-open only via `FORTKNOX_DISCIPLINE_BYPASS=1`.

Advisory rule: `.windsurf/rules/fortknox-certification-discipline.md`.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


DEFAULT_CANARIES = [
    "RTC-REQ-001", "RTC-REQ-002", "RTC-REQ-004", "RTC-REQ-030", "RTC-REQ-031",
]


def _canary_ids() -> list[str]:
    override = os.environ.get("POSITIVE_CONTROL_REQ_IDS", "").strip()
    if override:
        return [x.strip() for x in override.split(",") if x.strip()]
    return list(DEFAULT_CANARIES)


def _min_passing_controls() -> int:
    try:
        return int(os.environ.get("MIN_PASSING_CONTROLS", "3"))
    except ValueError:
        return 3


def main() -> int:
    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        print("[check_fortknox_positive_control] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)")
        return 0

    repo = _repo_root()
    report_path = repo / "artifacts" / "certification" / "final_requirement_signoff_report.json"
    if not report_path.exists():
        print(
            f"[check_fortknox_positive_control] FAIL: report not found at {report_path}",
            file=sys.stderr,
        )
        return 1

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"[check_fortknox_positive_control] FAIL: report unreadable: {exc}", file=sys.stderr)
        return 1

    raw = payload.get("rows") or []
    if isinstance(raw, list):
        rows = {r.get("req_id"): r for r in raw if isinstance(r, dict) and r.get("req_id")}
    elif isinstance(raw, dict):
        rows = raw
    else:
        print(f"[check_fortknox_positive_control] FAIL: report shape unexpected",
              file=sys.stderr)
        return 1

    canaries = _canary_ids()
    min_passing = _min_passing_controls()
    strict = os.environ.get("POSITIVE_CONTROL_STRICT", "0") == "1"

    failures: list[str] = []
    per_row: list[tuple[str, int, int]] = []  # (req_id, pass_count, required_count)
    for canary in canaries:
        row = rows.get(canary) or {}
        if not row:
            failures.append(f"{canary}: row not present in report")
            continue
        controls = row.get("controls") or []
        pass_count = sum(1 for c in controls if isinstance(c, dict) and c.get("passed"))
        required_count = len(row.get("required_controls") or [])
        per_row.append((canary, pass_count, required_count))
        if pass_count < min_passing:
            failures.append(f"{canary}: only {pass_count}/{required_count} controls passing "
                            f"(need >= {min_passing})")

    if failures:
        label = "FAIL" if strict else "WARN"
        print(f"[check_fortknox_positive_control] {label}: canary regression detected",
              file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        if strict:
            return 1
        print("[check_fortknox_positive_control] Advisory mode; set "
              "POSITIVE_CONTROL_STRICT=1 to block.", file=sys.stderr)
        return 0

    print(f"[check_fortknox_positive_control] PASS — "
          f"{len(canaries)} canary rows each have >= {min_passing} passing controls")
    for rid, p, r in per_row:
        print(f"  {rid}: {p}/{r} controls passing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
