#!/usr/bin/env python3
"""GOV-JPH: Judge panel harness boundary (agentic_core/runtime/judges/panel)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    test = repo / "tests" / "governance" / "test_judge_panel_harness_boundary.py"
    if not test.is_file():
        print(f"FAIL: missing {test}", file=sys.stderr)
        return 2
    proc = subprocess.run(
        [sys.executable, str(test)],
        cwd=repo,
        check=False,
    )
    smoke = subprocess.run(
        [
            sys.executable,
            "-c",
            "from agentic_core.runtime.judges.panel import JudgePanelRunner, CanonicalJudgeContract",
        ],
        cwd=repo,
        check=False,
    )
    if smoke.returncode != 0:
        print("FAIL: panel harness smoke import", file=sys.stderr)
        return smoke.returncode
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
