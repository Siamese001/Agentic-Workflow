"""Tier 3 enforcement gate verification entrypoint.

Generates Tier 3 metadata, then evaluates the Tier 3 enforcement gate
and writes its result/report. Exits 0 only when the result is READY.

Metadata-only. Does NOT execute tests, replay machinery, OTEL exporters,
or the proof harness. Does NOT claim proof, coverage, or readiness.

BLOCKED is the expected first-pass result and is preferred over fake
readiness.
"""

from __future__ import annotations

import sys

from agentic_core.runtime.prove_requirements import (
    tier3_enforcement_gate,
    tier3_step1_metadata,
)


def main() -> int:
    tier3_step1_metadata.generate()
    result = tier3_enforcement_gate.evaluate()
    result_path = tier3_enforcement_gate.write_result(result)
    report_path = tier3_enforcement_gate.write_report(result)
    print(f"Tier 3 enforcement gate: {result['result']}")
    print(f"Tier 3 seen / expected: {result['tier3_seen']} / {result['tier3_total']}")
    print(f"Blocker counts: {result['blocker_counts']}")
    print(f"Linkage status counts: {result['linkage_status_counts']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")
    return 0 if result["result"] == "READY" else 2


if __name__ == "__main__":
    sys.exit(main())
