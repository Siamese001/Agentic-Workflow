#!/usr/bin/env python3
"""Batch fix common syntax error patterns."""

import json
from pathlib import Path


def fix_unexpected_indent(file_path, line_num):
    """Fix unexpected indent errors by adjusting indentation."""
    path = Path(file_path)
    if not path.exists():
        return False

    try:
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()

        if line_num <= len(lines):
            line = lines[line_num - 1]
            # Check if it's an except/else/finally line that's over-indented
            stripped = line.lstrip()
            if any(keyword in stripped for keyword in ['except', 'else', 'finally']):
                # Reduce indentation by 4 spaces
                if line.startswith('        ') and not line.startswith('    '):
                    lines[line_num - 1] = line[4:]  # Remove 4 spaces

                with open(path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

    return False

def main():
    """Fix syntax errors in batches."""
    with open('C:/Git/Agentic-Workflow/syntax_error_report.json') as f:
        report = json.load(f)

    fixed = 0
    for err in report['details']:
        if 'unexpected indent' in err['message']:
            if fix_unexpected_indent(err['file'], err['line']):
                fixed += 1
                print(f"Fixed: {err['file']}:{err['line']}")

    print(f"\nFixed {fixed} files with unexpected indent errors")

if __name__ == '__main__':
    main()
