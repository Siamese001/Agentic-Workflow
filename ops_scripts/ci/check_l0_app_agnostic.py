#!/usr/bin/env python3
"""W0/W6 baseline — report apps_rg literals in core L0 routing (non-enforcing).

p3.2_apps-rg-l0-critical-gaps-remediation P0.3: establish automated proof surface.
Exit 0 always (report-only). Fail-closed enforcement is a later wave.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_L0_CORE = _REPO / "agentic_core" / "L0_routing"
_PATTERNS = (
    re.compile(r"\bapps_rg\b"),
    re.compile(r"\bresume_generation\b"),
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    hits: list[str] = []
    if not _L0_CORE.is_dir():
        print("[check_l0_app_agnostic] SKIP — agentic_core/L0_routing missing")
        return 0
    for path in sorted(_L0_CORE.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for rx in _PATTERNS:
            if rx.search(text):
                hits.append(f"{path.relative_to(_REPO)}: matched {rx.pattern}")
                break
    print(f"[check_l0_app_agnostic] L0_routing scan: {len(hits)} file(s) with app-ish literals")
    for h in hits[:40]:
        print("  ", h)
    if len(hits) > 40:
        print(f"  ... ({len(hits) - 40} more)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
