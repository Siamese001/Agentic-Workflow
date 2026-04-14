"""Move report artifacts under docs/reports according to SSOT-style rules."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import REPORTS_DIR, get_validated_project_root
from territory_ssot_definitions_config import suggest_report_subdir


PROJECT_ROOT = get_validated_project_root()
REPORTS_ROOT = PROJECT_ROOT / "docs" / REPORTS_DIR


@dataclass(slots=True)
class MigrationDecision:
    source: Path
    destination: Path


def discover_report_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in sorted(root.iterdir()):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"}:
            candidates.append(path)
    return candidates


def build_decisions(root: Path) -> list[MigrationDecision]:
    decisions: list[MigrationDecision] = []
    for path in discover_report_files(root):
        subdir = suggest_report_subdir(path.name)
        destination = REPORTS_ROOT / subdir / path.name
        decisions.append(MigrationDecision(source=path, destination=destination))
    return decisions


def apply_decisions(decisions: list[MigrationDecision], execute: bool) -> int:
    moved = 0
    for decision in decisions:
        if execute:
            decision.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(decision.source), str(decision.destination))
            print(
                f"Moved {decision.source.relative_to(PROJECT_ROOT)} -> {decision.destination.relative_to(PROJECT_ROOT)}"
            )
        else:
            print(
                f"[DRY-RUN] Would move {decision.source.relative_to(PROJECT_ROOT)} -> {decision.destination.relative_to(PROJECT_ROOT)}"
            )
        moved += 1
    return moved


def main(execute: bool = False) -> int:
    decisions = build_decisions(PROJECT_ROOT)
    print(f"Report migration candidates: {len(decisions)}")
    moved = apply_decisions(decisions, execute=execute)
    print(f"Total {'moved' if execute else 'planned'}: {moved}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate report files into docs/reports.")
    parser.add_argument("--execute", action="store_true", help="Perform the moves. Default is dry-run.")
    raise SystemExit(main(execute=parser.parse_args().execute))
