#!/usr/bin/env python3
"""Rename tests by stripping low-signal version and phase tokens from filenames.

This is a generalized replacement for one-shot hardcoded rename lists. It can
run in dry-run mode, avoids collisions, and updates Python import references to
renamed test modules when execution is enabled.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

LOW_SIGNAL_PATTERNS = [
    re.compile(r"(?:^|_)v\d+(?=_|$)", re.IGNORECASE),
    re.compile(r"(?:^|_)wave\d+(?=_|$)", re.IGNORECASE),
    re.compile(r"(?:^|_)phase\d+(?=_|$)", re.IGNORECASE),
    re.compile(r"(?:^|_)req\d+(?:_\d+)*(?=_|$)", re.IGNORECASE),
]
MULTI_UNDERSCORE_RE = re.compile(r"_+")
# SSOT: GLOBAL_EXCLUDED_DIRS covers standard tooling/cache/build dirs.
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS  # noqa: E402

SKIP_DIRS = set(GLOBAL_EXCLUDED_DIRS)


@dataclass(slots=True)
class RenameResult:
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
        if (candidate / ".git").exists() or (candidate / "tests").exists():
            return candidate
    return Path.cwd().resolve()


def _normalized_test_name(name: str) -> str:
    stem, suffix = os.path.splitext(name)
    for pattern in LOW_SIGNAL_PATTERNS:
        stem = pattern.sub("_", stem)
    stem = MULTI_UNDERSCORE_RE.sub("_", stem).strip("_")
    if not stem.startswith("test_"):
        stem = f"test_{stem}"
    return f"{stem}{suffix}"


def _module_name(project_root: Path, path: Path) -> str:
    return ".".join(path.relative_to(project_root).with_suffix("").parts)


def _update_imports(project_root: Path, old_module: str, new_module: str, *, execute: bool) -> int:
    changed_files = 0
    for path in project_root.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        updated = re.sub(rf"\b{re.escape(old_module)}\b", new_module, text)
        if updated == text:
            continue
        changed_files += 1
        if execute:
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            tmp_path.write_text(updated, encoding="utf-8")
            tmp_path.replace(path)
    return changed_files


def rename_tests(project_root: Path, *, execute: bool) -> dict[str, object]:
    results: list[RenameResult] = []
    for source in sorted((project_root / "tests").rglob("test_*.py")):
        if any(part in SKIP_DIRS for part in source.parts):
            continue
        target_name = _normalized_test_name(source.name)
        if target_name == source.name:
            continue
        target = source.with_name(target_name)
        if target.exists():
            results.append(RenameResult(str(source), str(target), 0, "skip", "target already exists"))
            continue
        changed_import_files = _update_imports(
            project_root,
            _module_name(project_root, source),
            _module_name(project_root, target),
            execute=execute,
        )
        if execute:
            source.replace(target)
            action = "rename"
        else:
            action = "would_rename"
        results.append(
            RenameResult(str(source), str(target), changed_import_files, action, "removed low-signal tokens")
        )

    return {
        "project_root": str(project_root),
        "execute": execute,
        "renames": [asdict(item) for item in results],
        "count": len(results),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Apply renames and import updates.")
    parser.add_argument("--report", help="Optional JSON report path.")
    args = parser.parse_args(argv)

    project_root = _resolve_project_root()
    report = rename_tests(project_root, execute=args.execute)

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
