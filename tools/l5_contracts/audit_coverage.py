"""Audit what extract_outputs.py captured vs what is actually IN the docs.

Strategy:
1. Walk every line of every L5 doctrine doc.
2. Find ALL identifier-shaped tokens that look like outputs (snake_case
   ending in a known suffix; PascalCase ending in a known suffix).
3. Compare against the registry. Report:
   - matches (in docs AND in registry)  -> covered
   - in docs, NOT in registry          -> MISSED
   - in registry, NOT in docs          -> spurious (should be empty)
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
DOC_ROOT = REPO / "docs" / "reference" / "00A_L5_Governance_&_Safety"

SNAKE_SUFFIXES = (
    "report", "receipt", "packet", "manifest", "log", "diff", "envelope",
    "result", "map", "status", "ref",
)
PASCAL_SUFFIXES = (
    "Packet", "Receipt", "Report", "Manifest", "Result", "Diff", "Envelope",
    "Map", "Log", "Context", "Token",
)

# ANYWHERE on a line: snake_case ending with one of our suffixes
SNAKE_ANY_RE = re.compile(
    r"\b([a-z][a-z0-9_]*_(?:" + "|".join(SNAKE_SUFFIXES) + r"))\b"
)
# ANYWHERE on a line: PascalCase ending with one of our suffixes
PASCAL_ANY_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9]*(?:" + "|".join(PASCAL_SUFFIXES) + r"))\b"
)


def main() -> int:
    sys.path.insert(0, str(REPO))
    from agentic_core.L5_safety.contracts import ALL_OUTPUT_NAMES

    found_in_docs: set[str] = set()
    line_locations: dict[str, list[str]] = {}
    for doc in sorted(DOC_ROOT.glob("00*.md")):
        for lineno, line in enumerate(
            doc.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            for m in SNAKE_ANY_RE.finditer(line):
                name = m.group(1)
                found_in_docs.add(name)
                line_locations.setdefault(name, []).append(
                    f"{doc.name}:{lineno}"
                )
            for m in PASCAL_ANY_RE.finditer(line):
                name = m.group(1)
                found_in_docs.add(name)
                line_locations.setdefault(name, []).append(
                    f"{doc.name}:{lineno}"
                )

    missed = sorted(found_in_docs - ALL_OUTPUT_NAMES)
    spurious = sorted(ALL_OUTPUT_NAMES - found_in_docs)
    overlap = found_in_docs & ALL_OUTPUT_NAMES

    print(f"Doctrine tokens found by anywhere-on-line regex : {len(found_in_docs)}")
    print(f"Tokens in registry                              : {len(ALL_OUTPUT_NAMES)}")
    print(f"Overlap (covered)                               : {len(overlap)}")
    print(f"In docs but NOT in registry (MISSED)            : {len(missed)}")
    print(f"In registry but NOT found by audit (spurious)   : {len(spurious)}")

    if missed:
        print("\n=== MISSED (in docs, not in registry) ===")
        for name in missed[:60]:
            locs = line_locations.get(name, [])
            print(f"  {name:60s} first seen: {locs[0] if locs else '?'}")
        if len(missed) > 60:
            print(f"  ... and {len(missed) - 60} more")

    if spurious:
        print("\n=== SPURIOUS (in registry, not seen by audit) ===")
        for name in spurious[:30]:
            print(f"  {name}")
        if len(spurious) > 30:
            print(f"  ... and {len(spurious) - 30} more")

    pathlib.Path(REPO / "tools" / "l5_contracts" / "_audit_report.json").write_text(
        json.dumps(
            {
                "found_in_docs": sorted(found_in_docs),
                "missed": missed,
                "spurious": spurious,
                "overlap_count": len(overlap),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
