#!/usr/bin/env python3
"""GOV-SAR: Same-authority regen boundary (agentic_core/L2_execution/regen)."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    test = repo / "tests" / "governance" / "test_regen_core_boundary.py"
    if not test.is_file():
        print(f"FAIL: missing {test}", file=sys.stderr)
        return 2
    import pytest

    rc = pytest.main([str(test), "-q", "--no-header"])
    try:
        from agentic_core.L2_execution.regen import (  # noqa: F401
            IncrementalRepairContract,
            SameAuthorityRegenRunner,
        )
    except ImportError:
        print("FAIL: regen package smoke import", file=sys.stderr)
        return 1
    if isinstance(rc, int) and rc != 0:
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
