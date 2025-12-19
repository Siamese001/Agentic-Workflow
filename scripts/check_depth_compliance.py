#!/usr/bin/env python3
"""
Check directory depth compliance with Key 49 - Universal Depth Law
MIN depth = 2 (no files directly in root)
MAX depth = 5 (max 5 levels from repo root)
"""

import os


def check_depth_compliance():
    """Check all Python files for depth compliance"""

    # Excluded directories
    EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', 'env', '.venv'}

    violations = []
    total_files = 0

    # Get all Python files
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith('.py'):
                total_files += 1
                file_path = os.path.join(root, file)

                # Calculate depth from root
                relative_path = os.path.relpath(file_path, '.')
                depth = len(relative_path.split(os.sep))

                # Check MIN depth (>= 2)
                if depth < 2:
                    violations.append({
                        'file': file_path,
                        'depth': depth,
                        'type': 'MIN_DEPTH_VIOLATION',
                        'message': f'File at depth {depth} (minimum is 2)'
                    })

                # Check MAX depth (<= 5)
                if depth > 5:
                    violations.append({
                        'file': file_path,
                        'depth': depth,
                        'type': 'MAX_DEPTH_VIOLATION',
                        'message': f'File at depth {depth} (maximum is 5)'
                    })

    # Report results
    print(f"\n📊 Depth Compliance Report")
    print(f"{'='*50}")
    print(f"Total Python files checked: {total_files}")
    print(f"Violations found: {len(violations)}")

    if violations:
        print(f"\n❌ VIOLATIONS:")
        for v in violations:
            print(f"  - {v['file']}: {v['message']}")

        # Group by type
        min_violations = [v for v in violations if v['type'] == 'MIN_DEPTH_VIOLATION']
        max_violations = [v for v in violations if v['type'] == 'MAX_DEPTH_VIOLATION']

        print(f"\n📋 Summary:")
        print(f"  MIN Depth Violations: {len(min_violations)}")
        print(f"  MAX Depth Violations: {len(max_violations)}")

        return False
    else:
        print(f"\n✅ All files comply with depth requirements (2-5 levels)")
        return True

if __name__ == "__main__":
    check_depth_compliance()
