"""
scripts/repair_legacy_agents_util.py
"""

import ast
import re
from pathlib import Path

LEGACY_ROOT = Path("apps_shared/legacy")

STUB_IMPORTS = """
from typing import Any, List, Dict, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel: pass
    def Field(*args, **kwargs): return None
"""


def repair_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8")

    # 1. Fix broken try statements that are empty
    lines = content.splitlines()
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # Check for empty try blocks
        if line.strip() == "try:":
            # Look ahead to see if next line is except or end
            if i + 1 < len(lines) and (
                lines[i + 1].strip().startswith("except") or lines[i + 1].strip() == ""
            ):
                fixed_lines.append("    pass")

        # Check for other empty blocks
        elif line.strip().endswith(":") and any(
            keyword in line
            for keyword in [
                "def",
                "class",
                "if",
                "for",
                "while",
                "with",
                "else",
                "elif",
                "except",
                "finally",
            ]
        ):
            # Look ahead to see if next line is empty, comment, or another block starter
            if (
                i + 1 >= len(lines)
                or not lines[i + 1].strip()
                or lines[i + 1].strip().startswith("#")
                or lines[i + 1].strip().endswith(":")
            ):
                # Insert a pass statement
                fixed_lines.append("    pass")

    content = "\n".join(fixed_lines)

    # 2. Fix Indentation - Use textwrap.dedent for proper handling
    import textwrap

    try:
        content = textwrap.dedent(content)
    except:
        pass  # If dedent fails, continue with original

    # 3. Fix specific syntax issues
    # Fix bare except clauses
    content = re.sub(r"except\s*:", "except Exception:", content)

    # Fix missing imports
    if "BaseModel" in content and "class BaseModel" not in content and "import BaseModel" not in content:
        content = STUB_IMPORTS + "\n" + content
    elif "Enum" in content and "import Enum" not in content:
        content = STUB_IMPORTS + "\n" + content

    # 4. Fix Broken Module Paths
    content = content.replace("apps_shared.base_agents", "agentic_core.base_agents")
    content = content.replace(
        "agentic_core.mixins.mcp_hardened_mixin",
        "agentic_core.mixins.infrastructure_mixin",
    )

    # 5. Write back
    file_path.write_text(content, encoding="utf-8")

    # 6. Verify AST
    try:
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"[-] Failed to repair {file_path.name}: {e}")
        return False


def run_resurrection():
    if not LEGACY_ROOT.exists():
        print("Legacy root not found. Run git restore first.")
        return

    success_count = 0
    files = list(LEGACY_ROOT.glob("*.py"))

    print(f"Attempting to resurrect {len(files)} agents...")

    for f in files:
        if repair_file(f):
            success_count += 1

    print(f"Resurrection Complete: {success_count}/{len(files)} files are now parseable.")


if __name__ == "__main__":
    run_resurrection()
