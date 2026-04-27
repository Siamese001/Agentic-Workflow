"""Tier 0 enforcement-gate verification entrypoint.

Runs metadata generation followed by the fail-closed enforcement gate.
Exits non-zero if the gate result is not ``READY``.

Usage (local or CI):
    python scripts/verify_tier0_enforcement_gate.py

Does not run pytest, proof harnesses, replay, or OTEL exporters.
"""

from __future__ import annotations

import sys

from agentic_core.runtime.prove_requirements import (
    tier0_enforcement_gate,
    tier0_step1_metadata,
)


def main() -> int:
    tier0_step1_metadata.generate()

    result = tier0_enforcement_gate.evaluate()
    result_path = tier0_enforcement_gate.write_result(result)
    tier0_enforcement_gate.write_report(result)

    status = result.get("result") if isinstance(result, dict) else None

    print(f"Tier 0 enforcement gate: {status}")
    print(f"Result file: {result_path}")

    return 0 if status == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
