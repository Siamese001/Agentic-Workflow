"""Tier 5 enforcement gate verification entrypoint.

1. Generates Tier 5 metadata from TIER5_SELECTION.json.
2. Evaluates the Tier 5 enforcement readiness gate.
3. Writes result + report.
4. Prints result paths.
5. Exits 0 only if READY, non-zero if BLOCKED.

Metadata-only. Does NOT execute tests, replay machinery, OTEL
exporters, or the proof harness. Does NOT claim proof or coverage.
BLOCKED is the expected and acceptable first-pass outcome.
"""

from __future__ import annotations

import sys

from agentic_core.runtime.prove_requirements import (
    tier5_enforcement_gate,
    tier5_step1_metadata,
)


def main() -> int:
    tier5_step1_metadata.generate()

    result = tier5_enforcement_gate.evaluate()
    result_path = tier5_enforcement_gate.write_result(result)
    report_path = tier5_enforcement_gate.write_report(result)

    print(f"Tier 5 enforcement gate: {result['result']}")
    print(f"Tier 5 seen / expected: {result['tier5_seen']} / {result['tier5_total']}")
    print(f"Blocker counts: {result['blocker_counts']}")
    print(f"Linkage status counts: {result['linkage_status_counts']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")

    return 0 if result["result"] == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
