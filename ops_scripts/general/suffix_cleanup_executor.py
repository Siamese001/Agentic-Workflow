#!/usr/bin/env python3
"""Rename Python files to normalized snake_case and update import references.

The script defaults to dry-run mode and writes a JSON report describing each
planned or executed rename. It is intentionally conservative and skips files
when a rename would collide with an existing path.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)

# SSOT: GLOBAL_EXCLUDED_DIRS covers standard tooling/cache/build dirs.
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS  # noqa: E402

DEFAULT_SKIP_DIRS = set(GLOBAL_EXCLUDED_DIRS)
CAMEL_BOUNDARY_1 = re.compile(r"(.)([A-Z][a-z]+)")
CAMEL_BOUNDARY_2 = re.compile(r"([a-z0-9])([A-Z])")
MULTI_UNDERSCORE_RE = re.compile(r"_+")


@dataclass(slots=True)
class RenamePlan:
    source: str
    target: str
    changed_import_files: int
    action: str
    reason: str


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / "agentic_core").exists():
            return candidate

    return Path.cwd().resolve()


def to_smart_snake_case(name: str) -> str:
    stem, suffix = os.path.splitext(name)
    stem = stem.replace("-", "_").replace(" ", "_")
    stem = CAMEL_BOUNDARY_1.sub(r"\1_\2", stem)
    stem = CAMEL_BOUNDARY_2.sub(r"\1_\2", stem)
    stem = MULTI_UNDERSCORE_RE.sub("_", stem).strip("_").lower()
    return f"{stem}{suffix}" if stem else name


def _module_name_from_path(project_root: Path, path: Path) -> str:
    relative = path.relative_to(project_root).with_suffix("")
    return ".".join(relative.parts)


def _should_scan_file(path: Path) -> bool:
    return (
        path.is_file() and path.suffix == ".py" and not any(part in DEFAULT_SKIP_DIRS for part in path.parts)
    )


def _update_imports_in_text(text: str, old_module: str, new_module: str) -> tuple[str, bool]:
    patterns = [
        (rf"(?m)^(\s*from\s+){re.escape(old_module)}(\s+import\s+)", rf"\1{new_module}\2"),
        (rf"(?m)^(\s*import\s+){re.escape(old_module)}(\b)", rf"\1{new_module}\2"),
        (rf"\b{re.escape(old_module)}\b", new_module),
    ]

    updated = text
    changed = False
    for pattern, replacement in patterns:
        updated, count = re.subn(pattern, replacement, updated)
        changed = changed or count > 0
    return updated, changed


def _atomic_write(path: Path, content: str) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def rename_file_and_refactor(
    source_path: Path, target_path: Path, project_root: Path, *, execute: bool
) -> int:
    old_module = _module_name_from_path(project_root, source_path)
    new_module = _module_name_from_path(project_root, target_path)
    changed_import_files = 0

    for candidate in project_root.rglob("*.py"):
        if not _should_scan_file(candidate):
            continue
        text = candidate.read_text(encoding="utf-8", errors="replace")
        updated_text, changed = _update_imports_in_text(text, old_module, new_module)
        if not changed:
            continue
        changed_import_files += 1
        if execute:
            _atomic_write(candidate, updated_text)

    if execute:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.replace(target_path)

    return changed_import_files


def execute_suffix_cleanup(
    project_root: Path, *, execute: bool, explicit_files: list[str] | None
) -> dict[str, object]:
    candidates = (
        [Path(item).expanduser().resolve() for item in explicit_files]
        if explicit_files
        else [path for path in project_root.rglob("*.py") if _should_scan_file(path)]
    )

    plans: list[RenamePlan] = []
    renamed = 0
    skipped = 0
    for source_path in sorted(candidates):
        target_name = to_smart_snake_case(source_path.name)
        if target_name == source_path.name:
            continue

        target_path = source_path.with_name(target_name)
        if target_path.exists() and target_path != source_path:
            skipped += 1
            plans.append(RenamePlan(str(source_path), str(target_path), 0, "skip", "target already exists"))
            continue

        changed_import_files = rename_file_and_refactor(
            source_path, target_path, project_root, execute=execute
        )
        action = "rename" if execute else "would_rename"
        reason = "normalized filename to snake_case"
        plans.append(RenamePlan(str(source_path), str(target_path), changed_import_files, action, reason))
        renamed += 1

    return {
        "project_root": str(project_root),
        "execute": execute,
        "renamed": renamed,
        "skipped": skipped,
        "plans": [asdict(plan) for plan in plans],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Optional explicit files to rename.")
    parser.add_argument("--execute", action="store_true", help="Apply the rename and import rewrites.")
    parser.add_argument("--report", help="Optional JSON report output path.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    project_root = _resolve_project_root()
    report = execute_suffix_cleanup(project_root, execute=args.execute, explicit_files=args.files or None)
    LOGGER.info("planned_or_renamed=%s skipped=%s", report["renamed"], report["skipped"])

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        LOGGER.info("Wrote report to %s", report_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
