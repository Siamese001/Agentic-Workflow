"""Move legacy contract-harness dirs from runtime_proofs/ root into contract_harness/."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.runtime.runtime_proof_layout import (  # noqa: E402
    CONTRACT_HARNESS_DIR,
    contract_harness_root,
    is_contract_harness_run_key,
)


def relocate(*, dry_run: bool) -> int:
    root = _REPO / "artifacts" / "apps_rg" / "runtime_proofs"
    dest_root = contract_harness_root(_REPO)
    if not root.is_dir():
        print(f"missing runtime_proofs root: {root}")
        return 1
    dest_root.mkdir(parents=True, exist_ok=True)
    moved = 0
    skipped = 0
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name == CONTRACT_HARNESS_DIR:
            continue
        if not is_contract_harness_run_key(child.name):
            continue
        target = dest_root / child.name
        if target.exists():
            print(f"skip (exists): {child.name}")
            skipped += 1
            continue
        print(f"{'would move' if dry_run else 'move'}: {child.name}")
        if not dry_run:
            shutil.move(str(child), str(target))
        moved += 1
    print(f"done: moved={moved} skipped={skipped} dry_run={dry_run}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return relocate(dry_run=bool(args.dry_run))


if __name__ == "__main__":
    raise SystemExit(main())
