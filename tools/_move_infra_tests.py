"""
Move 52 INTEGRATION_INFRA test files from tests/unit/ to tests/integration/,
preserving the directory sub-structure.

  tests/unit/foo/bar/test_x.py  ->  tests/integration/foo/bar/test_x.py

Skips moves where the destination already exists.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ART = REPO / "artifacts" / "adg_test_classification.json"


def main() -> None:
    art = json.loads(ART.read_text(encoding="utf-8"))
    violations = art.get("unit_violations", [])
    infra = [
        v["file"]
        for v in violations
        if v["classification"] == "INTEGRATION_INFRA" and v["file"].startswith("tests/unit/")
    ]

    print(f"Moving {len(infra)} INTEGRATION_INFRA files from tests/unit/ -> tests/integration/")

    moved = 0
    skipped = 0
    errors = 0

    for rel in infra:
        src = REPO / rel
        # Strip the "tests/unit/" prefix and re-root under "tests/integration/"
        tail = Path(rel).relative_to("tests/unit")
        dst = REPO / "tests" / "integration" / tail

        if not src.exists():
            print(f"  MISSING  {rel}")
            errors += 1
            continue

        if dst.exists():
            print(f"  EXISTS   {dst.relative_to(REPO)}")
            skipped += 1
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"  MOVED    {rel}  ->  tests/integration/{tail}")
        moved += 1

    print(f"\nDone: {moved} moved, {skipped} already existed, {errors} missing.")


if __name__ == "__main__":
    main()
