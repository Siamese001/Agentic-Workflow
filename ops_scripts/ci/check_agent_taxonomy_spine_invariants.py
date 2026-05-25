#!/usr/bin/env python3
"""CI gate: ADR-088 taxonomy spine invariants (W1)."""
from __future__ import annotations

import sys


def main() -> int:
    from agentic_core.L2_execution.types.agent_taxonomy_registry import (
        AGENT_TAXONOMY_MAP,
        validate_taxonomy_spine_invariants,
    )

    violations = validate_taxonomy_spine_invariants(AGENT_TAXONOMY_MAP)
    if violations:
        for v in violations:
            print(f"FAIL: {v}", file=sys.stderr)
        return 1
    print(
        "PASS: agent_taxonomy_spine_invariants "
        f"(entries={len(AGENT_TAXONOMY_MAP)}, ARTIFACT_PROVEN=0)",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
