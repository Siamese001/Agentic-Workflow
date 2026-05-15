#!/usr/bin/env python3
"""W0/W6 baseline — report apps_rg literals in core L0 routing (non-enforcing).

p3.2_apps-rg-l0-critical-gaps-remediation P0.3: establish automated proof surface.
Exit 0 always (report-only) unless ``--strict`` or ``L0_APP_AGNOSTIC_STRICT=1`` —
then fail closed if any hit is outside ``baselines/l0_app_agnostic_allowlist.json``.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_L0_CORE = _REPO / "agentic_core" / "L0_routing"
_BASELINE = Path(__file__).resolve().parent / "baselines" / "l0_app_agnostic_allowlist.json"
_PATTERNS = (
    re.compile(r"\bapps_rg\b"),
    re.compile(r"\bresume_generation\b"),
)


def _load_allowlist() -> frozenset[str]:
    if not _BASELINE.is_file():
        return frozenset()
    data = json.loads(_BASELINE.read_text(encoding="utf-8"))
    paths = data.get("allowed_paths") or []
    return frozenset(str(p).replace("\\", "/") for p in paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if a hit file is not in baselines/l0_app_agnostic_allowlist.json",
    )
    args = parser.parse_args(argv)
    strict = args.strict or os.environ.get("L0_APP_AGNOSTIC_STRICT", "").strip() == "1"

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

    if strict:
        allow = _load_allowlist()
        if not allow:
            print("[check_l0_app_agnostic] STRICT fail — missing or empty baseline", _BASELINE)
            return 1
        rel_paths = []
        for h in hits:
            rel_paths.append(h.split(":", 1)[0].replace("\\", "/"))
        bad = [p for p in rel_paths if p not in allow]
        if bad:
            print("[check_l0_app_agnostic] STRICT fail — unexpected literal hits outside allowlist:")
            for b in bad:
                print("   ", b)
            return 1
        missing = sorted(allow - set(rel_paths))
        if missing:
            print(
                "[check_l0_app_agnostic] STRICT fail — allowlist drift "
                "(paths in baseline with no literal hit):"
            )
            for m in missing:
                print("   ", m)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
