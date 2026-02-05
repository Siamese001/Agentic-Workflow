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
    Classify file by type using AST analysis.

    REFINED LOGIC to avoid false positives:
    - Don't flag Error/Exception classes as Agents
    - Don't flag Strategy/Engine/Guardrail/Validator classes as needing Agent suffix
    - Focus on actual naming convention violations
    """
    critical_ignores = {
        "conftest.py",
        "__init__.py",
        "__main__.py",
        "setup.py",
        "structure_blueprint.py",
        "tool_registry.py",
    }
    if path.name in critical_ignores:
        return "IGNORE"

    try:
        if not path.exists() or path.stat().st_size == 0:
            return "IGNORE"
        content = path.read_text(encoding="utf-8")

        if "NOT_AN_AGENT" in content or "# NOT_AN_AGENT" in content:
            return "STUB"

        tree = ast.parse(content)
    except:
        return "IGNORE"

    # Test detection - files in tests/ folder
    is_structural_test = "tests" in path.parts
    if is_structural_test:
        # Already compliant test files - don't touch them
        if path.name.startswith("test_") or path.name.endswith("_test.py"):
            return "IGNORE"
        # Files in tests/ that don't follow test naming convention
        return "TEST"

    # Script detection - files in ops_scripts/ or scripts/ folders
    if "ops_scripts" in path.parts or ("scripts" in path.parts and "agents" not in path.parts):
        # Only flag if it's PascalCase (needs conversion to snake_case)
        if re.match(r"^[A-Z]", path.stem):
            return "SCRIPT"
        return "IGNORE"  # Already snake_case

    # Types/Collections detection - exempt from renaming
    type_collections = {"types", "schemas", "models", "errors", "exceptions", "consts", "dtos"}
    if path.stem in type_collections or path.name.startswith("_"):
        return "TYPES"

    # Parse classes for detailed analysis
    is_pure_mixin = False  # Only true if primary class is a Mixin AND file is PascalCase
    is_error = False
    is_exception = False
    is_strategy = False
    is_guardrail = False
    is_validator = False
    is_engine_class = False
    is_protocol = False
    is_gateway = False
    is_enum = False
    is_agent = False
    primary_class_name = None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            name = node.name
            if primary_class_name is None:
                primary_class_name = name

            # Check inheritance
            for base in node.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr

                if base_name:
                    if base_name == "Protocol":
                        is_protocol = True
                    if base_name in ("Exception", "BaseException", "Error"):
                        is_exception = True
                    if base_name == "Enum":
                        is_enum = True
                    if "Agent" in base_name:
                        is_agent = True
                    if "Mixin" in base_name:
                        # Inherits from a Mixin, but doesn't mean this file IS a mixin
                        pass

            # Name-based classification - check the PRIMARY class
            if "Gateway" in name:
                is_gateway = True
            if name.endswith("Error") or name.endswith("Exception"):
                is_error = True
            if name.endswith("Strategy"):
                is_strategy = True
            if name.endswith("Guardrail"):
                is_guardrail = True
            if name.endswith("Validator"):
                is_validator = True
            if name.endswith("Engine"):
                is_engine_class = True
            if name.endswith("Agent"):
                is_agent = True

    # Check if primary class is a Mixin (class name ends with Mixin AND file is PascalCase)
    if primary_class_name and primary_class_name.endswith("Mixin"):
        # Only flag if filename is PascalCase (not already snake_case)
        if re.match(r"^[A-Z]", path.stem) and not path.stem.islower():
            is_pure_mixin = True

    # REFINED: Don't flag these - they're correctly named
    if is_error or is_exception or is_strategy or is_guardrail or is_validator or is_engine_class:
        return "IGNORE"
    if is_enum:
        return "IGNORE"
    if is_agent:
        return "IGNORE"  # Agents are correctly named with Agent suffix

    if is_protocol:
        return "PROTOCOL"
    elif is_gateway:
        return "GATEWAY"
    elif is_pure_mixin:
        return "MIXIN"
    else:
        return "IGNORE"  # Don't flag other classes


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
    project_root: Path, old_name: str, new_name: str
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
                        }
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
                }
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
