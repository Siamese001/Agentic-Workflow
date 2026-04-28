"""Tier 4 enforcement gate verification entrypoint.

1. Generates Tier 4 metadata from TIER4_SELECTION.json.
2. Evaluates the Tier 4 enforcement readiness gate.
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
    tier4_enforcement_gate,
    tier4_step1_metadata,
)


def main() -> int:
    tier4_step1_metadata.generate()

    result = tier4_enforcement_gate.evaluate()
    result_path = tier4_enforcement_gate.write_result(result)
    report_path = tier4_enforcement_gate.write_report(result)

    print(f"Tier 4 enforcement gate: {result['result']}")
    print(f"Tier 4 seen / expected: {result['tier4_seen']} / {result['tier4_total']}")
    print(f"Blocker counts: {result['blocker_counts']}")
    print(f"Linkage status counts: {result['linkage_status_counts']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")

    return 0 if result["result"] == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
