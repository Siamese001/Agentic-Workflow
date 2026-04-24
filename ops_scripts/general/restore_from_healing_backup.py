#!/usr/bin/env python3
"""Restore files from ``.healing_backups`` into safe quarantine or inferred targets.

Defaults to dry-run mode. The script copies backups back into the repository,
keeps the original backup files in place, and avoids overwriting existing files
unless explicitly requested.
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import os
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)

try:
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR as _AGENTIC_CORE_DIR,
        APPS_LIC_DIR as _APPS_LIC_DIR,
        APPS_RG_DIR as _APPS_RG_DIR,
        APPS_SHARED_DIR as _APPS_SHARED_DIR,
        TESTS_DIR as _TESTS_DIR,
    )
except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
    _AGENTIC_CORE_DIR = "agentic_core"
    _APPS_LIC_DIR = "apps_lic"
    _APPS_RG_DIR = "apps_rg"
    _APPS_SHARED_DIR = "apps_shared"
    _TESTS_DIR = "tests"

TIMESTAMP_SUFFIX_RE = re.compile(r"(?:[_-]?\d{8,14})+$")
CLASS_NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9_]*$")


@dataclass(slots=True)
class RestoreAction:
    source: str
    destination: str
    category: str
    action: str
    reason: str


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / _AGENTIC_CORE_DIR).exists():
            return candidate

    return Path.cwd().resolve()


def _strip_timestamp_suffix(name: str) -> str:
    stem, suffix = os.path.splitext(name)
    stem = TIMESTAMP_SUFFIX_RE.sub("", stem)
    return f"{stem}{suffix}"


def _iter_backup_files(backup_root: Path) -> list[Path]:
    if not backup_root.exists():
        return []
    return sorted(path for path in backup_root.rglob("*.py") if path.is_file())


def _read_ast(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return None


def _infer_agent_destination(project_root: Path, file_path: Path) -> Path:
    tree = _read_ast(file_path)
    if tree is None:
        return (
            project_root
            / _TESTS_DIR
            / "_quarantine"
            / "restored_agents"
            / _strip_timestamp_suffix(file_path.name)
        )

    imported_names: set[str] = set()
    base_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported_names.add(module)
        elif isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.add(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.add(base.attr)

    layer_map = {
        "L0": "L0_routing",
        "L1": "L1_cognition",
        "L2": "L2_execution",
        "L3": "L3_orchestration",
        "L4": "L4_state",
        "L5": "L5_safety",
        "L6": "L6_observability",
    }

    for token, layer_dir in layer_map.items():
        if any(token in value for value in imported_names | base_names):
            return (
                project_root
                / _AGENTIC_CORE_DIR
                / layer_dir
                / "reasoning"
                / _strip_timestamp_suffix(file_path.name)
            )

    file_name = _strip_timestamp_suffix(file_path.name)
    if file_name.startswith("RG"):
        return project_root / _APPS_RG_DIR / "agents" / file_name
    if file_name.startswith("LIC"):
        return project_root / _APPS_LIC_DIR / "agents" / file_name
    if file_name.startswith("SHARED"):
        return project_root / _APPS_SHARED_DIR / "agents" / file_name

    return project_root / _TESTS_DIR / "_quarantine" / "restored_agents" / file_name


def _categorize(project_root: Path, backup_root: Path, file_path: Path) -> tuple[str, Path | None, str]:
    relative = file_path.relative_to(backup_root)
    normalized_name = _strip_timestamp_suffix(file_path.name)
    normalized_relative = Path(*relative.parts[:-1], normalized_name)
    relative_posix = relative.as_posix().lower()

    if "naming_violations" in relative_posix:
        return "hold", None, "naming_violations backup requires manual review"

    if normalized_name == "__init__.py":
        return "package_init", project_root / normalized_relative, "restoring package init file"

    if normalized_name.startswith("test_"):
        destination = project_root / _TESTS_DIR / "_quarantine" / "restored_tests" / normalized_name
        return "test", destination, "test file restored to quarantine"

    stem = Path(normalized_name).stem
    if CLASS_NAME_RE.match(stem) and stem.endswith("Agent"):
        return (
            "agent",
            _infer_agent_destination(project_root, file_path),
            "agent restored to inferred territory",
        )

    destination = project_root / _TESTS_DIR / "_quarantine" / "restored_snake_case" / normalized_name
    return "snake_case", destination, "non-agent Python file restored to quarantine"


def _copy_file(source: Path, destination: Path, overwrite: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {destination}")

    temp_destination = destination.with_suffix(destination.suffix + ".tmp")
    shutil.copy2(source, temp_destination)
    temp_destination.replace(destination)


def restore(
    project_root: Path,
    backup_root: Path,
    *,
    execute: bool,
    overwrite: bool,
    delete_source: bool,
) -> dict[str, object]:
    actions: list[RestoreAction] = []
    restored = 0
    skipped = 0
    held = 0
    errors = 0

    for source in _iter_backup_files(backup_root):
        category, destination, reason = _categorize(project_root, backup_root, source)
        if destination is None:
            actions.append(RestoreAction(str(source), "", category, "hold", reason))
            held += 1
            continue

        action_name = "restore" if execute else "would_restore"
        try:
            if execute:
                _copy_file(source, destination, overwrite=overwrite)
                if delete_source:
                    source.unlink()
                restored += 1
            else:
                skipped += 1
            actions.append(RestoreAction(str(source), str(destination), category, action_name, reason))
        except OSError as exc:
            actions.append(RestoreAction(str(source), str(destination), category, "error", str(exc)))
            errors += 1

    return {
        "backup_root": str(backup_root),
        "project_root": str(project_root),
        "execute": execute,
        "overwrite": overwrite,
        "delete_source": delete_source,
        "restored": restored,
        "planned": skipped,
        "held": held,
        "errors": errors,
        "actions": [asdict(action) for action in actions],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-root", help="Override backup root path.")
    parser.add_argument("--execute", action="store_true", help="Perform file copies.")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting destination files.")
    parser.add_argument(
        "--delete-source", action="store_true", help="Delete backup files after successful copy."
    )
    parser.add_argument("--report", help="Optional JSON report output path.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    project_root = _resolve_project_root()
    backup_root = (
        Path(args.backup_root).expanduser().resolve()
        if args.backup_root
        else project_root / ".healing_backups"
    )

    if not backup_root.exists():
        LOGGER.error("Backup root not found: %s", backup_root)
        return 2

    report = restore(
        project_root,
        backup_root,
        execute=args.execute,
        overwrite=args.overwrite,
        delete_source=args.delete_source,
    )

    LOGGER.info(
        "planned=%s restored=%s held=%s errors=%s",
        report["planned"],
        report["restored"],
        report["held"],
        report["errors"],
    )

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        LOGGER.info("Wrote report to %s", report_path)

    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
