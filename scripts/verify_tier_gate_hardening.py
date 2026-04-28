"""Tier 0 / Tier 1 / Tier 2 gate-hardening verifier.

Runs only the targeted hardening test file. Exits non-zero if any
hardening test fails (i.e. if any gate fails to fail-closed under a
controlled corruption).

Does NOT run the full pytest suite. Does NOT execute replay machinery,
OTEL exporters, or the proof harness.

Forces serial execution (``-n 0``) and disables the xdist plugin
explicitly. The hardening tests share the
``artifacts/runtime/requirements_proof/*.generated.json`` files via
their module-scoped autouse fixture, which calls each tier's
``_t*meta.generate()`` once per test session. Under xdist's default
parallel workers, multiple worker processes call ``generate()``
simultaneously and write to those shared paths concurrently; brief
overlapping windows can produce truncated JSON reads in a sibling
worker, which surfaces as flaky ``json.JSONDecodeError`` failures
inside the hardening fixture setups even though every assertion
passes deterministically when run serially.

This verifier is the canonical entry point invoked by
``.github/workflows/tier-gate-hardening.yml``, so forcing serial
execution here makes both local and CI runs deterministic without
changing any gate semantics or test logic.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET = "tests/runtime/test_tier_gate_fail_closed_hardening.py"


def main() -> int:
    # ``pytest.ini`` bakes ``-n 24 --dist=worksteal`` into ``addopts``,
    # which is the actual source of the parallelism. We override
    # ``addopts`` for this verifier only with ``-o addopts=...`` so the
    # xdist flags drop out, then add ``-n 0`` and ``-p no:xdist`` as
    # belt-and-braces. We keep ``--strict-markers`` and ``--strict-config``
    # from the original addopts so collection-time validation is still
    # enforced for this hardening run; the rest of the addopts string is
    # not relevant here.
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        # Override addopts so the xdist flags from pytest.ini drop out.
        "-o",
        "addopts=--strict-markers --strict-config --import-mode=importlib",
        # Disable the xdist plugin entirely. With xdist not loaded we
        # cannot also pass ``-n 0`` (it would be unrecognized), so the
        # addopts override above is the load-bearing step.
        "-p",
        "no:xdist",
        TARGET,
        "-q",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        timeout=300,
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
