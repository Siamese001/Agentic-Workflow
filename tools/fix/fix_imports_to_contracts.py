#!/usr/bin/env python3
"""
Fix import statements to use L_CONTRACTS instead of runtime.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def fix_imports():
    """Fix import statements to use L_CONTRACTS."""
    print("🔧 Fixing import statements to use L_CONTRACTS...")

    # Pattern to find imports from runtime
    patterns = [
        (r'from agentic_core\.runtime\.lifecycle_trace_contract import', 'from agentic_core.L_CONTRACTS.lifecycle_trace_contract import'),
        (r'import agentic_core\.runtime\.lifecycle_trace_contract', 'import agentic_core.L_CONTRACTS.lifecycle_trace_contract'),
        (r'from agentic_core\.runtime import lifecycle_trace_contract', 'from agentic_core.L_CONTRACTS import lifecycle_trace_contract'),
        (r'from agentic_core\.runtime\.types\.execution_trace import', 'from agentic_core.L_CONTRACTS.execution_trace import'),
        (r'import agentic_core\.runtime\.types\.execution_trace', 'import agentic_core.L_CONTRACTS.execution_trace'),
        (r'from agentic_core\.runtime\.types import execution_trace', 'from agentic_core.L_CONTRACTS import execution_trace'),
        (r'from agentic_core\.runtime\.exceptions\.healer_exceptions import', 'from agentic_core.L_CONTRACTS.healer_exceptions import'),
        (r'import agentic_core\.runtime\.exceptions\.healer_exceptions', 'import agentic_core.L_CONTRACTS.healer_exceptions'),
        (r'from agentic_core\.runtime\.exceptions import healer_exceptions', 'from agentic_core.L_CONTRACTS import healer_exceptions'),
    ]

    # Find all Python files
    python_files = list(PROJECT_ROOT.rglob("*.py"))

    # Skip certain directories
    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules', 'archives', 'agentic_core/L_CONTRACTS', 'agentic_core/runtime'}

    fixed_count = 0
    for file_path in python_files:
        if any(skip_dir in str(file_path) for skip_dir in skip_dirs):
            continue

        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content

            # Fix each pattern
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                fixed_count += 1

                if fixed_count % 100 == 0:
                    print(f"  Fixed {fixed_count} files...")

        except Exception as e:
            print(f"  Error fixing {file_path}: {e}")

    print(f"✅ Fixed {fixed_count} import statements")


if __name__ == "__main__":
    fix_imports()
