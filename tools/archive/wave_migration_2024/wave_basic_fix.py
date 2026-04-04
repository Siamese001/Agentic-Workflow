#!/usr/bin/env python3
"""
Basic Wave Fix: Minimal fixes, one file at a time.
"""

import argparse
import ast
import pathlib
import re


def basic_fix_file(file_path: pathlib.Path) -> bool:
    """Basic fix: Remove MOVED blocks and add pass."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')

        # Remove MOVED blocks (simple approach)
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip MOVED blocks (improved detection)
            if re.search(r'^(\s*)#\s*#\s*MOVED:', line):
                # Skip until we find a line with less or equal indentation
                current_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines):
                    line_indent = len(lines[i]) - len(lines[i].lstrip())
                    if line_indent <= current_indent and lines[i].strip():
                        break
                    i += 1
                continue

            # Skip REMOVED lines
            if re.search(r'#\s*REMOVED:', line):
                i += 1
                continue

            fixed_lines.append(line)
            i += 1

        # Add pass for empty functions
        result_lines = []
        for i, line in enumerate(fixed_lines):
            result_lines.append(line)

            # If line is a def and next line is not indented, add pass
            if re.match(r'^(\s+)def\s+', line):
                if i + 1 < len(fixed_lines):
                    next_line = fixed_lines[i + 1]
                    if not next_line.startswith('        ') and next_line.strip() != '':
                        def_indent = len(line) - len(line.lstrip())
                        result_lines.append(' ' * (def_indent + 4) + 'pass')

        fixed_content = '\n'.join(result_lines)

        # Verify
        try:
            ast.parse(fixed_content)
        except SyntaxError:
            return False

        # Write if changed
        if fixed_content != content:
            file_path.write_text(fixed_content, encoding='utf-8')
            print("  ✅ Fixed")
            return True
        else:
            print("  ℹ️  No change needed")
            return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Basic wave fix')
    parser.add_argument('--count', type=int, default=1,
                       help='Number of files to process (default: 1)')

    args = parser.parse_args()

    print(f"Basic Wave: Processing {args.count} files")

    # Find first broken file
    tests_dir = pathlib.Path('tests')
    processed = 0

    for f in sorted(tests_dir.rglob('test_*.py')):
        if 'archive' in str(f).lower():
            continue

        try:
            content = f.read_text(encoding='utf-8', errors='replace')
            ast.parse(content)
            continue
        except SyntaxError:
            # Found broken file
            print(f"File {processed + 1}/{args.count}: {f}")

            if basic_fix_file(f):
                processed += 1
                if processed >= args.count:
                    break
        except:
            continue

    print(f"\nProcessed: {processed} files")

    if processed > 0:
        print("\nTo commit:")
        print("  git add tests/")
        print(f"  git commit -m 'Basic Wave: Fix {processed} files'")
        print("  git push")


if __name__ == '__main__':
    main()
