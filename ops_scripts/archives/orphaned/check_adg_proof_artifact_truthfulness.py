#!/usr/bin/env python3
"""
CI gate: §15 ADG Proof-Artifact Truthfulness.

Scans every JSON artifact under docs/reports/plans/ that contains a
'raw_counts' block and verifies:
  1. Every *_raw flag matches its raw_counts value (zero count → false).
  2. Every *_derived flag that is true has a non-empty 'deriving_command'.
  3. Every *_derived flag that is true has 'deriving_command_output_lines' > 0.

Exits 1 on any violation.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / "docs" / "reports" / "plans"


def check_artifact(path: Path) -> list[str]:
    violations: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):    # guardian: Add error context logging
        return violations  # not a JSON artifact or unreadable — skip

    if "raw_counts" not in data:
        return violations  # not a proof artifact

    raw_counts: dict = data["raw_counts"]
    flags: dict = data.get("flags", {})
    derived_facts: dict = data.get("derived_facts", {})

    # Rule 1: *_raw flags must agree with raw_counts
    for key, count in raw_counts.items():
        raw_flag = f"{key}_present_raw"
        if raw_flag in flags:
            expected = count > 0
            if flags[raw_flag] != expected:
                violations.append(
                    f"{path}: flags.{raw_flag}={flags[raw_flag]} "
                    f"but raw_counts.{key}={count} (expected {expected})",
                )

    # Rule 2 & 3: *_derived flags that are true need deriving_command + output_lines > 0
    for flag_key, flag_val in flags.items():
        if not flag_key.endswith("_derived"):
            continue
        if flag_val is not True:
            continue
        deriving_cmd = derived_facts.get("deriving_command", "")
        if not deriving_cmd:
            violations.append(
                f"{path}: flags.{flag_key}=true but derived_facts.deriving_command is absent or empty",
            )
        output_lines = derived_facts.get("deriving_command_output_lines", 0)
        if not isinstance(output_lines, int) or output_lines <= 0:
            violations.append(
                f"{path}: flags.{flag_key}=true but derived_facts.deriving_command_output_lines={output_lines!r} (must be > 0)",
            )

    return violations


def main() -> int:
    if not PLANS_DIR.exists():
        print(f"OK: {PLANS_DIR} does not exist — no proof artifacts to check.")
        return 0

    all_violations: list[str] = []
    for path in sorted(PLANS_DIR.rglob("*.json")):
        all_violations.extend(check_artifact(path))

    if all_violations:
        print(f"ERROR: §15 ADG proof-artifact truthfulness violations ({len(all_violations)}):")
        for v in all_violations:
            print(f"  {v}")
        return 1

    print("OK: §15 ADG proof-artifact truthfulness — all artifacts clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
