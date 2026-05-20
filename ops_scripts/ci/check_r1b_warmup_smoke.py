"""CI gate — retired R1B warm-up runner must stay absent (RG-W3).

``tools/apps_rg/warm_r1b_cache.py`` was a cache-mutating shadow runner outside
``python -m apps_rg``. Product cache behavior is exercised only via the canonical
integrated spine and contract tests.

Advisory by default. Set ``R1B_WARMUP_SMOKE_FAIL_CLOSED=1`` to fail-closed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RETIRED_WARM_SCRIPT = REPO_ROOT / "tools" / "apps_rg" / "warm_r1b_cache.py"

FAIL_CLOSED = os.environ.get("R1B_WARMUP_SMOKE_FAIL_CLOSED", "0") == "1"
_findings: list[str] = []


def _check(label: str, ok: bool, detail: str = "") -> None:
    tag = "OK " if ok else "ERR"
    msg = f"[{tag}] {label}" + (f": {detail}" if detail else "")
    print(msg)
    if not ok:
        _findings.append(label)


def main() -> int:
    absent = not RETIRED_WARM_SCRIPT.is_file()
    _check("warm_r1b_cache.py physically absent", absent, str(RETIRED_WARM_SCRIPT))
    if _findings and FAIL_CLOSED:
        print(f"FAIL: {len(_findings)} finding(s)", file=sys.stderr)
        return 1
    if _findings:
        print(f"ADVISORY: {len(_findings)} finding(s) (set R1B_WARMUP_SMOKE_FAIL_CLOSED=1 to fail-closed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
