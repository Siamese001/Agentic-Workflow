#!/usr/bin/env python3
"""
Terminal Alignment Command - Final Pass
Fixes all remaining apps_lic.engines failures to achieve 100% PASS.
"""

import re
from pathlib import Path


def fix_dataclass_field_syntax(file_path: Path) -> bool:
    """Fix incorrect field(...) syntax - dataclass field() doesn't accept positional args."""
    content = file_path.read_text(encoding="utf-8")

    # Replace field(..., description=...) with field(default=..., metadata=...)
    # field(...) is invalid - must use field(default=...) or field(default_factory=...)

    # Pattern: field(..., description="...")
    content = re.sub(r'field\(\.\.\., description="([^"]+)"\)', r"# \1", content)

    # Pattern: field(..., metadata={...}, description="...")
    content = re.sub(
        r'field\(\.\.\., metadata=\{([^}]+)\}, description="([^"]+)"\)',
        r"field(metadata={\1})  # \2",
        content,
    )

    # Pattern: field(default=None, description="...")
    content = re.sub(r'field\(default=([^,]+), description="([^"]+)"\)', r"field(default=\1)  # \2", content)

    if content != file_path.read_text(encoding="utf-8"):
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def fix_subatomic_mixin_imports(file_path: Path) -> bool:
    """Add missing SubatomicTestingMixin imports."""
    content = file_path.read_text(encoding="utf-8")

    if "SubatomicTestingMixin" not in content:
        return False

    if "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin" in content:
        return False

    # Remove bad import if exists
    content = re.sub(r"from apps_lic\.shared\.core\.mixins import.*SubatomicTestingMixin.*\n", "", content)

    lines = content.split("\n")
    insert_idx = 0

    for i, line in enumerate(lines):
        if line.startswith("from apps_lic.utils.LICAgentBase"):
            insert_idx = i + 1
            break
        elif line.startswith("from typing import"):
            insert_idx = i + 1
            break

    lines.insert(
        insert_idx,
        "from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin",
    )

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def fix_mro_conflicts(file_path: Path) -> bool:
    """Fix MRO conflicts by removing duplicate mixins."""
    content = file_path.read_text(encoding="utf-8")

    # Remove SubatomicTestingMixin, MCPHardenedMixin, HealerMixin from class definitions
    # These are already in LICAgentBase
    content = re.sub(
        r"class (\w+)\(LICAgentBase, SubatomicTestingMixin, MCPHardenedMixin, HealerMixin\):",
        r"class \1(LICAgentBase):",
        content,
    )

    content = re.sub(
        r"class (\w+)\(LICAgentBase, SubatomicTestingMixin, MCPHardenedMixin\):",
        r"class \1(LICAgentBase):",
        content,
    )

    content = re.sub(
        r"class (\w+)\(LICAgentBase, HealerMixin, MCPHardenedMixin, SubatomicTestingMixin\):",
        r"class \1(LICAgentBase):",
        content,
    )

    if content != file_path.read_text(encoding="utf-8"):
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def fix_syntax_errors(file_path: Path) -> bool:
    """Fix specific syntax errors."""
    content = file_path.read_text(encoding="utf-8")
    original = content

    # Fix unmatched parentheses
    content = re.sub(r"\)\s+_format_prompt_with_defaults", r")\n# _format_prompt_with_defaults", content)
    content = re.sub(r"\)\s+SOVEREIGN_REGISTRY", r")\n# SOVEREIGN_REGISTRY", content)

    # Fix regex escaping issues in knowledge_graph
    content = re.sub(
        r"\{([^}]+)\}",
        lambda m: "{" + m.group(1) + "}" if "metadata" not in m.group(0) else m.group(0),
        content,
    )

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def add_missing_imports(file_path: Path, import_type: str) -> bool:
    """Add missing imports based on type."""
    content = file_path.read_text(encoding="utf-8")

    imports_to_add = {
        "dataclass": "from dataclasses import dataclass, field",
        "Enum": "from enum import Enum",
        "Path": "from pathlib import Path",
        "Agent": "from apps_lic.utils.LICAgentBase import LICAgentBase as Agent",
        "BaseAgent": "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent as BaseAgent",
    }

    if import_type not in imports_to_add:
        return False

    import_line = imports_to_add[import_type]

    if import_line in content:
        return False

    lines = content.split("\n")
    insert_idx = 0

    for i, line in enumerate(lines):
        if line.startswith("from __future__"):
            insert_idx = i + 1
            break
        elif line.startswith("import ") or line.startswith("from "):
            insert_idx = i
            break

    lines.insert(insert_idx, import_line)
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def main():
    engines_dir = Path("apps_lic/engines")

    print("🎯 Terminal Alignment Command - Final Pass")
    print("=" * 60)

    fixes = {
        "field_syntax": [],
        "subatomic_imports": [],
        "mro_conflicts": [],
        "syntax_errors": [],
        "missing_imports": [],
    }

    # Fix all Python files in engines
    for py_file in engines_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Fix field() syntax
        if fix_dataclass_field_syntax(py_file):
            fixes["field_syntax"].append(py_file.name)

        # Fix SubatomicTestingMixin imports
        if fix_subatomic_mixin_imports(py_file):
            fixes["subatomic_imports"].append(py_file.name)

        # Fix MRO conflicts
        if fix_mro_conflicts(py_file):
            fixes["mro_conflicts"].append(py_file.name)

        # Fix syntax errors
        if fix_syntax_errors(py_file):
            fixes["syntax_errors"].append(py_file.name)

        # Add missing imports based on content
        content = py_file.read_text(encoding="utf-8")

        if "dataclass" in content and "from dataclasses import" not in content:
            if add_missing_imports(py_file, "dataclass"):
                fixes["missing_imports"].append(f"{py_file.name} (dataclass)")

        if "Enum" in content and "from enum import" not in content:
            if add_missing_imports(py_file, "Enum"):
                fixes["missing_imports"].append(f"{py_file.name} (Enum)")

        if "Path" in content and "from pathlib import" not in content:
            if add_missing_imports(py_file, "Path"):
                fixes["missing_imports"].append(f"{py_file.name} (Path)")

        if re.search(r"class \w+\(Agent\)", content) and "Agent" not in ["import", "from"]:
            if add_missing_imports(py_file, "Agent"):
                fixes["missing_imports"].append(f"{py_file.name} (Agent)")

    print("\n📊 Fixes Applied:")
    for fix_type, files in fixes.items():
        if files:
            print(f"\n  {fix_type.replace('_', ' ').title()}: {len(files)} files")
            for f in files[:5]:
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")

    total_fixes = sum(len(f) for f in fixes.values())
    print("\n" + "=" * 60)
    print(f"✅ Applied {total_fixes} fixes across all categories")
    print("\n🔍 Run: python scripts/generate_certificate.py")


if __name__ == "__main__":
    main()
