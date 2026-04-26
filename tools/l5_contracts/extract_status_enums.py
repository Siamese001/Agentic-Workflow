"""Extract per-status enum value sets from L5 doctrine docs.

Doctrine pattern: ``<x>_status = value1 | value2 | value3``.

Output: tools/l5_contracts/_l5_status_enums.json — mapping
field_name -> list of allowed string values (in doctrine order).

The generator (``generate_contracts.py``) consumes this to emit a
StrEnum per field in ``agentic_core.L5_safety.contracts._status_enums``
and to bind those enums as the ``status_value`` field type on the
corresponding ``L5Status`` subclass.
"""
from __future__ import annotations

import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
DOC_ROOT = REPO / "docs" / "reference" / "00_L5_Policy_Plane"
OUT = REPO / "tools" / "l5_contracts" / "_l5_status_enums.json"

STATUS_SET_RE = re.compile(
    r"^[\s\-\*]*([a-z][a-z0-9_]*_status)\s*=\s*(.+?)\s*$"
)
# Strip trailing prose like " (per-step)" or stray markdown bold.
TRAILING_NOTE_RE = re.compile(r"\s*[\(\[].*$")
VALUE_TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def main() -> None:
    found: dict[str, list[str]] = {}
    sources: dict[str, str] = {}
    for doc in sorted(DOC_ROOT.glob("00*.md")):
        for lineno, raw in enumerate(
            doc.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            m = STATUS_SET_RE.match(raw.strip())
            if not m:
                continue
            name = m.group(1)
            rhs = TRAILING_NOTE_RE.sub("", m.group(2)).strip()
            # Split on '|' and take only well-formed snake_case tokens.
            values: list[str] = []
            for tok in rhs.split("|"):
                tok = tok.strip().rstrip(",.;").strip()
                if VALUE_TOKEN_RE.match(tok) and tok not in values:
                    values.append(tok)
            if not values:
                continue
            # Union semantics across docs: when two docs declare the same
            # status field with different value sets, accept the union to
            # be conservative (a runtime may emit either set). Preserve
            # doctrine order for the first-seen values and append novel
            # values from later docs at the end.
            if name in found:
                added = [v for v in values if v not in found[name]]
                if added:
                    print(
                        f"INFO: extending {name} value set with {added} "
                        f"from {doc.name}:{lineno} (first seen in "
                        f"{sources[name]})"
                    )
                    found[name] = found[name] + added
                    sources[name] = f"{sources[name]}; {doc.name}:{lineno}"
                continue
            found[name] = values
            sources[name] = f"{doc.name}:{lineno}"

    OUT.write_text(
        json.dumps(
            {"enums": found, "sources": sources}, indent=2, sort_keys=True
        ),
        encoding="utf-8",
    )
    print(f"Extracted {len(found)} status enums to {OUT.relative_to(REPO)}")
    for name, values in sorted(found.items()):
        print(f"  {name}: {values}")


if __name__ == "__main__":
    main()
