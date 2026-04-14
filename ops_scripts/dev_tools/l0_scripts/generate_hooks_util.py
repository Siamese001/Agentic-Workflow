"""Generate a simple pre-commit configuration from the current repository structure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def generate_sovereign_list(project_root: Path | None = None) -> list[str]:
    project_root = project_root or _find_project_root()
    roots = []
    for child in sorted(project_root.iterdir()):
        if not child.is_dir() or child.name.startswith("__") or child.name == "tests":
            continue
        roots.append(child.name)
    return roots


def render_pre_commit_config(project_root: Path | None = None) -> str:
    project_root = project_root or _find_project_root()
    roots = generate_sovereign_list(project_root)
    roots_pattern = "|".join(roots) if roots else ".*"
    return f"""repos:\n  - repo: local\n    hooks:\n      - id: python-compile-check\n        name: python-compile-check\n        entry: python -m py_compile\n        language: system\n        files: ^({roots_pattern})/.*\\.py$\n      - id: trailing-whitespace\n        name: trailing-whitespace\n        entry: trailing-whitespace-fixer\n        language: system\n        files: ^({roots_pattern})/\n"""


def sync_pre_commit(*, dry_run: bool = False, output_path: Path | None = None) -> bool:
    project_root = _find_project_root()
    config_path = output_path or project_root / ".pre-commit-config.yaml"
    content = render_pre_commit_config(project_root)
    print(f"Config target: {config_path}")
    if dry_run:
        print(content)
        return True
    config_path.write_text(content, encoding="utf-8")
    print(f"Wrote {config_path}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a simple pre-commit configuration from repo roots")
    parser.add_argument("--dry-run", action="store_true", help="Print the config instead of writing it")
    parser.add_argument("--list", action="store_true", help="List current sovereign roots")
    parser.add_argument("--output", type=Path, help="Optional output path for the config file")
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    if args.list:
        for item in generate_sovereign_list(project_root):
            print(item)
        return 0
    success = sync_pre_commit(dry_run=args.dry_run, output_path=args.output)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
