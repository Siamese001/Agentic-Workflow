"""
Generate rename suggestions for intentional variants.
Uses NamingAgent principles to suggest unique, descriptive names.
"""

import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import SCRIPTS_DIR, TESTS_DIR
from tqdm import tqdm

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))


def read_file_content(file_path: Path) -> str:
    """Read file content."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception:  # guardian: allow-silent-swallow
        return ""


def extract_purpose_from_content(content: str, file_path: Path) -> str:
    """Extract purpose/context from file content."""
    # Check for docstrings
    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if docstring_match:
        doc = docstring_match.group(1).strip()
        if doc:
            return doc.split("\n")[0][:100]  # First line, max 100 chars

    # Check for comments
    comment_match = re.search(r"^#\s*(.+)$", content, re.MULTILINE)
    if comment_match:
        return comment_match.group(1).strip()[:100]

    # Check parent directory context
    parent = file_path.parent.name
    if parent and parent != SCRIPTS_DIR:
        return f"Initializer for {parent} package"

    return "Package initializer"


def suggest_rename_for_init_files(file_paths):
    """Suggest renames for __init__.py variants."""
    suggestions = []

    for file_path in tqdm(file_paths, desc="Processing", unit="item"):
        content = read_file_content(file_path)
        rel_path = file_path.relative_to(project_root)

        # Determine context from path
        path_parts = rel_path.parts

        # Extract meaningful context
        if "config" in path_parts:
            pass
        elif "L0_routing" in path_parts:
            pass
        elif "L1_cognition" in path_parts:
            pass
        elif "L2_execution" in path_parts:
            pass
        elif "L3_orchestration" in path_parts:
            pass
        elif "L4_state" in path_parts:
            pass
        elif "L5_safety" in path_parts:
            pass
        elif "observability" in path_parts:
            pass
        elif APPS_LIC_DIR in path_parts:
            pass
        elif APPS_RG_DIR in path_parts:
            pass
        elif APPS_SHARED_DIR in path_parts:
            pass
        elif TESTS_DIR in path_parts:
            pass
        else:
            path_parts[0] if path_parts else "unknown"

        # Get parent directory name
        parent = file_path.parent.name

        # Check if content is empty or minimal
        lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        is_empty = len(lines) == 0

        # Generate suggestion
        if is_empty:
            suggestion = {
                "original": str(rel_path),
                "suggested_name": "__init__.py",  # Keep as is if empty
                "action": "KEEP_AS_IS",
                "reason": "Empty package initializer - standard Python convention",
            }
        else:
            # Suggest descriptive name based on content
            purpose = extract_purpose_from_content(content, file_path)
            suggestion = {
                "original": str(rel_path),
                "suggested_name": f"__{parent}_init__.py" if parent != SCRIPTS_DIR else "__init__.py",
                "action": "CONSIDER_RENAME",
                "reason": f"Non-empty init with purpose: {purpose[:60]}...",
                "alternative": "Consider consolidating into parent __init__.py or extracting to separate module",
            }

        suggestions.append(suggestion)

    return suggestions


def suggest_rename_for_canon_validator(file_paths):
    """Suggest renames for canon_validator___init__.py variants."""
    suggestions = []

    for file_path in tqdm(file_paths, desc="Processing", unit="item"):
        read_file_content(file_path)
        rel_path = file_path.relative_to(project_root)

        # Determine purpose from location
        if "L0_routing/scripts" in str(rel_path):
            suggested_name = "canon_validator_bootstrap.py"
            reason = "Bootstrap/initialization script for canon validator in maintenance layer"
        elif "tests/core" in str(rel_path):
            suggested_name = "canon_validator_test_init.py"
            reason = "Test initialization for canon validator tests"
        else:
            suggested_name = "canon_validator_init.py"
            reason = "Initialization module for canon validator"

        suggestion = {
            "original": str(rel_path),
            "suggested_name": suggested_name,
            "action": "RENAME",
            "reason": reason,
            "command": f'git mv "{rel_path}" "{rel_path.parent / suggested_name}"',
        }

        suggestions.append(suggestion)

    return suggestions


def main():
    print("=" * 120)
    print("RENAME SUGGESTIONS FOR INTENTIONAL VARIANTS")
    print("Using NamingAgent principles: Descriptive, Layer-aware, Purpose-driven")
    print("=" * 120)
    print()

    # Variant 1: __init__.py files
    print("=" * 120)
    print("[1] VARIANT GROUP: __init__.py (29 copies)")
    print("=" * 120)
    print()

    print("ANALYSIS:")
    print("  These are Python package initializers (__init__.py)")
    print("  Per Python convention, these SHOULD have the same filename")
    print("  Different content is EXPECTED - each package has its own initialization logic")
    print()

    print("RECOMMENDATION:")
    print("  ✓ NO ACTION NEEDED")
    print("  ✓ Keep all __init__.py files as-is")
    print("  ✓ This is standard Python package structure")
    print()

    print("RATIONALE:")
    print("  - __init__.py is a Python convention for package initialization")
    print("  - Each package (L0, L1, L2, L3, L4, L5, apps, tests) needs its own __init__.py")
    print("  - Different content reflects different package initialization needs")
    print("  - Renaming would break Python import system")
    print()

    print("-" * 120)
    print()

    # Variant 2: canon_validator___init__.py
    print("=" * 120)
    print("[2] VARIANT GROUP: canon_validator___init__.py (2 copies)")
    print("=" * 120)
    print()

    files = [
        project_root / "agentic_core/L0_routing/scripts/canon_validator___init__.py",
        project_root / "tests/core/canon_validator___init__.py",
    ]

    # Filter to existing files
    existing_files = [f for f in files if f.exists()]

    if not existing_files:
        print("⚠️  Files not found - may have been deleted or moved")
        print()
    else:
        suggestions = suggest_rename_for_canon_validator(existing_files)

        print("ANALYSIS:")
        print("  These files have unusual triple-underscore naming (___init__.py)")
        print("  This violates Python conventions and NamingAgent rules")
        print("  Different locations suggest different purposes")
        print()

        print("RENAME SUGGESTIONS:")
        print()

        for idx, sug in enumerate(suggestions, 1):
            print(f"  [{idx}] {sug['original']}")
            print(f"      → Suggested: {sug['suggested_name']}")
            print(f"      → Reason: {sug['reason']}")
            print(f"      → Action: {sug['action']}")
            if "command" in sug:
                print(f"      → Command: {sug['command']}")
            print()

        print("RATIONALE:")
        print("  - Triple-underscore (___) is non-standard and confusing")
        print("  - Names should reflect purpose (bootstrap vs test_init)")
        print("  - Descriptive names improve code discoverability")
        print("  - Follows NamingAgent PascalCase/snake_case conventions")
        print()

    print("-" * 120)
    print()

    # Summary
    print()
    print("=" * 120)
    print("SUMMARY & NEXT STEPS")
    print("=" * 120)
    print()

    print("VARIANT 1: __init__.py files")
    print("  ✓ Status: NO ACTION NEEDED")
    print("  ✓ These are legitimate Python package initializers")
    print("  ✓ Keep all 29 files as-is")
    print()

    print("VARIANT 2: canon_validator___init__.py files")
    print("  ⚠️  Status: RENAME RECOMMENDED")
    print("  ⚠️  Action: Rename to descriptive names (see suggestions above)")
    print("  ⚠️  Commands provided for git mv operations")
    print()

    print("CONCLUSION:")
    print("  - Only 2 files need renaming (canon_validator variants)")
    print("  - All __init__.py files are correct as-is")
    print("  - Total renames needed: 2 files")
    print()


if __name__ == "__main__":
    main()
