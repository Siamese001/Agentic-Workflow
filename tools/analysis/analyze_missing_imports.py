#!/usr/bin/env python3
"""Analyze missing imports from test execution failures."""

import re
import subprocess


def get_import_errors():
    """Run pytest and extract ImportError messages."""
    # Run pytest on a subset to get error patterns
    result = subprocess.run(
        ["pytest", "tests/unit/agentic_core/L0_routing/enforcement/", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        cwd="C:\\Git\\Agentic-Workflow"
    )

    # Extract ImportError patterns
    import_errors = []
    for line in result.stderr.split('\n'):
        if 'ImportError:' in line and 'cannot import name' in line:
            # Extract module and missing name
            match = re.search(r'cannot import name \'([^\']+)\' from \'([^\']+)\'', line)
            if match:
                missing_name = match.group(1)
                from_module = match.group(2)
                import_errors.append((missing_name, from_module))

    return import_errors

def main():
    errors = get_import_errors()
    print(f"Found {len(errors)} import errors:")
    for missing_name, from_module in sorted(set(errors)):
        print(f"  {missing_name} from {from_module}")

    # Group by module
    by_module = {}
    for missing_name, from_module in errors:
        if from_module not in by_module:
            by_module[from_module] = []
        by_module[from_module].append(missing_name)

    print("\nBy module:")
    for module, names in sorted(by_module.items()):
        print(f"  {module}: {', '.join(sorted(set(names)))}")

if __name__ == "__main__":
    main()
