"""Find lingering bootstrap references that no longer resolve cleanly."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


PROJECT_ROOT = get_validated_project_root()
BOOTSTRAP_TOKEN = re.compile(r"bootstrap", re.IGNORECASE)


def scan_bootstrap_references(root: Path) -> list[tuple[Path, int, str]]:
    findings: list[tuple[Path, int, str]] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            if BOOTSTRAP_TOKEN.search(line):
                findings.append((path, line_number, line.strip()))
    return findings


def main(limit: int = 100) -> int:
    findings = scan_bootstrap_references(PROJECT_ROOT)
    print(f"Bootstrap findings: {len(findings)}")
    for path, line_number, line in findings[:limit]:
        print(f"- {path.relative_to(PROJECT_ROOT)}:{line_number} {line}")
    if len(findings) > limit:
        print(f"... truncated {len(findings) - limit} additional findings")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for lingering bootstrap references.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum findings to print.")
    raise SystemExit(main(limit=parser.parse_args().limit))
