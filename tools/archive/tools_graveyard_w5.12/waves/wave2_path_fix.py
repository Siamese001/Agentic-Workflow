#!/usr/bin/env python3
"""Wave 2: Path normalization fix script

Replaces string-based path manipulation with pathlib.Path operations.
Focuses on critical files identified in Wave 1 audit.
"""

import re
from pathlib import Path

# Files to fix (from Wave 1 audit - critical and high risk)
TARGET_FILES = [
    "agentic_core/L0_routing/utils/complexity_visitor_util.py",
    "agentic_core/L0_routing/scripts/debug_invocation_pipeline_util.py",
    "agentic_core/L0_routing/scripts/_ssot_phases.py",
    "agentic_core/L0_routing/scripts/full_agent_discovery.py",
    "agentic_core/L0_routing/scripts/_ssot_routing.py",
    "agentic_core/L0_routing/scripts/_ssot_validation_artifacts.py",
    "agentic_core/L0_routing/utils/path_util.py",
]


def fix_path_normalization(content: str, file_path: str) -> tuple[str, list[str]]:
    """Fix path normalization patterns in content.

    Returns:
        Tuple of (fixed_content, list_of_changes)
    """
    changes = []
    original = content

    # Pattern 1: str(path).replace("\\", "/") -> path.as_posix()
    # But only when path is already a Path object
    pattern1 = r'str\((\w+)\)\.replace\(["\']\\\\\\\\["\'], ["\']\/["\']\)'
    matches = re.finditer(pattern1, content)
    for match in matches:
        var_name = match.group(1)
        old = match.group(0)
        new = f"{var_name}.as_posix()"
        content = content.replace(old, new)
        changes.append(f"Replaced '{old}' with '{new}'")

    # Pattern 2: path_str.replace("\\", "/") - keep if path_str is string
    # Pattern 3: .replace(chr(92), '/') -> .as_posix() when used on Path
    pattern3 = r'\.replace\(chr\(92\), ["\']\/["\']\)'
    matches = re.finditer(pattern3, content)
    for match in matches:
        old = match.group(0)
        # This is harder to auto-fix, just flag it
        changes.append(f"FLAG: chr(92) replacement at line {content[: match.start()].count(chr(10)) + 1}")

    return content, changes


def apply_fixes():
    """Apply fixes to target files."""
    results = []

    for rel_path in TARGET_FILES:
        file_path = Path(rel_path)
        if not file_path.exists():
            results.append({"file": rel_path, "status": "not_found"})
            continue

        try:
            original = file_path.read_text(encoding="utf-8")
            fixed, changes = fix_path_normalization(original, rel_path)

            # Only write if changes were made
            if changes and fixed != original:
                # Create backup
                backup_path = file_path.with_suffix(".py.bak_w2")
                backup_path.write_text(original, encoding="utf-8")

                # Write fixed content
                file_path.write_text(fixed, encoding="utf-8")
                results.append(
                    {
                        "file": rel_path,
                        "status": "fixed",
                        "changes": changes,
                        "backup": str(backup_path),
                    }
                )
            else:
                results.append(
                    {
                        "file": rel_path,
                        "status": "no_changes_needed",
                        "changes": changes,
                    }
                )
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            results.append(
                {
                    "file": rel_path,
                    "status": "error",
                    "error": str(e),
                }
            )

    return results


def main():
    print("Wave 2: Path Normalization Fix")
    print("=" * 50)

    results = apply_fixes()

    fixed_count = sum(1 for r in results if r.get("status") == "fixed")
    error_count = sum(1 for r in results if r.get("status") == "error")

    print("\nResults:")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total processed: {len(results)}")

    print("\nDetails:")
    for r in results:
        print(f"  {r['file']}: {r['status']}")
        if "changes" in r and r["changes"]:
            for change in r["changes"][:3]:  # Show first 3 changes
                print(f"    - {change}")


if __name__ == "__main__":
    main()
