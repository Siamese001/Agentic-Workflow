#!/usr/bin/env python3
"""GOV: agentic_core must not reference apps_rg resume resolver or default resume SSOT paths."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE = REPO_ROOT / "agentic_core"

_FORBIDDEN_SUBSTRINGS: tuple[str, ...] = (
    "resume_resolution",
    "resolve_resume_for_lanes",
    "load_lane_base_resume_json",
    "canonical_resume_digest",
    "DEFAULT_RESUME_SSOT",
    "DEFAULT_RESUME_REPO_RELPATH",
    "amit_ayer_base_resume_v1",
    "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
)


def main() -> int:
    if not CORE.is_dir():
        print("RG-RESUME0 SKIP: agentic_core/ missing")
        return 0

    failures: list[str] = []
    for path in sorted(CORE.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(REPO_ROOT).as_posix()
        for frag in _FORBIDDEN_SUBSTRINGS:
            if frag in text:
                failures.append(f"{rel}: forbidden substring {frag!r}")

    if failures:
        print("RG-RESUME0 FAIL: agentic_core must not reference apps_rg resume resolver / SSOT:")
        for line in failures:
            print(f"  - {line}")
        return 1

    print("RG-RESUME0 PASS: no apps_rg resume resolver / SSOT references under agentic_core/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
