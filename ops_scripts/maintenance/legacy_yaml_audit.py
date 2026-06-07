"""Legacy policy/threshold YAML deprecation audit.

Plan: `docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-residual-a2d9c7.md` W4.P1.

Scans the repo for legacy configuration files matching deprecated
naming patterns (`*_policies.yaml`, `*_thresholds.yaml`) and emits a
JSON report of migration candidates to the canonical `config/domain_contract/`
SSOT.

This is a READ-ONLY audit. It never deletes or modifies files.
Actual deletion requires its own Author-Gate plan.

Usage
-----
    python ops_scripts/maintenance/legacy_yaml_audit.py \
        --root . \
        --out artifacts/maintenance/legacy_yaml_audit.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

Logger = logging.getLogger(__name__)

# Directories excluded from the scan (archives, vendor, build output).
EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "archives",
        "__pycache__",
        "artifacts",
        "docs/archive/windsurf/legacy-tree",
    }
)

# Filename patterns considered legacy.
LEGACY_SUFFIXES: tuple[str, ...] = ("_policies.yaml", "_thresholds.yaml")


@dataclass(frozen=True)
class LegacyFile:
    path: str
    size_bytes: int
    app_hint: str  # inferred app id from path, or "" if ambiguous


@dataclass
class AuditReport:
    total_files_found: int = 0
    legacy_files: List[LegacyFile] = field(default_factory=list)
    excluded_dirs: List[str] = field(default_factory=lambda: sorted(EXCLUDED_DIRS))


def _infer_app_hint(path: Path) -> str:
    for part in path.parts:
        if part.startswith("apps_"):
            return part
    return ""


def _is_excluded(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRS for part in rel_parts)


def scan(root: Path) -> AuditReport:
    """Walk the repo from root and collect legacy YAML files."""
    report = AuditReport()
    if not root.is_dir():
        raise FileNotFoundError(f"root not a directory: {root}")
    for candidate in root.rglob("*.yaml"):
        if _is_excluded(candidate, root):
            continue
        name = candidate.name
        if not any(name.endswith(suffix) for suffix in LEGACY_SUFFIXES):
            continue
        try:
            size = candidate.stat().st_size
        except OSError as exc:
            Logger.warning("cannot stat %s: %s", candidate, exc)
            size = -1
        rel = candidate.relative_to(root).as_posix()
        report.legacy_files.append(
            LegacyFile(path=rel, size_bytes=size, app_hint=_infer_app_hint(candidate))
        )
    report.legacy_files.sort(key=lambda lf: lf.path)
    report.total_files_found = len(report.legacy_files)
    return report


def report_to_dict(report: AuditReport) -> dict:
    return {
        "total_files_found": report.total_files_found,
        "legacy_suffixes": list(LEGACY_SUFFIXES),
        "excluded_dirs": report.excluded_dirs,
        "legacy_files": [asdict(lf) for lf in report.legacy_files],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit legacy policy/threshold YAMLs")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=None, help="Optional JSON output path")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    report = scan(args.root.resolve())
    payload = report_to_dict(report)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {report.total_files_found} legacy files -> {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
