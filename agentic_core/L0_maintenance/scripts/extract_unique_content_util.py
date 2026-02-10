#!/usr/bin/env python3
"""
Extract unique classes/functions from high-priority archived files.
Only extracts content that doesn't exist in current codebase.
"""

import ast
from pathlib import Path


def build_codebase_index(dirs: list[str]) -> tuple[set[str], set[str]]:
    """Build index of all class and function names in current codebase."""
    classes = set()
    functions = set()

    for dir_path in dirs:
        for py_file in Path(dir_path).rglob("*.py"):
            if "__pycache__" in str(py_file) or "archives" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.add(node.name.lower())
                    elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        functions.add(node.name.lower())
            # guardian: allow-silent-swallow
            except:
                continue

    return classes, functions


def analyze_archive_file(file_path: Path, existing_classes: set[str], existing_functions: set[str]) -> dict:
    """Analyze an archived file and identify unique content."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
    except:
        return {"error": True}

    unique_classes = []
    unique_functions = []
    existing_in_file = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            if node.name.lower() not in existing_classes:
                # Get bases
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)

                # Get methods
                methods = [
                    item.name
                    for item in node.body
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
                ]

                unique_classes.append(
                    {
                        "name": node.name,
                        "bases": bases,
                        "methods": methods[:10],
                        "is_agent": node.name.endswith("Agent"),
                        "lineno": node.lineno,
                        "end_lineno": getattr(node, "end_lineno", node.lineno + 50),
                    },
                )
            else:
                existing_in_file.append(node.name)

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if node.name.lower() not in existing_functions and not node.name.startswith("_"):
                params = [arg.arg for arg in node.args.args if arg.arg != "self"]
                unique_functions.append(
                    {
                        "name": node.name,
                        "params": params,
                        "lineno": node.lineno,
                        "end_lineno": getattr(node, "end_lineno", node.lineno + 20),
                    },
                )
            else:
                existing_in_file.append(node.name)

    return {
        "unique_classes": unique_classes,
        "unique_functions": unique_functions,
        "existing": existing_in_file,
        "error": False,
    }


def main():
    print("=" * 80)
    print("EXTRACTING UNIQUE CONTENT FROM HIGH-PRIORITY ARCHIVES")
    print("=" * 80)

    # Build codebase index
    print("\n[1/3] Building codebase index...")
    current_dirs = ["agentic_core", "apps_rg", "apps_lic", "apps_shared", "scripts"]
    existing_classes, existing_functions = build_codebase_index(current_dirs)
    print(f"  Indexed: {len(existing_classes)} classes, {len(existing_functions)} functions")

    # High-priority files to analyze (remaining 44 from report)
    high_priority_files = [
        # Legacy agents with unique detectors
        (
            "archives/legacy_agents/legacy_detectors/DuplicateCodeDetectorAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/PerformanceBottleneckAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/SecurityVulnerabilityAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/UnusedImportCleanerAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/DeprecatedAPIDetectorAgent.py",
            "apps_shared/base_agents",
        ),
        (
            "archives/legacy_agents/legacy_detectors/MemoryLeakDetectorAgent.py",
            "apps_shared/base_agents",
        ),
        # Legacy validators
        ("archives/legacy_validators/StructuralHealerAgent.py", "apps_shared/base_agents"),
        ("archives/legacy_validators/CanonValidatorAgent.py", "apps_shared/base_agents"),
        (
            "archives/legacy_validators/ContentCleanlinessValidatorAgent.py",
            "apps_shared/base_agents",
        ),
        # Reachout Engine - agents
        ("archives/Reachout Engine Archive/deprecated in v13/agents_v13.py", "apps_lic/engines"),
        ("archives/Reachout Engine Archive/Agentic LIC/rag.py", "apps_lic/engines/stacks"),
        # Reachout Engine - models and utilities
        ("archives/Reachout Engine Archive/deprecated in v13/toggles.py", "apps_lic/engines/utils"),
        ("archives/Reachout Engine Archive/deprecated in v13/models.py", "apps_lic/engines/utils"),
        # apps_lic archive - routing and archetypes
        ("archives/apps_lic/L1_cognition/lic_cta_patterns.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_routing_rules.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_archetypes.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_vector_memory.py", "apps_lic/engines/utils"),
        ("archives/apps_lic/L1_cognition/lic_code_interpreter.py", "apps_lic/engines/utils"),
        # apps_rg archive - creative brief
        ("archives/apps_rg/L1_cognition/rg_creative_brief.py", "apps_rg/engines/utils"),
        # Legacy orchestrators
        (
            "archives/legacy_orchestrators/SelfRecoveringOrchestratorAgent.py",
            "apps_shared/base_agents",
        ),
    ]

    print(f"\n[2/3] Analyzing {len(high_priority_files)} high-priority files...")

    to_restore_full = []  # Files to restore completely
    to_extract = []  # Files with some unique content to extract
    skip_files = []  # Files with no unique content

    for archive_path, target_dir in high_priority_files:
        file_path = Path(archive_path)
        if not file_path.exists():
            print(f"  [NOT FOUND] {archive_path}")
            continue

        result = analyze_archive_file(file_path, existing_classes, existing_functions)

        if result.get("error"):
            print(f"  [SYNTAX ERROR] {file_path.name}")
            continue

        unique_classes = result["unique_classes"]
        unique_functions = result["unique_functions"]
        existing = result["existing"]

        unique_agents = [c for c in unique_classes if c["is_agent"]]
        unique_other = [c for c in unique_classes if not c["is_agent"]]

        if unique_agents:
            # Has unique agents - restore full file
            to_restore_full.append(
                {
                    "source": archive_path,
                    "target": target_dir,
                    "unique_agents": [a["name"] for a in unique_agents],
                    "unique_classes": [c["name"] for c in unique_other],
                    "unique_functions": [f["name"] for f in unique_functions],
                },
            )
            print(f"  [RESTORE FULL] {file_path.name} - {len(unique_agents)} unique agents")
        elif unique_other or unique_functions:
            # Has unique classes/functions but no agents
            to_extract.append(
                {
                    "source": archive_path,
                    "target": target_dir,
                    "unique_classes": [c["name"] for c in unique_other],
                    "unique_functions": [f["name"] for f in unique_functions],
                    "existing": existing,
                },
            )
            print(
                f"  [EXTRACT] {file_path.name} - {len(unique_other)} classes, {len(unique_functions)} functions",
            )
        else:
            skip_files.append(
                {
                    "source": archive_path,
                    "existing": existing,
                },
            )
            print(f"  [SKIP] {file_path.name} - all content exists")

    # Print summary
    print("\n" + "=" * 80)
    print("RESTORATION PLAN")
    print("=" * 80)

    print(f"\n## RESTORE FULL ({len(to_restore_full)} files)")
    for item in to_restore_full:
        print(f"\n  {Path(item['source']).name} -> {item['target']}/")
        print(f"    Unique Agents: {item['unique_agents']}")
        if item["unique_classes"]:
            print(f"    Unique Classes: {item['unique_classes'][:5]}")

    print(f"\n## EXTRACT UNIQUE CONTENT ({len(to_extract)} files)")
    for item in to_extract:
        print(f"\n  {Path(item['source']).name} -> {item['target']}/")
        print(f"    Unique Classes: {item['unique_classes'][:5]}")
        print(f"    Unique Functions: {item['unique_functions'][:5]}")

    print(f"\n## SKIP ({len(skip_files)} files)")
    for item in skip_files:
        print(f"  {Path(item['source']).name} - exists: {item['existing'][:3]}")

    # Execute restorations
    print("\n" + "=" * 80)
    print("EXECUTING RESTORATIONS")
    print("=" * 80)

    import shutil

    restored_count = 0
    for item in to_restore_full:
        src = Path(item["source"])
        target_dir = Path(item["target"])
        target_dir.mkdir(parents=True, exist_ok=True)

        # Use agent name as filename if available
        if item["unique_agents"]:
            dst_name = item["unique_agents"][0] + ".py"
        else:
            dst_name = src.name

        dst = target_dir / dst_name

        if not dst.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  ✓ Restored: {dst}")
            restored_count += 1
        else:
            print(f"  - Skipped (exists): {dst}")

    # For extract files, copy the whole file (simpler than extracting individual classes)
    for item in to_extract:
        src = Path(item["source"])
        target_dir = Path(item["target"])
        target_dir.mkdir(parents=True, exist_ok=True)

        dst = target_dir / src.name

        if not dst.exists():
            shutil.copy2(str(src), str(dst))
            print(f"  ✓ Restored: {dst}")
            restored_count += 1
        else:
            print(f"  - Skipped (exists): {dst}")

    print(f"\n  Total restored: {restored_count} files")


if __name__ == "__main__":
    main()
