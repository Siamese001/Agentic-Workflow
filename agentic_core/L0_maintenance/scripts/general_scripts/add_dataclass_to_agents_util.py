#!/usr/bin/env python3
"""
Add @dataclass decorator to all agents that don't have it.

This script:
1. Reads agent_discovery_full.json to find agents with schema_strictness < 100%
2. Adds @dataclass decorator and dataclasses import to each agent file
3. Preserves existing code structure
"""

import ast
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def has_dataclass_decorator(source: str) -> bool:
    """Check if source already has @dataclass decorator."""
    return "@dataclass" in source


def has_dataclass_import(source: str) -> bool:
    """Check if source already imports dataclass."""
    return "from dataclasses import" in source or "import dataclasses" in source


def add_dataclass_to_file(file_path: Path) -> bool:
    """Add @dataclass decorator to agent class in file.

    Returns True if changes were made.
    """
    if not file_path.exists():
        return False

    try:
        source = file_path.read_text(encoding="utf-8")
        original_source = source

        # Skip if already has @dataclass
        if has_dataclass_decorator(source):
            return False

        # Parse to find the agent class
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return False

        # Find the main agent class (ends with 'Agent')
        agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                agent_class = node
                break

        if not agent_class:
            return False

        lines = source.split("\n")

        # Add dataclass import if needed
        if not has_dataclass_import(source):
            # Find the best place to add the import
            import_line = 0
            for i, line in enumerate(lines):
                if line.startswith("from __future__"):
                    import_line = i + 1
                elif line.startswith("import ") or line.startswith("from "):
                    import_line = i + 1
                elif line.strip() and not line.startswith("#") and not line.startswith('"""'):
                    break

            lines.insert(import_line, "from dataclasses import dataclass")

        # Find the class definition line and add @dataclass before it
        # Need to re-parse after potential import addition
        source = "\n".join(lines)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                # Check if already has @dataclass decorator
                has_dc = False
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id == "dataclass":
                        has_dc = True
                    elif (
                        isinstance(dec, ast.Call)
                        and isinstance(dec.func, ast.Name)
                        and dec.func.id == "dataclass"
                    ):
                        has_dc = True

                if not has_dc:
                    # Add @dataclass decorator before the class
                    lines = source.split("\n")
                    class_line = node.lineno - 1  # 0-indexed

                    # Get the indentation of the class line
                    indent = ""
                    if lines[class_line]:
                        indent = len(lines[class_line]) - len(lines[class_line].lstrip())
                        indent = " " * indent

                    # Insert @dataclass before the class definition
                    lines.insert(class_line, f"{indent}@dataclass")
                    source = "\n".join(lines)
                break

        if source != original_source:
            file_path.write_text(source, encoding="utf-8")
            return True

        return False

    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False


def main():
    print("=" * 70)
    print("Adding @dataclass decorator to agents for schema Strictness 100%")
    print("=" * 70)

    # Load agent discovery
    discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
    with open(discovery_path, encoding="utf-8") as f:
        agents = json.load(f)

    # Find agents needing @dataclass
    agents_to_fix = [a for a in agents if a.get("schema_strictness", 100) < 100]

    print(f"\nAgents needing @dataclass: {len(agents_to_fix)}")

    fixed_count = 0
    skipped_count = 0

    for agent in agents_to_fix:
        path = agent["path"]
        file_path = PROJECT_ROOT / path

        if not file_path.exists():
            # Try with different path variations
            alt_paths = [
                PROJECT_ROOT / "agentic_core" / path,
                PROJECT_ROOT / path.replace("\\", "/"),
            ]
            for alt in alt_paths:
                if alt.exists():
                    file_path = alt
                    break

        if not file_path.exists():
            skipped_count += 1
            continue

        if add_dataclass_to_file(file_path):
            print(f"  ✓ {agent['class_name']}")
            fixed_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 70)
    print(f"✅ Added @dataclass to {fixed_count} agent files")
    print(f"   Skipped: {skipped_count} (already have @dataclass or couldn't process)")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
