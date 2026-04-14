from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


PROJECT_ROOT = get_validated_project_root()
PLANS_DIR = PROJECT_ROOT / "docs" / "reports" / "plans"
STATUS_PATTERN = re.compile(r"^Status:", re.MULTILINE)
DATE_PATTERN = re.compile(r"^(Date:.*)$", re.MULTILINE)


def add_status_if_missing(file_path: Path, execute: bool) -> bool:
    """Add 'Status: RESOLVED' to an RCA file if it is missing."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    if STATUS_PATTERN.search(content):
        print(f"Skipped {file_path.relative_to(PROJECT_ROOT)} (status already present)")
        return False

    if DATE_PATTERN.search(content):
        new_content = DATE_PATTERN.sub(r"\1\nStatus: RESOLVED", content, count=1)
    else:
        new_content = "Status: RESOLVED\n" + content

    if execute:
        file_path.write_text(new_content, encoding="utf-8")
        print(f"Patched {file_path.relative_to(PROJECT_ROOT)}")
    else:
        print(f"[DRY-RUN] Would patch {file_path.relative_to(PROJECT_ROOT)}")
    return True


def main(execute: bool = False) -> int:
    if not PLANS_DIR.is_dir():
        print(f"ERROR: Directory not found: {PLANS_DIR}")
        return 1

    rca_files = sorted(PLANS_DIR.glob("RCA_*.md"))
    patched_count = 0
    for file_path in rca_files:
        try:
            if add_status_if_missing(file_path, execute=execute):
                patched_count += 1
        except OSError as exc:
            print(f"ERROR: Could not process {file_path.relative_to(PROJECT_ROOT)}: {exc}")
            return 1

    mode = "EXECUTE" if execute else "DRY-RUN"
    print(f"\nPatching complete ({mode}). {patched_count} of {len(rca_files)} files would be updated.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add missing status fields to RCA markdown files.")
    parser.add_argument("--execute", action="store_true", help="Write changes to disk. Default is dry-run.")
    sys.exit(main(execute=parser.parse_args().execute))
