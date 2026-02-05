#!/usr/bin/env python3
"""
Fix remaining BaseModel conversions to Sovereign Dataclasses.
Converts Pydantic BaseModel classes to @dataclass pattern.
"""

import re
from pathlib import Path


def convert_basemodel_to_dataclass(file_path: Path) -> bool:
    """Convert Pydantic BaseModel classes to dataclasses."""
    content = file_path.read_text(encoding="utf-8")

    # Check if file uses BaseModel
    if "BaseModel" not in content:
        return False

    modified = False

    # Add necessary imports at the top
    if "from dataclasses import dataclass, field" not in content:
        lines = content.split("\n")
        insert_idx = 0

        for i, line in enumerate(lines):
            if line.startswith("from __future__"):
                insert_idx = i + 1
                break
            elif line.startswith("import ") or line.startswith("from "):
                insert_idx = i
                break

        lines.insert(insert_idx, "from __future__ import annotations")
        lines.insert(insert_idx + 1, "from dataclasses import dataclass, field")
        lines.insert(insert_idx + 2, "from typing import Any")
        content = "\n".join(lines)
        modified = True

    # Replace class BaseModel with @dataclass
    content = re.sub(r"class (\w+)\(BaseModel\):", r"@dataclass\nclass \1:", content)

    # Replace Field(...) with field(...)
    content = re.sub(r"Field\(", r"field(", content)

    # Replace Field default_factory with field default_factory
    content = re.sub(r"= Field\(default_factory=", r"= field(default_factory=", content)

    # Remove @validator decorators (convert to __post_init__ if needed)
    content = re.sub(
        r"\s*@validator\([^)]+\)\s*\n\s*def [^:]+:[^}]+", "", content, flags=re.MULTILINE
    )

    # Remove ge/le constraints from field (move to metadata)
    content = re.sub(
        r"field\(([^,]+), ge=([^,]+), le=([^,]+)",
        r'field(\1, metadata={"ge": \2, "le": \3}',
        content,
    )

    if content != file_path.read_text(encoding="utf-8"):
        file_path.write_text(content, encoding="utf-8")
        return True

    return modified


def main():
    engines_dir = Path("apps_lic/engines")

    basemodel_files = [
        "knowledge_graph_agent.py",
        "onboarding_planner_agent.py",
        "stack_modernization_agent.py",
    ]

    print("🔄 Converting BaseModel to Sovereign Dataclasses")
    print("=" * 60)

    fixed_count = 0

    for filename in basemodel_files:
        file_path = engines_dir / filename
        if file_path.exists():
            if convert_basemodel_to_dataclass(file_path):
                print(f"  ✅ {filename}")
                fixed_count += 1
            else:
                print(f"  ⚠️  {filename} - no changes needed")
        else:
            print(f"  ❌ {filename} not found")

    print("\n" + "=" * 60)
    print(f"✅ Converted {fixed_count} files")


if __name__ == "__main__":
    main()
