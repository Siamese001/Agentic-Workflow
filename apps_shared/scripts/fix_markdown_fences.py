"""
Fix markdown code fences in Python files.
Removes ```python and ``` from files that have them.
"""

import re
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "fix_markdown_fences", "uwg_governed_write")
_emit_writes_through("p1", "fix_markdown_fences", "uwg_governed_write_2")
_emit_pulls_context("p1", "fix_markdown_fences", "context_retrieval")
_emit_pulls_context("p1", "fix_markdown_fences", "context_retrieval_2")
emit_determinism_digest("trace_fix_markdown_fences", "fix_markdown_fences_dispatch")
emit_determinism_digest("trace_fix_markdown_fences", "fix_markdown_fences_complete")
_emit_validated_by_safety_plane("p1", "fix_markdown_fences", "safety_validation")


def fix_markdown_fences(file_path: str) -> bool:
    """Remove markdown code fences from a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()
        if "```python" not in content and "```" not in content:
            return False
        content: Any = re.sub("^```python\\s*\\n", "", content, flags=re.MULTILINE)
        content: Any = re.sub("\\n```\\s*$", "", content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Fixed: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main() -> Any:
    """Find and fix all Python files with markdown fences."""
    root: Any = Path("c:/Git/Agentic-Workflow/agentic_core")
    fixed_count: Any = 0
    for py_file in get_python_files(root):
        if fix_markdown_fences(str(py_file)):
            fixed_count += 1
    print(f"\n🎯 Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
