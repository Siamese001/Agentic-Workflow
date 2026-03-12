"""
Suffix Cleanup Executor

Renames files with stuttering patterns and triggers deep refactoring
to update all imports and references across the codebase.

Target files:
1. LicHealingOrchestrator.py → LicHealingOrchestrator.py
2. OutreachPhase5Orchestrator.py → OutreachPhase5Orchestrator.py
3. MessageDiversityValidator.py → MessageDiversityValidator.py
4. ValidatorAgent.py → ValidatorAgent.py (SKIP - base validator)
5. RgHealingOrchestrator.py → RgHealingOrchestrator.py
6. RgResumeOrchestrator.py → RgResumeOrchestrator.py
"""

import ast
import os
import re
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

_ROOT = get_validated_project_root()


def to_smart_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case while preserving acronyms."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def update_imports_in_file(file_path: Path, old_name: str, new_name: str) -> int:
    """Update imports in a single file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Update import statements
        patterns = [
            (rf"from ([a-zA-Z0-9_.]+) import {old_name}", rf"from \1 import {new_name}"),
            (
                rf"from ([a-zA-Z0-9_.]+) import \(([^)]*){old_name}([^)]*)\)",
                rf"from \1 import (\2{new_name}\3)",
            ),
            (rf"import ([a-zA-Z0-9_.]+\.{old_name})", r"import \1"),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        # Update class references
        content = re.sub(rf"\b{old_name}\b", new_name, content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return 1
        return 0
    except (UnicodeDecodeError, OSError):
        return 0


def rename_file_and_refactor(source_path: Path, new_filename: str, project_root: Path) -> dict[str, Any]:
    """Rename a file and update all references."""
    old_stem = source_path.stem
    new_stem = Path(new_filename).stem

    result = {
        "source": str(source_path),
        "target": str(source_path.parent / new_filename),
        "old_class": old_stem,
        "new_class": new_stem,
        "files_updated": 0,
        "success": False,
    }

    if not source_path.exists():
        result["error"] = "Source file not found"
        return result

    target_path = source_path.parent / new_filename
    if target_path.exists():
        result["error"] = "Target file already exists"
        return result

    # Step 1: Rename the file
    try:
        shutil.move(str(source_path), str(target_path))
        print(f"✓ Renamed: {source_path.name} → {new_filename}")
    # guardian: allow-silent-swallow
    except Exception as e:
        result["error"] = str(e)
        return result

    # Step 2: Update class name inside the file
    try:
        content = target_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find and replace class definition
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == old_stem:
                content = re.sub(rf"class {old_stem}\b", f"class {new_stem}", content)
                break

        target_path.write_text(content, encoding="utf-8")
        print(f"  ✓ Updated class definition: {old_stem} → {new_stem}")
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"  ⚠ Warning: Could not update class definition: {e}")

    # Step 3: Deep refactoring - update all imports and references
    print("  → Scanning codebase for references...")

    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
    files_updated = 0

    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename.endswith(".py"):
                file_path = Path(dirpath) / filename
                files_updated += update_imports_in_file(file_path, old_stem, new_stem)

    result["files_updated"] = files_updated
    result["success"] = True
    print(f"  ✓ Updated {files_updated} files with new imports/references")

    # Step 4: Update corresponding test file
    test_name_old = f"test_{to_smart_snake_case(old_stem)}.py"
    test_name_new = f"test_{to_smart_snake_case(new_stem)}.py"

    # Find test file
    rel_path = source_path.relative_to(project_root)
    test_path_old = _ROOT / TESTS_DIR / "unit" / rel_path.parent / test_name_old
    test_path_new = _ROOT / TESTS_DIR / "unit" / rel_path.parent / test_name_new

    if test_path_old.exists() and not test_path_new.exists():
        try:
            shutil.move(str(test_path_old), str(test_path_new))
            print(f"  ✓ Renamed test: {test_name_old} → {test_name_new}")

            # Update test content
            content = test_path_new.read_text(encoding="utf-8")
            content = re.sub(rf"\b{old_stem}\b", new_stem, content)
            test_path_new.write_text(content, encoding="utf-8")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  ⚠ Warning: Could not update test file: {e}")

    return result


def execute_suffix_cleanup(project_root: Path, dry_run: bool = False) -> dict[str, Any]:
    """Execute the suffix cleanup for all flagged files."""

    # Target files with stuttering patterns
    targets = [
        ("apps_lic/engines/LicHealingOrchestrator.py", "LicHealingOrchestrator.py"),
        ("apps_lic/engines/OutreachPhase5Orchestrator.py", "OutreachPhase5Orchestrator.py"),
        ("apps_lic/engines/MessageDiversityValidator.py", "MessageDiversityValidator.py"),
        # Skip ValidatorAgent.py - it's a base validator, not stuttering
        ("apps_rg/engines/utils/RgHealingOrchestrator.py", "RgHealingOrchestrator.py"),
        ("apps_rg/engines/utils/RgResumeOrchestrator.py", "RgResumeOrchestrator.py"),
    ]

    report = {
        "mode": "DRY_RUN" if dry_run else "EXECUTE",
        "results": [],
        "total_files_updated": 0,
        "success_count": 0,
        "error_count": 0,
    }

    print("=" * 60)
    print(f"SUFFIX CLEANUP EXECUTOR - {report['mode']}")
    print("=" * 60)

    for source_rel, new_filename in targets:
        source_path = project_root / source_rel
        print(f"\n[{len(report['results']) + 1}/{len(targets)}] Processing: {source_rel}")

        if dry_run:
            print(f"  → Would rename to: {new_filename}")
            report["results"].append(
                {
                    "source": str(source_path),
                    "target": new_filename,
                    "dry_run": True,
                },
            )
        else:
            result = rename_file_and_refactor(source_path, new_filename, project_root)
            report["results"].append(result)

            if result["success"]:
                report["success_count"] += 1
                report["total_files_updated"] += result["files_updated"]
            else:
                report["error_count"] += 1
                print(f"  ✗ Error: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files renamed: {report['success_count']}/{len(targets)}")
    print(f"Total references updated: {report['total_files_updated']}")
    print(f"Errors: {report['error_count']}")

    return report


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Suffix Cleanup Executor")
    parser.add_argument("--execute", action="store_true", help="Execute changes (default: dry run)")
    parser.add_argument("--output", type=str, default="suffix_cleanup_report.json", help="Report output file")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    report = execute_suffix_cleanup(project_root, dry_run=not args.execute)

    # Save report
    output_path = project_root / args.output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: {output_path}")
