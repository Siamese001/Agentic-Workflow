#!/usr/bin/env python3
"""
File Classification Analysis Script - Refined Version
Runs classification analysis on SSOT-approved folders and generates detailed report.

FOCUS: Only flag actual naming violations, avoid false positives.
- SCRIPT: PascalCase files in ops_scripts/ or scripts/ should be snake_case
- TEST: Files in tests/ without test_ prefix
- MIXIN: Files with Mixin in class name but PascalCase filename
- Avoid flagging: Errors, Strategies, Validators, Guardrails, etc. as needing Agent suffix
"""

import ast
import json
import os
import re
from pathlib import Path
from typing import Any


def get_python_files_fast(root: Path) -> list[Path]:
    """Optimized repository scanner that prunes heavy directories"""
    python_files = []
    exclude_dirs = {
        ".git",
        "archives",
        "__pycache__",
        "node_modules",
        "venv",
        ".env",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith(".py"):
                python_files.append(Path(dirpath) / filename)
    return python_files


def classify_file(path: Path) -> str:
    """
    Classify file by type — delegates to the classification kernel (SSOT).

    [REFACTORED 2026-02-08] Removed 130-line reimplementation.
    Now delegates to the zero-dependency classification kernel for
    consistent results across all tools.

    This script's purpose is to flag naming violations, so it wraps the
    kernel result to determine if a file needs renaming or not.
    """
    from agentic_core.core.classification_kernel import classify_file_standalone

    file_type = classify_file_standalone(path)

    # This script only cares about files that need naming fixes.
    # Most types are already compliant — only flag actionable violations.
    if file_type in ("AGENT", "ORCHESTRATOR", "STRATEGY", "ADAPTER", "VALIDATOR",
                     "EXCEPTION", "CONFIG", "FACTORY", "SERVICE", "ENGINE",
                     "TYPES", "CLASS", "UTILITY", "STUB", "IGNORE"):
        # Check if SCRIPT needs PascalCase→snake_case conversion
        pass

    if file_type == "SCRIPT":
        # Only flag if it's PascalCase (needs conversion to snake_case)
        if re.match(r"^[A-Z]", path.stem):
            return "SCRIPT"
        return "IGNORE"

    if file_type == "TEST":
        # Only flag if missing test_ prefix
        if path.name.startswith("test_") or path.name.endswith("_test.py"):
            return "IGNORE"
        return "TEST"

    if file_type == "MIXIN":
        # Only flag if filename is PascalCase (not already snake_case)
        if re.match(r"^[A-Z]", path.stem) and not path.stem.islower():
            return "MIXIN"
        return "IGNORE"

    if file_type == "PROTOCOL":
        return "PROTOCOL"

    if file_type == "GATEWAY":
        return "GATEWAY"

    return "IGNORE"


def get_compliant_name(path: Path, file_type: str) -> str | None:
    """Get compliant name for file based on type"""
    if file_type in {"IGNORE", "TYPES", "UTILITY", "PROTOCOL", "GATEWAY"}:
        return None

    if file_type == "SCRIPT":
        # Convert PascalCase to snake_case
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", path.stem).lower().replace("__", "_")
        return f"{snake}.py" if f"{snake}.py" != path.name else None

    if file_type == "TEST":
        # Add test_ prefix and convert to snake_case
        stem = path.stem
        if stem.startswith("test_"):
            return None  # Already compliant
        # Convert PascalCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", stem)
        clean = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        return f"test_{clean}.py" if f"test_{clean}.py" != path.name else None

    if file_type == "MIXIN":
        stem = path.stem
        # Check if already snake_case with _mixin suffix
        if stem.islower() and stem.endswith("_mixin"):
            return None  # Already compliant
        # Convert PascalCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", stem)
        clean_stem = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        if not clean_stem.endswith("_mixin"):
            clean_stem += "_mixin"
        target = f"{clean_stem}.py"
        return target if target != path.name else None

    return None


def find_imports_to_update(
    project_root: Path,
    old_name: str,
    new_name: str,
) -> list[dict[str, Any]]:
    """Find all files that import the old module name"""
    old_mod = old_name.replace(".py", "")
    new_mod = new_name.replace(".py", "")

    import_updates = []
    python_files = get_python_files_fast(project_root)

    for path in python_files:
        try:
            content = path.read_text(encoding="utf-8")
            if old_mod not in content:
                continue

            # Check for import patterns
            patterns = [
                rf"from\s+[\w.]*{re.escape(old_mod)}\s+import",
                rf"import\s+[\w.]*{re.escape(old_mod)}",
            ]

            for pattern in patterns:
                if re.search(pattern, content):
                    import_updates.append(
                        {
                            "file": str(path.relative_to(project_root)),
                            "old_module": old_mod,
                            "new_module": new_mod,
                        },
                    )
                    break
        except:
            continue

    return import_updates


def main():
    """Main analysis function"""
    print("=" * 80)
    print("FILE CLASSIFICATION ANALYSIS")
    print("=" * 80)

    project_root = Path(__file__).parent.resolve()
    python_files = get_python_files_fast(project_root)

    stats = {"analyzed": len(python_files), "compliant": 0, "violations": {}}

    proposals = []

    for path in python_files:
        if not path.exists():
            continue

        file_type = classify_file(path)
        if file_type == "IGNORE":
            continue

        new_name = get_compliant_name(path, file_type)
        if new_name and new_name != path.name:
            stats["violations"][file_type] = stats["violations"].get(file_type, 0) + 1

            # Find import updates needed
            import_updates = find_imports_to_update(project_root, path.name, new_name)

            proposals.append(
                {
                    "current_path": str(path),
                    "current_name": path.name,
                    "proposed_name": new_name,
                    "file_type": file_type,
                    "relative_path": str(path.relative_to(project_root)),
                    "import_updates": import_updates,
                    "import_count": len(import_updates),
                },
            )
        else:
            stats["compliant"] += 1

    # Print summary
    print(f"\nTotal files analyzed: {stats['analyzed']}")
    print(f"Compliant files: {stats['compliant']}")
    total_violations = sum(stats["violations"].values())
    print(f"Total violations: {total_violations}")

    if total_violations > 0:
        print("\nViolation breakdown:")
        for vtype, count in sorted(stats["violations"].items(), key=lambda x: -x[1]):
            if count > 0:
                print(f"  {vtype}: {count}")

        # Group by phase
        phase1 = [p for p in proposals if p["file_type"] == "AGENT"]
        phase2 = [p for p in proposals if p["file_type"] == "MIXIN"]
        phase3 = [p for p in proposals if p["file_type"] == "TEST"]
        other = [p for p in proposals if p["file_type"] not in {"AGENT", "MIXIN", "TEST"}]

        print(f"\n{'=' * 80}")
        print(f"PHASE 1: AGENT RENAMES ({len(phase1)} files)")
        print(f"{'=' * 80}")
        for i, proposal in enumerate(phase1[:20], 1):
            print(f"{i:3d}. {proposal['relative_path']}")
            print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")
            print(f"     Import updates needed: {proposal['import_count']}")
        if len(phase1) > 20:
            print(f"... and {len(phase1) - 20} more")

        print(f"\n{'=' * 80}")
        print(f"PHASE 2: MIXIN RENAMES ({len(phase2)} files)")
        print(f"{'=' * 80}")
        for i, proposal in enumerate(phase2[:20], 1):
            print(f"{i:3d}. {proposal['relative_path']}")
            print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")
            print(f"     Import updates needed: {proposal['import_count']}")
        if len(phase2) > 20:
            print(f"... and {len(phase2) - 20} more")

        print(f"\n{'=' * 80}")
        print(f"PHASE 3: TEST RENAMES ({len(phase3)} files)")
        print(f"{'=' * 80}")
        for i, proposal in enumerate(phase3[:20], 1):
            print(f"{i:3d}. {proposal['relative_path']}")
            print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")
        if len(phase3) > 20:
            print(f"... and {len(phase3) - 20} more")

        if other:
            print(f"\n{'=' * 80}")
            print(f"OTHER RENAMES ({len(other)} files)")
            print(f"{'=' * 80}")
            for i, proposal in enumerate(other[:10], 1):
                print(f"{i:3d}. {proposal['relative_path']} ({proposal['file_type']})")
                print(f"     {proposal['current_name']} -> {proposal['proposed_name']}")

    print(f"\nTotal proposals: {len(proposals)}")

    # Save detailed report
    report = {
        "summary": stats,
        "proposals": proposals,
        "total_proposals": len(proposals),
        "phase1_agent_count": len([p for p in proposals if p["file_type"] == "AGENT"]),
        "phase2_mixin_count": len([p for p in proposals if p["file_type"] == "MIXIN"]),
        "phase3_test_count": len([p for p in proposals if p["file_type"] == "TEST"]),
    }

    report_file = project_root / "file_classification_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")
    return report


if __name__ == "__main__":
    main()
