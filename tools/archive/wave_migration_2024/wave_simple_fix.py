#!/usr/bin/env python3
"""
Simple Wave Fix: One file at a time, basic pattern fixes only.

No complex block detection - just simple regex-based fixes.
"""

import argparse
import ast
import pathlib
import re
import sys

# Import existing ProgressTracker
sys.path.insert(0, str(pathlib.Path(__file__).parent))


def simple_fix_pattern_A(content: str) -> str:
    """Simple Pattern A fix: Remove MOVED blocks with basic regex."""
    # Remove entire MOVED blocks (comment + indented lines + closing ))
    content = re.sub(
        r'#\s*#\s*MOVED:.*?^\s*\)\s*$',
        '',
        content,
        flags=re.MULTILINE | re.DOTALL
    )

    # Remove REMOVED lines
    content = re.sub(r'^\s*#\s*REMOVED:.*$', '', content, flags=re.MULTILINE)

    return content


def simple_fix_pattern_B(content: str) -> str:
    """Simple Pattern B fix: Re-indented docstrings."""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        # Look for unindented docstring after def
        if re.match(r'^\"\"\"Test \w+', line):
            # Find the previous def to get its indent
            for j in range(i-1, -1, -1):
                if re.match(r'^(\s+)def\s+', lines[j]):
                    def_indent = len(re.match(r'^(\s+)', lines[j]).group(1))
                    docstring_indent = def_indent + 4
                    fixed_lines.append(' ' * docstring_indent + line.strip())
                    break
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def simple_fix_pattern_C(content: str) -> str:
    """Simple Pattern C fix: Add pass after empty blocks."""
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # If line ends with : and next line is empty or next def, add pass
        if re.search(r':\s*$', line) and not re.search(r'#.*:', line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if (next_line.strip() == '' or
                    re.match(r'^\s*(def|class|@)', next_line)):
                    # Add pass
                    current_indent = len(line) - len(line.lstrip())
                    pass_indent = current_indent + 4
                    fixed_lines.append(' ' * pass_indent + 'pass')

    return '\n'.join(fixed_lines)


def simple_fix_pattern_D(content: str) -> str:
    """Simple Pattern D fix: Remove trailing unmatched parens."""
    return re.sub(r'[\)\}]$', '', content, flags=re.MULTILINE)


def fix_single_file(file_path: pathlib.Path, pattern: str, dry_run: bool = False) -> bool:
    """Fix a single file with simple pattern matching."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')

        # Apply pattern-specific fix
        if pattern == 'A':
            fixed_content = simple_fix_pattern_A(content)
        elif pattern == 'B':
            fixed_content = simple_fix_pattern_B(content)
        elif pattern == 'C':
            fixed_content = simple_fix_pattern_C(content)
        elif pattern == 'D':
            fixed_content = simple_fix_pattern_D(content)
        else:
            return False

        # Verify the fix
        try:
            ast.parse(fixed_content)
        except SyntaxError as e:
            print(f"  ❌ Fix failed: {e.msg}")
            return False

        # Write if not dry run and content changed
        if not dry_run and fixed_content != content:
            file_path.write_text(fixed_content, encoding='utf-8')
            print("  ✅ Fixed successfully")
            return True
        elif dry_run:
            print("  ✅ Would be fixed (dry run)")
            return True
        else:
            print("  ℹ️  No changes needed")
            return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def get_next_broken_file(pattern: str, skip_files: list[pathlib.Path] = None) -> pathlib.Path:
    """Get the next broken file for a pattern."""
    if skip_files is None:
        skip_files = []

    tests_dir = pathlib.Path('tests')

    for f in sorted(tests_dir.rglob('test_*.py')):
        if 'archive' in str(f).lower() or f in skip_files:
            continue

        try:
            content = f.read_text(encoding='utf-8', errors='replace')
            ast.parse(content)
            continue
        except SyntaxError as e:
            has_moved = bool(re.search(r'#\s*#\s*MOVED:', content))

            if pattern == 'A' and 'unexpected indent' in e.msg and has_moved:
                return f
            elif pattern == 'B' and 'unindent does not match' in e.msg:
                return f
            elif pattern == 'C' and 'expected an indented block' in e.msg:
                return f
            elif pattern == 'D':
                if not (('unexpected indent' in e.msg and has_moved) or
                       ('unindent does not match' in e.msg) or
                       ('expected an indented block' in e.msg)):
                    return f
        except:
            if pattern == 'D':
                return f

    return None


def main():
    parser = argparse.ArgumentParser(description='Simple wave fix - one file at a time')
    parser.add_argument('--pattern', choices=['A', 'B', 'C', 'D'], required=True,
                       help='Pattern to fix')
    parser.add_argument('--count', type=int, default=10,
                       help='Number of files to process (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without writing')

    args = parser.parse_args()

    print(f"Simple Wave {args.pattern}: Processing {args.count} files one by one")
    print()

    fixed_files = []
    failed_files = []
    skipped_files = []

    for i in range(args.count):
        file_path = get_next_broken_file(args.pattern, fixed_files + failed_files + skipped_files)

        if not file_path:
            print(f"No more Pattern {args.pattern} files found after {i} processed")
            break

        print(f"File {i+1}/{args.count}: {file_path}")

        if fix_single_file(file_path, args.pattern, args.dry_run):
            fixed_files.append(file_path)
        else:
            failed_files.append(file_path)

    print()
    print("Summary:")
    print(f"  Processed: {i+1} files")
    print(f"  Fixed: {len(fixed_files)}")
    print(f"  Failed: {len(failed_files)}")

    if not args.dry_run and fixed_files:
        print("\nTo commit changes:")
        print("  git add tests/")
        commit_msg = f'Simple Wave {args.pattern}: Fix {len(fixed_files)} files'
        print(f"  git commit -m '{commit_msg}'")
        print("  git push")


if __name__ == '__main__':
    main()
