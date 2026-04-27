"""Tier 1 enforcement-gate verification entrypoint.

Generates Tier 1 metadata, evaluates the fail-closed enforcement gate,
writes both result + report, and exits 0 only when status is READY.

Metadata-only. No tests, proof harness, replay, or OTEL exporter run.
"""

from __future__ import annotations

import sys

from agentic_core.runtime.prove_requirements import (
    tier1_enforcement_gate,
    tier1_step1_metadata,
    tier_fixture_bootstrap,
)


def main() -> int:
    tier_fixture_bootstrap.materialize()
    tier1_step1_metadata.generate()

    result = tier1_enforcement_gate.evaluate()
    result_path = tier1_enforcement_gate.write_result(result)
    tier1_enforcement_gate.write_report(result)

    status = result.get("result") if isinstance(result, dict) else None
    print(f"Tier 1 enforcement gate: {status}")
    print(f"Result file: {result_path}")

    return 0 if status == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
