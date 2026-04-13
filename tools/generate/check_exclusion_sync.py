#!/usr/bin/env python3
"""Check synchronization between excluded_paths.yaml and .pre-commit-config.yaml.

This script verifies that the pre-commit exclude patterns in .pre-commit-config.yaml
are consistent with the exclusion patterns in config/excluded_paths.yaml.

Usage:
    python tools/generate/check_exclusion_sync.py      # Check sync
    python tools/generate/check_exclusion_sync.py --fix # Generate report (future)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML required (pip install pyyaml)")
    sys.exit(1)

_REPO_ROOT = Path(__file__).parent.parent.parent


def load_excluded_paths() -> Any:
    """Load exclusions from config/excluded_paths.yaml."""
    config_path = _REPO_ROOT / "config" / "excluded_paths.yaml"

    if not config_path.exists():
        print(f"Error: Config not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_precommit_excludes() -> list[str]:
    """Load exclude patterns from .pre-commit-config.yaml."""
    precommit_path = _REPO_ROOT / ".pre-commit-config.yaml"

    if not precommit_path.exists():
        print("Error: .pre-commit-config.yaml not found")
        sys.exit(1)

    with open(precommit_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract exclude section more robustly
    # Find the exclude: | line and extract until the closing )
    exclude_start = content.find("exclude: |")
    if exclude_start == -1:
        print("Error: Could not find exclude section in .pre-commit-config.yaml")
        sys.exit(1)

    # Find the regex start
    regex_start = content.find("(?x)^(", exclude_start)
    if regex_start == -1:
        print("Error: Could not find regex pattern in exclude section")
        sys.exit(1)

    # Find the closing ) that matches the opening (?x)^(
    # We need to count parentheses to find the correct closing one
    # Start at 1 because we've already seen the opening (
    paren_count = 1
    patterns_text = ""

    for i in range(regex_start + 6, len(content)):  # Start after "(?x)^("
        char = content[i]
        if char == "(":
            paren_count += 1
        elif char == ")":
            paren_count -= 1
            if paren_count == 0:
                # Found the closing parenthesis
                patterns_text = content[regex_start + 6 : i]
                break

    if not patterns_text:
        print(f"Error: Could not parse exclude patterns (paren_count={paren_count})")
        sys.exit(1)

    # Parse patterns from regex
    patterns = []
    for line in patterns_text.split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            # Remove trailing pipe and whitespace
            patterns.append(line.rstrip("|"))

    return [p for p in patterns if p]


def normalize_pattern(pattern: str) -> str:
    """Normalize a pattern for comparison."""
    # Remove regex anchors and quantifiers for simple comparison
    pattern = pattern.replace(r"\.", ".")
    pattern = pattern.replace(r".*", "*")
    pattern = pattern.replace(r"[", "").replace("]", "")
    pattern = pattern.replace("^", "").replace("$", "")
    pattern = pattern.replace(r"/.*", "/")
    pattern = pattern.strip()
    return pattern


def compare_patterns(excluded_data: dict, precommit_patterns: list[str]) -> dict:
    """Compare patterns between excluded_paths.yaml precommit_excludes and pre-commit config."""

    # Load only precommit_excludes from YAML (not all directories/file patterns)
    precommit_excludes = set(excluded_data.get("precommit_excludes", []))

    # Normalize for comparison
    normalized_yaml = {normalize_pattern(p) for p in precommit_excludes}
    normalized_precommit = {normalize_pattern(p) for p in precommit_patterns}

    # Find differences
    in_yaml_not_precommit = normalized_yaml - normalized_precommit
    in_precommit_not_yaml = normalized_precommit - normalized_yaml
    common = normalized_yaml & normalized_precommit

    return {
        "in_yaml_not_precommit": sorted(in_yaml_not_precommit),
        "in_precommit_not_yaml": sorted(in_precommit_not_yaml),
        "common": sorted(common),
        "total_yaml": len(normalized_yaml),
        "total_precommit": len(normalized_precommit),
        "common_count": len(common),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check exclusion sync between gitignore and pre-commit")
    parser.add_argument("--fix", action="store_true", help="Generate sync report (future)")

    _ = parser.parse_args(argv)

    print("Checking exclusion synchronization...")
    print("=" * 60)

    # Load data
    excluded_data = load_excluded_paths()
    precommit_patterns = load_precommit_excludes()

    # Compare
    comparison = compare_patterns(excluded_data, precommit_patterns)

    # Report
    print(f"\nYAML precommit_excludes: {comparison['total_yaml']}")
    print(f"Pre-commit patterns: {comparison['total_precommit']}")
    print(f"Common patterns: {comparison['common_count']}")

    if comparison["in_yaml_not_precommit"]:
        print(f"\n⚠️  Patterns in YAML but NOT in pre-commit ({len(comparison['in_yaml_not_precommit'])}):")
        for p in comparison["in_yaml_not_precommit"][:20]:
            print(f"  - {p}")
        if len(comparison["in_yaml_not_precommit"]) > 20:
            print(f"  ... and {len(comparison['in_yaml_not_precommit']) - 20} more")

    if comparison["in_precommit_not_yaml"]:
        print(f"\n⚠️  Patterns in pre-commit but NOT in YAML ({len(comparison['in_precommit_not_yaml'])}):")
        for p in comparison["in_precommit_not_yaml"][:20]:
            print(f"  - {p}")
        if len(comparison["in_precommit_not_yaml"]) > 20:
            print(f"  ... and {len(comparison['in_precommit_not_yaml']) - 20} more")

    # Determine sync status
    if not comparison["in_yaml_not_precommit"] and not comparison["in_precommit_not_yaml"]:
        print("\n✅ Pre-commit exclusion patterns are in sync")
        return 0
    else:
        print("\n❌ Pre-commit exclusion patterns are out of sync")
        print("\nTo fix:")
        print("  1. Run: python tools/generate/gitignore.py --write-precommit")
        print("  2. Update .pre-commit-config.yaml exclude section with the output")
        return 1


if __name__ == "__main__":
    sys.exit(main())
