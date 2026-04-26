"""Build UPDATED_MANIFEST.json and the parent-thinning zip archive.

Outputs:
  docs/reference/UPDATED_MANIFEST.json
  docs/reference/Agentic_Requirements_MECE_ParentThinned_ZeroLoss.zip
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REF = REPO / "docs" / "reference"
SKIP_DIRS = {"_archive", "__pycache__"}

MANIFEST = REF / "UPDATED_MANIFEST.json"
ZIP_OUT = REF / "Agentic_Requirements_MECE_ParentThinned_ZeroLoss.zip"


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def should_skip(rel: Path) -> bool:
    return any(part in SKIP_DIRS for part in rel.parts)


def main() -> int:
    if not REF.is_dir():
        print(f"ERROR: {REF} not found", file=sys.stderr)
        return 1

    entries: list[dict] = []
    files = sorted(p for p in REF.rglob("*") if p.is_file())
    for p in files:
        rel = p.relative_to(REF)
        if should_skip(rel):
            continue
        entries.append(
            {
                "path": rel.as_posix(),
                "size": p.stat().st_size,
                "sha256": sha256_of(p),
            }
        )

    manifest = {
        "manifest_version": "2026-04-26.parent-thinning",
        "generated_utc": "2026-04-26T19:25:00Z",
        "root": "docs/reference/",
        "file_count": len(entries),
        "total_bytes": sum(e["size"] for e in entries),
        "files": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"WROTE: {MANIFEST.relative_to(REPO)} ({len(entries)} files)")

    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for e in entries:
            src = REF / e["path"]
            zf.write(src, arcname=e["path"])
    bad = None
    with zipfile.ZipFile(ZIP_OUT) as zf:
        bad = zf.testzip()
    if bad:
        print(f"ERROR: bad zip entry {bad}", file=sys.stderr)
        return 2
    print(f"WROTE: {ZIP_OUT.relative_to(REPO)} ({ZIP_OUT.stat().st_size:,} bytes) — ZIP_INTEGRITY_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
