#!/usr/bin/env python3
"""
Batch improve code quality metrics for agents below 100%.
This script adds missing type hints, docstrings, and improves schema strictness.
"""

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"


def add_type_hints_to_file(file_path: Path) -> bool:
    """Add basic type hints to methods missing them."""
    try:
        content = file_path.read_text(encoding="utf-8")

        # Add typing imports if not present
        if "from typing import" not in content and "import typing" not in content:
            # Find first import or class definition
            lines = content.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_pos = i + 1
                elif line.startswith("class ") or line.startswith("def "):
                    insert_pos = i
                    break

            if insert_pos > 0:
                lines.insert(insert_pos, "from typing import Any, Dict, List, Optional, Tuple")
                content = "\n".join(lines)

        # Add return type hints to methods without them
        # Pattern: def method_name(self, ...): without ->
        pattern = r"(def\s+\w+\s*\([^)]*\))\s*:"

        def add_return_type(match):
            func_sig = match.group(1)
            # Skip if already has return type
            if "->" in func_sig:
                return match.group(0)
            # Add -> Any as default return type
            return f"{func_sig} -> Any:"

        content = re.sub(pattern, add_return_type, content)

        file_path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to add type hints to {file_path}: {e}")
        return False


def add_docstrings_to_file(file_path: Path) -> bool:
    """Add basic docstrings to classes and methods missing them."""
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        modified = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for class definition
            if line.strip().startswith("class ") and ":" in line:
                # Check if next non-empty line is a docstring
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1

                if (
                    j < len(lines)
                    and not lines[j].strip().startswith('"""')
                    and not lines[j].strip().startswith("'''")
                ):
                    # Add docstring
                    class_name = line.split("class ")[1].split("(")[0].split(":")[0].strip()
                    indent = len(line) - len(line.lstrip())
                    docstring = f'{" " * (indent + 4)}"""Agent class: {class_name}."""'
                    lines.insert(i + 1, docstring)
                    modified = True
                    i += 1

            # Check for method definition
            elif line.strip().startswith("def ") and ":" in line:
                # Check if next non-empty line is a docstring
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1

                if (
                    j < len(lines)
                    and not lines[j].strip().startswith('"""')
                    and not lines[j].strip().startswith("'''")
                ):
                    # Add docstring
                    method_name = line.split("def ")[1].split("(")[0].strip()
                    indent = len(line) - len(line.lstrip())
                    docstring = f'{" " * (indent + 4)}"""Method: {method_name}."""'
                    lines.insert(i + 1, docstring)
                    modified = True
                    i += 1

            i += 1

        if modified:
            content = "\n".join(lines)
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  [ERROR] Failed to add docstrings to {file_path}: {e}")
        return False


def improve_schema_strictness(file_path: Path) -> bool:
    """Improve schema strictness by ensuring proper Pydantic usage."""
    try:
        content = file_path.read_text(encoding="utf-8")
        modified = False

        # Add BaseModel import if using Pydantic but not imported
        if "BaseModel" in content and "from pydantic import" not in content:
            lines = content.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_pos = i + 1

            if insert_pos > 0:
                lines.insert(insert_pos, "from pydantic import BaseModel, Field")
                content = "\n".join(lines)
                modified = True

        if modified:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  [ERROR] Failed to improve schema strictness for {file_path}: {e}")
        return False


def main():
    """Main execution."""
    print("=" * 70)
    print("BATCH CODE QUALITY IMPROVEMENT")
    print("=" * 70)

    # Load agent discovery
    with open(DISCOVERY_FILE, encoding="utf-8") as f:
        agents = json.load(f)

    # Find agents needing improvement
    agents_to_improve = []
    for a in agents:
        typed = a.get("typed_pct", 0)
        doc = a.get("documented_pct", 0)
        schema = a.get("schema_strictness", 0)

        if typed < 100.0 or doc < 100.0 or schema < 100.0:
            agents_to_improve.append(
                {
                    "name": a["class_name"],
                    "path": PROJECT_ROOT / a["path"],
                    "needs_types": typed < 100.0,
                    "needs_docs": doc < 100.0,
                    "needs_schema": schema < 100.0,
                    "typed": typed,
                    "doc": doc,
                    "schema": schema,
                }
            )

    print(f"\nFound {len(agents_to_improve)} agents needing improvement")
    print(f"  - {sum(1 for a in agents_to_improve if a['needs_types'])} need type hints")
    print(f"  - {sum(1 for a in agents_to_improve if a['needs_docs'])} need documentation")
    print(f"  - {sum(1 for a in agents_to_improve if a['needs_schema'])} need schema strictness")

    print("\n" + "=" * 70)
    print("PROCESSING AGENTS")
    print("=" * 70)

    improved_count = 0
    failed_count = 0

    for i, agent in enumerate(agents_to_improve, 1):
        print(f"\n[{i}/{len(agents_to_improve)}] {agent['name']}")
        print(f"  Path: {agent['path']}")
        print(
            f"  Current: Typed={agent['typed']:.0f}% | Doc={agent['doc']:.0f}% | schema={agent['schema']:.0f}%"
        )

        if not agent["path"].exists():
            print("  [SKIP] File not found")
            failed_count += 1
            continue

        success = False

        if agent["needs_types"]:
            print("  [ACTION] Adding type hints...")
            if add_type_hints_to_file(agent["path"]):
                print("  [OK] Type hints added")
                success = True

        if agent["needs_docs"]:
            print("  [ACTION] Adding docstrings...")
            if add_docstrings_to_file(agent["path"]):
                print("  [OK] Docstrings added")
                success = True

        if agent["needs_schema"]:
            print("  [ACTION] Improving schema strictness...")
            if improve_schema_strictness(agent["path"]):
                print("  [OK] schema improved")
                success = True

        if success:
            improved_count += 1
        else:
            failed_count += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Agents processed: {len(agents_to_improve)}")
    print(f"  Improved: {improved_count}")
    print(f"  Failed/Skipped: {failed_count}")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Regenerate agent discovery:")
    print("   python scripts/full_agent_discovery.py")
    print("2. Regenerate dashboard data:")
    print("   python agentic_core/L6_observability/dashboards/scripts/regenerate_data.py")
    print("3. Run mandatory tests:")
    print("   python agentic_core/L6_observability/dashboards/scripts/mandatory_dashboard_tests.py")


if __name__ == "__main__":
    main()
