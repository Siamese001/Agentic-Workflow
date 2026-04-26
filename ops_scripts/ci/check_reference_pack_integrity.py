"""Reference-pack integrity gate.

Verifies ``docs/reference/MANIFEST.json`` against disk:
  - every listed file exists
  - byte-size matches
  - sha256 matches

Also verifies sub-MANIFEST consistency for sub-packs that publish their own
``children[]`` list — those lists must be a subset of the on-disk files in
the same folder.

Exit codes:
  0  PASS
  1  FAIL  manifest drift detected
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from tqdm import tqdm

REPO = Path(__file__).resolve().parents[2]
REF = REPO / "docs" / "reference"
ROOT_MANIFEST = REF / "MANIFEST.json"


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_root_manifest() -> tuple[int, int, list[str]]:
    """Return (mismatches, total_entries, error_messages)."""
    if not ROOT_MANIFEST.exists():
        return 1, 0, [f"MISSING: {ROOT_MANIFEST.relative_to(REPO)}"]
    data = json.loads(ROOT_MANIFEST.read_text(encoding="utf-8"))
    entries = data.get("files", [])
    errs: list[str] = []
    for ent in tqdm(entries, desc="Verifying manifest", unit="file", disable=not sys.stdout.isatty()):
        rel = ent["path"]
        p = REF / rel
        if not p.exists():
            errs.append(f"MISSING:  {rel}")
            continue
        sz = p.stat().st_size
        if sz != ent["size"]:
            errs.append(f"SIZE:     {rel} (manifest={ent['size']}, disk={sz})")
            continue
        actual = sha256_of(p)
        if actual != ent["sha256"]:
            errs.append(f"HASH:     {rel} (manifest={ent['sha256'][:16]}, disk={actual[:16]})")
    return len(errs), len(entries), errs


def check_sub_manifests() -> list[str]:
    """For each sub-MANIFEST.json, verify its children[] entries exist on disk."""
    errs: list[str] = []
    for sub_mp in REF.rglob("MANIFEST.json"):
        if sub_mp == ROOT_MANIFEST:
            continue
        try:
            data = json.loads(sub_mp.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errs.append(f"INVALID JSON: {sub_mp.relative_to(REPO)} ({exc})")
            continue
        folder = sub_mp.parent
        # Bounded N (small per-folder); wrapped with tqdm for §16 compliance, disabled in non-TTY
        children: list[str] = []
        for kind in ("files", "children"):
            children.extend(c for c in (data.get(kind, []) or []) if isinstance(c, str))
        for child in tqdm(children, desc=f"sub:{sub_mp.parent.name}", unit="file", leave=False, disable=not sys.stdout.isatty()):
            # children entries are filenames relative to the sub-MANIFEST's folder,
            # except some (like 00B's) include a folder prefix
            target = folder / child
            if not target.exists():
                # try root-relative as fallback for prefixed entries
                target_root = REF / child
                if not target_root.exists():
                    errs.append(f"SUB:      {sub_mp.relative_to(REPO)} → '{child}' not on disk")
    return errs


def main() -> int:
    print("[check_reference_pack_integrity]")
    bad, total, root_errs = check_root_manifest()
    sub_errs = check_sub_manifests()
    print(f"  Root manifest entries: {total}")
    print(f"  Root mismatches:       {bad}")
    print(f"  Sub-manifest errors:   {len(sub_errs)}")
    if root_errs or sub_errs:
        print()
        for e in root_errs[:30]:
            print(f"  [root] {e}")
        if len(root_errs) > 30:
            print(f"  ...and {len(root_errs) - 30} more")
        for e in sub_errs[:30]:
            print(f"  [sub]  {e}")
        if len(sub_errs) > 30:
            print(f"  ...and {len(sub_errs) - 30} more")
        print()
        print("FAIL: docs/reference/ pack drift. To repair:")
        print("  1. If files moved/renamed, update MANIFEST entries (re-hash)")
        print("  2. If files were edited, refresh size+sha256 in MANIFEST")
        print("  3. If sub-MANIFEST drifted, update its children[] list")
        return 1
    print()
    print("[check_reference_pack_integrity] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
