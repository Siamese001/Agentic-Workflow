"""
Wave 0B: Categorized restore from .healing_backups/

Restores files that were unintentionally archived by the healing pipeline into
.healing_backups/ during the run11 archiving event.

Category routing:
  1. test_*.py          -> tests/_quarantine/restored_tests/
  2. PascalCase*Agent.py -> <inferred-layer>/reasoning/   (apps_rg, apps_lic, agentic_core)
  3. snake_case*.py     -> tests/_quarantine/restored_snake_case/  (manual triage)
  4. __init__.py        -> original package path (strip timestamp suffix from backup name)
  5. naming_violations/ -> HOLD — do not auto-restore

Run:
    python -m ops_scripts.general.restore_from_healing_backup [--dry-run] [--backup-root PATH]

AST analysis is used for category inference. No heuristics on file content patterns.
"""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L5_SAFETY_DIR,
    TESTS_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
DEFAULT_BACKUP_ROOT = PROJECT_ROOT / ".healing_backups"

# Destination roots for each category
DEST_QUARANTINE_TESTS = PROJECT_ROOT / TESTS_DIR / "_quarantine" / "restored_tests"
DEST_QUARANTINE_SNAKE = PROJECT_ROOT / TESTS_DIR / "_quarantine" / "restored_snake_case"

LAYER_ROOTS = [
    PROJECT_ROOT / APPS_RG_DIR,
    PROJECT_ROOT / APPS_LIC_DIR,
    PROJECT_ROOT / APPS_SHARED_DIR,
    PROJECT_ROOT / L5_SAFETY_DIR,
    PROJECT_ROOT / L1_COGNITION_DIR,
    PROJECT_ROOT / L2_EXECUTION_DIR,
    PROJECT_ROOT / L3_ORCHESTRATION_DIR,
    PROJECT_ROOT / L0_ROUTING_DIR,
]

PASCAL_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*Agent\.py$")
SNAKE_RE = re.compile(r"^[a-z_][a-z0-9_]*\.py$")
INIT_RE = re.compile(r"^__init__(\.py|\.[0-9]+\.py)$")
NAMING_VIOLATION_RE = re.compile(r"^naming_violations[/\\]")


def _infer_agent_layer(py_path: Path) -> Path | None:
    """Use AST to detect the primary base class and infer layer root."""
    try:
        src = py_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except Exception:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for base in node.bases:
            base_name = ""
            if isinstance(base, ast.Attribute):
                base_name = base.attr
            elif isinstance(base, ast.Name):
                base_name = base.id
            if APPS_RG_DIR in src and APPS_LIC_DIR not in src:
                return PROJECT_ROOT / APPS_RG_DIR / "reasoning"
            if APPS_LIC_DIR in src and APPS_RG_DIR not in src:
                return PROJECT_ROOT / APPS_LIC_DIR / "reasoning"
    # Default: agentic_core L5_safety (most archived agents were there)
    return PROJECT_ROOT / L5_SAFETY_DIR / "reasoning"


def _strip_timestamp_suffix(name: str) -> str:
    """Remove trailing .YYYYMMDDHHMMSS timestamp from backup filenames."""
    return re.sub(r"\.\d{14}$", "", name)


def _categorize(path: Path, rel: Path) -> tuple[str, Path | None]:
    """
    Returns (category, destination_path).

    Categories:
      TEST, AGENT, SNAKE, INIT, NAMING_VIOLATION, UNKNOWN
    """
    name = path.name
    rel_str = str(rel)

    if NAMING_VIOLATION_RE.match(rel_str):
        return "NAMING_VIOLATION", None

    if INIT_RE.match(name):
        clean_name = _strip_timestamp_suffix(name)
        # Best-effort: place into same relative directory minus the backup prefix
        parts = rel.parts[1:]  # strip the first backup subfolder
        if parts:
            dest = PROJECT_ROOT.joinpath(*parts[:-1]) / clean_name
        else:
            dest = PROJECT_ROOT / clean_name
        return "INIT", dest

    if name.startswith("test_") and name.endswith(".py"):
        return "TEST", DEST_QUARANTINE_TESTS / name

    if PASCAL_RE.match(name):
        layer = _infer_agent_layer(path)
        dest = (layer or PROJECT_ROOT / L5_SAFETY_DIR / "reasoning") / name
        return "AGENT", dest

    if SNAKE_RE.match(name) and name.endswith(".py"):
        return "SNAKE", DEST_QUARANTINE_SNAKE / name

    return "UNKNOWN", DEST_QUARANTINE_SNAKE / name


def restore(backup_root: Path = DEFAULT_BACKUP_ROOT, dry_run: bool = True) -> dict:
    """Main restore driver. Returns summary dict."""
    if not backup_root.exists():
        print(f"ERROR: Backup root not found: {backup_root}")
        return {"error": f"backup root not found: {backup_root}"}

    summary: dict[str, list[str]] = {
        "TEST": [],
        "AGENT": [],
        "SNAKE": [],
        "INIT": [],
        "NAMING_VIOLATION": [],
        "UNKNOWN": [],
        "SKIPPED_EXISTS": [],
        "ERROR": [],
    }

    all_py = list(backup_root.rglob("*.py"))
    print(f"[restore] Scanning {len(all_py)} .py files under {backup_root.name}/")

    for src_path in all_py:
        try:
            rel = src_path.relative_to(backup_root)
        except ValueError:
            continue

        category, dest = _categorize(src_path, rel)

        if category == "NAMING_VIOLATION" or dest is None:
            summary["NAMING_VIOLATION"].append(str(rel))
            print(f"  HOLD [naming_violation]: {rel}")
            continue

        if dest.exists():
            summary["SKIPPED_EXISTS"].append(str(rel))
            print(f"  SKIP [exists]: {rel} -> {dest.relative_to(PROJECT_ROOT)}")
            continue

        print(f"  {category}: {rel} -> {dest.relative_to(PROJECT_ROOT)}")
        summary[category].append(str(rel))

        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest)

    print("\n[restore] Summary:")
    for cat, items in summary.items():
        if items:
            print(f"  {cat}: {len(items)}")

    if dry_run:
        print("\n[restore] DRY-RUN: no files written. Pass --no-dry-run to apply.")

    return {k: len(v) for k, v in summary.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Wave 0B: restore files from .healing_backups/")
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=DEFAULT_BACKUP_ROOT,
        help="Path to .healing_backups/ directory",
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        default=False,
        help="Actually copy files (default is dry-run)",
    )
    args = parser.parse_args()
    result = restore(backup_root=args.backup_root, dry_run=not args.no_dry_run)
    errors = result.get("ERROR", 0)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
