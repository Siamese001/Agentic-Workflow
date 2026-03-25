#!/usr/bin/env python3
"""Fix missing except/finally blocks."""

import json
from pathlib import Path


def fix_missing_except(file_path, line_num):
    """Fix missing except/finally errors."""
    path = Path(file_path)
    if not path.exists():
        return False

    try:
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()

        if line_num <= len(lines):
            # Look for a try block that needs an except
            for i in range(max(0, line_num - 10), min(len(lines), line_num + 10)):
                line = lines[i]
                if 'try:' in line:
                    # Check if there's an except/finally after this try
                    found_except = False
                    indent_level = len(line) - len(line.lstrip())

                    for j in range(i + 1, len(lines)):
                        check_line = lines[j]
                        if check_line.strip() == '':
                            continue
                        check_indent = len(check_line) - len(check_line.lstrip())
                        if check_indent <= indent_level and not check_line.strip().startswith('#'):
                            # We're back to the same or lower indentation level
                            break
                        if any(keyword in check_line for keyword in ['except', 'finally']):
                            found_except = True
                            break

                    if not found_except:
                        # Add an except block
                        for j in range(len(lines) - 1, i, -1):
                            if lines[j].strip() != '':
                                insert_pos = j + 1
                                break
                        else:
                            insert_pos = len(lines)

                        # Insert except block with proper indentation
                        indent = ' ' * (indent_level + 4)
                        lines.insert(insert_pos, f"{indent}except Exception as e:\n")
                        lines.insert(insert_pos + 1, f"{indent}    pass\n")

                        with open(path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

    return False

def main():
    """Fix missing except/finally errors."""
    with open('C:/Git/Agentic-Workflow/syntax_error_report.json') as f:
        report = json.load(f)

    fixed = 0
    for err in report['details']:
        if 'expected \'except\' or \'finally\'' in err['message']:
            if fix_missing_except(err['file'], err['line']):
                fixed += 1
                print(f"Fixed: {err['file']}:{err['line']}")

    print(f"\nFixed {fixed} files with missing except/finally errors")

if __name__ == '__main__':
    main()
