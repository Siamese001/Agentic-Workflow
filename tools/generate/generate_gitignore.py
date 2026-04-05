#!/usr/bin/env python3
"""Generate .gitignore from YAML exclusion config.

SSOT: config/excluded_paths.yaml
This script generates .gitignore entries from the canonical exclusion list.

Usage:
    python tools/generate_gitignore.py --write    # Update .gitignore
    python tools/generate_gitignore.py --check    # Verify sync (CI mode)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence


# Header for generated .gitignore
GITIGNORE_HEADER = """# Generated from config/excluded_paths.yaml
# Do not edit manually - run: python tools/generate_gitignore.py --write
# Last generated: {timestamp}

"""


def load_exclusions() -> tuple[set[str], set[str]]:
    """Load exclusions from YAML config."""
    config_path = Path(__file__).parent.parent.parent / "config" / "excluded_paths.yaml"

    try:
        import yaml
    except ImportError:
        print("Error: PyYAML required (pip install pyyaml)")
        sys.exit(1)

    if not config_path.exists():
        print(f"Error: Config not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Collect directory exclusions
    all_dirs: set[str] = set()
    categories = [
        "build_cache_dirs",
        "version_control_dirs",
        "virtual_env_dirs",
        "coverage_dirs",
        "archive_dirs",
        "ide_dirs",
        "vendor_dirs",
        "data_dirs",
        "special_dirs",
    ]

    for category in categories:
        dirs = data.get(category, [])
        if isinstance(dirs, list):
            all_dirs.update(dirs)

    # File patterns
    file_patterns = set(data.get("file_patterns", []))

    return all_dirs, file_patterns


def generate_gitignore_content(dirs: set[str], patterns: set[str]) -> str:
    """Generate .gitignore content from exclusions."""
    from datetime import datetime

    lines = [GITIGNORE_HEADER.format(timestamp=datetime.now().isoformat())]

    # Group by category for readability
    groups = {
        "Build & Cache": [],
        "Version Control": [],
        "Virtual Environments": [],
        "Coverage & Test Output": [],
        "Archives & Backups": [],
        "IDE & Editor": [],
        "Vendor Packages": [],
        "Data & Logs": [],
        "Other": [],
        "File Patterns": [],
    }

    # Categorize directories
    build_cache = {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".tox", "node_modules", "build", "dist", "_build", ".eggs"}
    version_control = {".git", ".svn", ".hg"}
    virtual_env = {".venv", "venv", "venv_stable", "env", ".env", "Lib", "site-packages"}
    coverage = {"coverage_html", "htmlcov", ".coverage", ".test_artifacts", "test_artifacts", "reports"}
    archives = {"archives", "archive", "artifacts", ".sovereign_healing_backup", ".healing_backups", ".backup", ".gravity_state"}
    ide = {".idea", ".vscode", ".windsurf", ".DS_Store"}
    vendor = {"google", "gapic", "pip", "dist-info", "licenses", "src"}
    data = {"data", "docs", "logs", "raw", "shared"}

    for d in sorted(dirs):
        if d in build_cache:
            groups["Build & Cache"].append(d)
        elif d in version_control:
            groups["Version Control"].append(d)
        elif d in virtual_env:
            groups["Virtual Environments"].append(d)
        elif d in coverage:
            groups["Coverage & Test Output"].append(d)
        elif d in archives:
            groups["Archives & Backups"].append(d)
        elif d in ide:
            groups["IDE & Editor"].append(d)
        elif d in vendor:
            groups["Vendor Packages"].append(d)
        elif d in data:
            groups["Data & Logs"].append(d)
        else:
            groups["Other"].append(d)

    # Add file patterns to their group
    groups["File Patterns"] = sorted(patterns)

    # Generate content
    for group_name, entries in groups.items():
        if not entries:
            continue
        lines.append(f"# {group_name}")
        for entry in entries:
            # Add trailing slash for directories (no dot prefix needed for gitignore)
            if not entry.startswith(".") and not entry.startswith("*"):
                lines.append(f"/{entry}/")
            elif entry.startswith("."):
                lines.append(f"{entry}/")
            else:
                lines.append(entry)
        lines.append("")

    return "\n".join(lines)


def read_current_gitignore() -> str | None:
    """Read current .gitignore content."""
    gitignore_path = Path(__file__).parent.parent.parent / ".gitignore"
    if gitignore_path.exists():
        return gitignore_path.read_text(encoding="utf-8")
    return None


def write_gitignore(content: str) -> None:
    """Write .gitignore file."""
    gitignore_path = Path(__file__).parent.parent.parent / ".gitignore"
    gitignore_path.write_text(content, encoding="utf-8")
    print(f"Updated: {gitignore_path}")


def check_sync() -> bool:
    """Check if .gitignore is in sync with YAML config."""
    dirs, patterns = load_exclusions()
    generated = generate_gitignore_content(dirs, patterns)
    current = read_current_gitignore()

    if current is None:
        print("Error: .gitignore does not exist")
        return False

    # Compare (ignore timestamp in header)
    generated_lines = generated.split("\n")[3:]  # Skip header
    current_lines = current.split("\n")[3:] if current.startswith("# Generated") else current.split("\n")

    if generated_lines == current_lines:
        print("✅ .gitignore is in sync with config/excluded_paths.yaml")
        return True
    else:
        print("❌ .gitignore is out of sync with config/excluded_paths.yaml")
        print("Run: python tools/generate_gitignore.py --write")
        return False


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate .gitignore from YAML config")
    parser.add_argument("--write", action="store_true", help="Write .gitignore file")
    parser.add_argument("--check", action="store_true", help="Check if .gitignore is in sync (CI mode)")

    args = parser.parse_args(argv)

    if args.check:
        return 0 if check_sync() else 1

    if args.write:
        dirs, patterns = load_exclusions()
        content = generate_gitignore_content(dirs, patterns)
        write_gitignore(content)
        return 0

    # Default: print to stdout
    dirs, patterns = load_exclusions()
    content = generate_gitignore_content(dirs, patterns)
    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
