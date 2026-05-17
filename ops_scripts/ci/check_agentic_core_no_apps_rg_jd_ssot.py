#!/usr/bin/env python3
"""GOV: agentic_core must not reference apps_rg JD resolver or default JD SSOT paths."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE = REPO_ROOT / "agentic_core"

# Substrings that would indicate coupling to apps_rg JD SSOT / resolver (forbidden in core).
_FORBIDDEN_SUBSTRINGS: tuple[str, ...] = (
    "jd_resolution",
    "resolve_jd_for_lanes",
    "default_jd_targeting",
    "jd_ssot",
    "DEFAULT_JD_TARGETING",
)


def main() -> int:
    if not CORE.is_dir():
        print("RG-JD0 SKIP: agentic_core/ missing")
        return 0

    failures: list[str] = []
    for path in sorted(CORE.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(REPO_ROOT).as_posix()
        for frag in _FORBIDDEN_SUBSTRINGS:
            if frag in text:
                failures.append(f"{rel}: forbidden substring {frag!r}")

    if failures:
        print("RG-JD0 FAIL: agentic_core must not reference apps_rg JD resolver / default JD SSOT:")
        for line in failures:
            print(f"  - {line}")
        return 1

    print("RG-JD0 PASS: no apps_rg JD resolver / SSOT references under agentic_core/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
