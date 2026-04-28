"""Tier 0 / Tier 1 gate-hardening verifier.

Runs only the targeted hardening test file. Exits non-zero if any
hardening test fails (i.e. if any gate fails to fail-closed under a
controlled corruption).

Does NOT run the full pytest suite. Does NOT execute replay machinery,
OTEL exporters, or the proof harness.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = "tests/runtime/test_tier_gate_fail_closed_hardening.py"


def main() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", TARGET, "-q"],
        cwd=str(REPO_ROOT),
        timeout=300,
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
