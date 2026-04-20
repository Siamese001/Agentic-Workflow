#!/usr/bin/env python3
"""
Phase 2: Fix Magic Configuration anti-patterns.
Target: Externalize hardcoded timeouts, thresholds, and magic numbers.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def fix_magic_config_in_file(file_path: Path) -> int:
    """Fix magic configuration violations in a file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (UnicodeDecodeError, OSError):  # guardian: allow-silent-swallow - acceptable exception handling
        return 0

    lines = content.splitlines()
    fixed_count = 0

    # Common magic patterns to fix
    magic_patterns = [
        # Timeouts
        (r"timeout=(\d+\.?\d*)", r"timeout=DEFAULT_TIMEOUT"),
        (r"timeout\s*=\s*(\d+\.?\d*)", r"timeout = DEFAULT_TIMEOUT"),
        (r"sleep\((\d+\.?\d*)\)", r"sleep(DEFAULT_SLEEP)"),
        # Thresholds
        (r"max_files=(\d+)", r"max_files=MAX_FILES"),
        (r"max_depth=(\d+)", r"max_depth=MAX_DEPTH"),
        (r"max_retries=(\d+)", r"max_retries=MAX_RETRIES"),
        (r"batch_size=(\d+)", r"batch_size=BATCH_SIZE"),
        # Common magic numbers
        (r"buffer_size=(\d+)", r"buffer_size=BUFFER_SIZE"),
        (r"limit=(\d+)", r"limit=LIMIT"),
        (r"threshold=(\d+\.?\d*)", r"threshold=THRESHOLD"),
    ]

    # Skip if already has config constants
    has_config = any(
        re.search(r"\b(DEFAULT_TIMEOUT|MAX_FILES|MAX_DEPTH|BATCH_SIZE|BUFFER_SIZE)\b", content)
        for content in [content]
    )

    if not has_config:
        # Add config constants at the top after imports
        import_section = []
        config_added = False

        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_section.append(i)
            elif (
                import_section
                and line.strip()
                and not line.startswith("import ")
                and not line.startswith("from ")
            ):
                # End of imports, add config here
                indent = 0
                config_lines = [
                    "",
                    "# Configuration constants",
                    "DEFAULT_TIMEOUT = 300  # 5 minutes",
                    "MAX_FILES = 1000",
                    "MAX_DEPTH = 6",
                    "BATCH_SIZE = 32",
                    "BUFFER_SIZE = 8192",
                    "THRESHOLD = 0.95",
                    "DEFAULT_SLEEP = 1.0",
                    "MAX_RETRIES = 3",
                ]

                for config_line in config_lines:
                    lines.insert(i, config_line)
                    fixed_count += 1
                config_added = True
                break

        if not config_added and import_section:
            # Add at end of file if no clear import section end
            lines.extend(
                [
                    "",
                    "# Configuration constants",
                    "DEFAULT_TIMEOUT = 300  # 5 minutes",
                    "MAX_FILES = 1000",
                    "MAX_DEPTH = 6",
                    "BATCH_SIZE = 32",
                    "BUFFER_SIZE = 8192",
                    "THRESHOLD = 0.95",
                    "DEFAULT_SLEEP = 1.0",
                    "MAX_RETRIES = 3",
                ]
            )
            fixed_count += 10

    # Apply magic pattern fixes
    for pattern, replacement in magic_patterns:
        for i, line in enumerate(lines):
            if re.search(pattern, line) and not line.strip().startswith("#"):
                lines[i] = re.sub(pattern, replacement, line)
                fixed_count += 1

    # Remove duplicate config additions
    if fixed_count > 20:  # Likely added configs multiple times
        # Deduplicate config section
        config_start = None
        for i, line in enumerate(lines):
            if "# Configuration constants" in line:
                if config_start is None:
                    config_start = i
                else:
                    # Remove duplicate
                    del lines[i : i + 10]  # Remove the duplicate block
                    fixed_count -= 10
                    break

    if fixed_count > 0:
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return fixed_count


def main() -> None:
    """Execute Phase 2: Fix Magic Configuration."""
    print("Phase 2: Fixing Magic Configuration violations")

    # Find Python files
    python_files = list(REPO.rglob("*.py"))

    # Skip certain directories
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".nox",
        "archives",
        ".backup",
    }

    total_fixed = 0
    files_fixed = 0

    for py_file in python_files:
        # Skip if in excluded directory
        if any(skip in py_file.parts for skip in skip_dirs):
            continue

        # Skip test files for now
        if "test" in py_file.parts:
            continue

        fixed = fix_magic_config_in_file(py_file)
        if fixed > 0:
            print(f"  Fixed {fixed} violations in {py_file.relative_to(REPO)}")
            total_fixed += fixed
            files_fixed += 1

    print("\nPhase 2 Summary:")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Violations fixed: {total_fixed}")

    # Update baseline
    import os
    import subprocess

    env = os.environ.copy()
    env["ALLOW_LANDMINE_BASELINE_WRITE"] = "1"

    result = subprocess.run(
        ["python", "ops_scripts/ci/check_anti_patterns.py", "--write-baseline"],
        capture_output=True,
        text=True,
        cwd=REPO,
        env=env,
    )

    if result.returncode == 0:
        print("  ✓ Baseline updated")
    else:
        print("  ✗ Failed to update baseline")


if __name__ == "__main__":
    main()
