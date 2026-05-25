#!/usr/bin/env python3
"""Append §22 ADG graph-layer evidence sections to active plans when missing."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / ".cursor" / "plans"
APPENDIX = Path(__file__).with_name("graph_layer_plan_appendix.md")
EXCLUDE = frozenset({"README.md", "CURSOR_RUNTIME_SEAM_TEMPLATE.md"})

EVIDENCE_HDR = "## ADG_GRAPH_LAYER_EVIDENCE"
HOTSPOT_HDR = "## ADG_HOTSPOT_REPORT"


def _needs_appendix(text: str) -> bool:
    return EVIDENCE_HDR not in text or HOTSPOT_HDR not in text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("plans", nargs="*", help="Optional plan basenames; default all top-level *.md")
    args = parser.parse_args()

    appendix = APPENDIX.read_text(encoding="utf-8")
    if args.plans:
        targets = [PLANS_DIR / (p if p.endswith(".md") else f"{p}.md") for p in args.plans]
    else:
        targets = sorted(p for p in PLANS_DIR.glob("*.md") if p.name not in EXCLUDE)

    patched = 0
    for path in targets:
        if not path.is_file():
            print(f"skip missing {path.name}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        if not _needs_appendix(text):
            continue
        if args.dry_run:
            print(f"would patch {path.name}", file=sys.stderr)
            patched += 1
            continue
        path.write_text(text.rstrip() + appendix, encoding="utf-8")
        print(f"patched {path.name}", file=sys.stderr)
        patched += 1

    print(f"{'would patch' if args.dry_run else 'patched'} {patched} plan(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
