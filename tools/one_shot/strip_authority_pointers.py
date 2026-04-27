"""One-shot: remove misleading 'SOURCE FILES TO TREAT AS AUTHORITY' blocks from
Tier A SSOT files in `docs/reference/00B_L4_State_Archive_and_UWG/`.

Per user directive 2026-04-27: the three doctrine notes (`_notes/agentic_*.md`,
`_notes/agentic_system_process_map_exec.md`) are scratchpads, NOT authority.
The numbered REQ_MATRIX folders ARE the requirements. The cross-reference
blocks claiming the notes as authority are misleading.

The block runs from the line `SOURCE FILES TO TREAT AS AUTHORITY:` through
the next blank line (inclusive). Same shape across all 8 `00B.*.md` files.

For `MANIFEST.json` we drop the `source_files_to_treat_as_authority` key
without restructuring the rest.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REF = REPO / "docs" / "reference"

# All Tier A numbered folders. Skip sentinels (_archive, _notes, _primers).
SENTINELS = {"_archive", "_notes", "_primers", "contracts"}
TARGET_DIRS = [
    p for p in REF.iterdir()
    if p.is_dir() and p.name not in SENTINELS and not p.name.startswith(".")
]

HEADERS = (
    "SOURCE FILES TO TREAT AS AUTHORITY:",
    "SOURCE SPEC TO FOLLOW:",
)


def strip_block_from_md(path: Path) -> int:
    """Remove any SOURCE-FILES / SOURCE-SPEC authority block; return #lines removed."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    removed = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() in HEADERS:
            # also drop preceding blank line (block separator) if present
            if out and out[-1].strip() == "":
                out.pop()
                removed += 1
            # consume until (and including) the next blank line
            i += 1
            removed += 1  # the header itself
            while i < len(lines):
                if lines[i].strip() == "":
                    i += 1
                    removed += 1
                    break
                i += 1
                removed += 1
            continue
        out.append(line)
        i += 1
    if removed:
        path.write_text("".join(out), encoding="utf-8", newline="")
    return removed


def strip_key_from_manifest(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if "source_files_to_treat_as_authority" not in data:
        return False
    del data["source_files_to_treat_as_authority"]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    return True


def main() -> int:
    md_total = 0
    json_total = 0
    for tdir in sorted(TARGET_DIRS):
        for path in sorted(tdir.rglob("*.md")):
            n = strip_block_from_md(path)
            if n:
                md_total += 1
                print(f"  {path.relative_to(REPO).as_posix()}: stripped {n} lines")
        manifest = tdir / "MANIFEST.json"
        if manifest.exists() and strip_key_from_manifest(manifest):
            json_total += 1
            print(f"  {manifest.relative_to(REPO).as_posix()}: dropped key")
    print(f"done: {md_total} markdown files modified, {json_total} manifests cleaned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
