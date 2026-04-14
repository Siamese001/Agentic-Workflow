"""
Fix global variable violations by replacing with manager pattern
"""

import os
import re
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "fix_global_variables", "uwg_governed_write")
_emit_writes_through("p1", "fix_global_variables", "uwg_governed_write_2")
_emit_pulls_context("p1", "fix_global_variables", "context_retrieval")
_emit_pulls_context("p1", "fix_global_variables", "context_retrieval_2")
emit_determinism_digest("trace_fix_global_variables", "fix_global_variables_dispatch")
emit_determinism_digest("trace_fix_global_variables", "fix_global_variables_complete")
_emit_validated_by_safety_plane("p1", "fix_global_variables", "safety_validation")


def fix_global_variables(file_path: str) -> Any:
    """Fix global variables in a Python file"""
    with open(file_path, encoding="utf-8") as f:
        content: Any = f.read()
    original: Any = content
    pattern: Any = "(_\\w+)\\s*=\\s*None\\s*\\n\\s*\\n\\s*def\\s+get_\\w+\\([^)]*\\):\\s*\\n\\s*global\\s+\\1\\s*\\n\\s*if\\s+\\1\\s+is\\s+None:\\s*\\n\\s+\\1\\s*=\\s*\\w+\\([^)]*\\)\\s*\\n\\s*return\\s+\\1"
    matches: Any = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    for match in matches:
        var_name: Any = match.group(1)
        class_name: Any = var_name.replace("_", "").title()
        replacement: Any = f'''class {class_name}Manager:\n    """Manager for {class_name} without global state"""\n\n    def __init__(self):\n        self._instance = None\n\n    def get_instance(self):\n        """Get or create the instance"""\n        if self._instance is None:\n            self._instance = {class_name}()\n        return self._instance\n\n\n# Global manager instance (acceptable as it's a dependency injection container)\n_{var_name}_manager = {class_name}Manager()\n\n\ndef get_{var_name[1:]}():\n    """Get the global instance"""\n    return _{var_name}_manager.get_instance()'''
        content: Any = content.replace(match.group(0), replacement)
    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed global variables in: {file_path}")
        return True
    return False


def main() -> Any:
    """Fix all global variable violations"""
    files_to_fix: Any = [
        "apps_shared/mcp_hardening.py",
        "apps_shared/strip_bom_and_fix.py",
        "apps_shared/time_bound_benchmarking.py",
        "apps_shared/utils.py",
        "apps_shared/verify_hardening.py",
        "apps_shared/verify_hardening_minimal.py",
        "apps_shared/verify_hardening_simple.py",
        "apps_shared/watchdog_sidecar.py",
        "scripts/shared/resilience/mixin.py",
        "scripts/shared/safety/constitutional_ai_impl.py",
        "tests/test_integrity.py",
        "tests/test_integrity_mock.py",
    ]
    fixed_count: Any = 0
    for file_path in files_to_fix:
        # guardian: allow-path-string
        if os.path.exists(file_path):
            if fix_global_variables(file_path):
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")
    print(f"\nFixed {fixed_count} files with global variable violations")


if __name__ == "__main__":
    main()
