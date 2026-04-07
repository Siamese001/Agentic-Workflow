#!/usr/bin/env python3
"""
Regenerate specific test files with the fixed template.
"""

import sys

sys.path.append('C:/Git/Agentic-Workflow')
from pathlib import Path

from tools.enhance_import_only_tests import analyze_module_api, generate_enhanced_test

# Files to fix
files_to_fix = [
    'tests/architecture/test_phantom_folder_regression.py',
    'tests/stress/test_atomic_concurrency.py',
    'tests/unit/agentic_core/adg/adapters/test___init___adg.py',
]

for file_path in files_to_fix:
    fp = Path(file_path)

    # Extract module path from existing content
    content = fp.read_text('utf-8')
    for line in content.splitlines():
        if line.startswith('MODULE_PATH = '):
            module_path = line.split('"')[1]
            break
    else:
        print(f"No MODULE_PATH found in {file_path}")
        continue

    print(f"Regenerating {file_path} -> {module_path}")

    try:
        # Analyze module and generate new test
        public_symbols, classes, functions = analyze_module_api(module_path)
        new_content = generate_enhanced_test(module_path, classes, functions)

        # Write the fixed content
        fp.write_text(new_content, encoding='utf-8')
        print(f"  Fixed: {len(classes)} classes, {len(functions)} functions")
    except Exception as e:
        print(f"  Error: {e}")

print("Done!")
