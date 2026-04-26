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

# snake_case suffix pattern (e.g., classification_report, prompt_hash_receipt)
OUTPUT_SUFFIX_RE = re.compile(
    r"^[\s]*[\-\*]\s+"
    r"([a-z][a-z0-9_]*_(?:"
    r"report|receipt|packet|manifest|log|diff|envelope|result|map|status|ref"
    r"))\s*$"
)

# PascalCase pattern (e.g., HITLFreezePacket, OriginTrustManifest)
PASCAL_RE = re.compile(
    r"^[\s]*[\-\*]\s+"
    r"([A-Z][A-Za-z0-9]*"
    r"(?:Packet|Receipt|Report|Manifest|Result|Diff|Envelope|Map|Log|Context|Token)"
    r")\s*$"
)


def extract() -> dict[str, list[str]]:
    from tqdm import tqdm  # progress per Constitutional §16

    docs = sorted(DOC_ROOT.glob("00*.md"))
    out: dict[str, list[str]] = {}
    for doc in tqdm(docs, desc="Extracting L5 doctrine outputs", unit="doc"):
        text = doc.read_text(encoding="utf-8", errors="replace")
        names: set[str] = set()
        for line in text.splitlines():
            m = OUTPUT_SUFFIX_RE.match(line)
            if m:
                names.add(m.group(1))
            m2 = PASCAL_RE.match(line)
            if m2:
                names.add(m2.group(1))
        out[doc.name] = sorted(names)
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
