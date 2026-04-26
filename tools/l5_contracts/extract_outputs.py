"""Extract every named L5 output (Packet/Receipt/Report/...) from the
8 doctrine docs under docs/reference/00_L5_Policy_Plane and write
_l5_outputs.json mapping doc filename -> sorted list of names.

Constitutional discipline:
- subprocess timeouts: not applicable (no subprocesses spawned)
- progress bar: not required (operation < 1s on 8 small files)
- ADG: pure docs scan, no graph queries needed
"""

from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
DOC_ROOT = REPO / "docs" / "reference" / "00_L5_Policy_Plane"

# snake_case suffix pattern, ANYWHERE on a line (not just bullets).
# Catches names appearing in tables, prose ("emits foo_report"), code
# fences, payload field references, etc.
SNAKE_RE = re.compile(
    r"\b("
    r"[a-z][a-z0-9_]*_"
    r"(?:report|receipt|packet|manifest|log|diff|envelope|result|map|status|ref)"
    r")\b"
)

# PascalCase pattern, ANYWHERE on a line.
PASCAL_RE = re.compile(
    r"\b("
    r"[A-Z][A-Za-z0-9]*"
    r"(?:Packet|Receipt|Report|Manifest|Result|Diff|Envelope|Map|Log|Context|Token)"
    r")\b"
)

# Names to skip even though they shape-match — these are documentation
# artifacts, not doctrine outputs. Add sparingly and explain each.
EXCLUDED: frozenset[str] = frozenset({
    # No exclusions yet — every shape-match is treated as a doctrine name.
})


def extract() -> dict[str, list[str]]:
    from tqdm import tqdm  # progress per Constitutional §16

    docs = sorted(DOC_ROOT.glob("00*.md"))
    out: dict[str, list[str]] = {}
    # Track first-seen doc for each name to give it a stable home.
    first_seen: dict[str, str] = {}
    per_doc: dict[str, set[str]] = {d.name: set() for d in docs}
    for doc in tqdm(docs, desc="Extracting L5 doctrine outputs", unit="doc"):
        text = doc.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            for m in SNAKE_RE.finditer(line):
                name = m.group(1)
                if name in EXCLUDED:
                    continue
                first_seen.setdefault(name, doc.name)
                per_doc[first_seen[name]].add(name)
            for m in PASCAL_RE.finditer(line):
                name = m.group(1)
                if name in EXCLUDED:
                    continue
                first_seen.setdefault(name, doc.name)
                per_doc[first_seen[name]].add(name)
    for d in per_doc:
        out[d] = sorted(per_doc[d])
    return out


def main() -> None:
    mapping = extract()
    target = REPO / "tools" / "l5_contracts" / "_l5_outputs.json"
    target.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    total = {n for v in mapping.values() for n in v}
    print(f"Wrote {target.relative_to(REPO)}")
    print(f"Total unique outputs: {len(total)}")
    for fn, names in mapping.items():
        print(f"  {fn}: {len(names)}")


if __name__ == "__main__":
    main()
