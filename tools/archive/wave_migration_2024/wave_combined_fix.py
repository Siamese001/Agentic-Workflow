#!/usr/bin/env python3
"""
Wave Combined Fix: Handles multiple syntax corruption patterns in one pass.
Processes files one by one, verifying each with ast.parse.
"""

import argparse
import ast
import pathlib
import re
import sys

# Try to import ProgressTracker from fast_file_analysis
try:
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from fast_file_analysis import ProgressTracker
except ImportError:
    # Fallback if not available
    class ProgressTracker:
        def __init__(self, total, description):
            self.total = total
            self.current = 0
            self.description = description
        def start(self): print(f"Starting {self.description}...")
        def update(self, n, msg=""):
            self.current += n
            print(f"[{self.current}/{self.total}] {msg}")
        def complete(self, msg=""): print(f"Completed: {msg}")

def fix_content(content: str) -> str:
    """Apply all fix patterns to content."""
    # Pass 1: Pattern A - Remove MOVED blocks and REMOVED lines
    lines = content.splitlines()
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Pattern A: MOVED comment
        if re.search(r'#\s*#\s*MOVED:', line):
            i += 1
            # Skip until we find a line that is NOT indented
            # OR we find a closing parenthesis on its own line
            while i < len(lines):
                l = lines[i]
                if not l.strip():
                    i += 1
                    continue
                if re.match(r'^\s*\)\s*$', l):
                    i += 1
                    break
                if not l.startswith(' ') and not l.startswith('\t'):
                    break
                i += 1
            continue

        if re.search(r'#\s*REMOVED:', line):
            i += 1
            continue

        fixed_lines.append(line)
        i += 1

    # Pass 2: Pattern B - Fix stub indentation and cleanup consecutive duplicates
    intermediate_lines = []
    last_non_empty = None
    for i, line in enumerate(fixed_lines):
        stripped = line.strip()

        # Deduplicate consecutive identical lines (often leftovers)
        if stripped and stripped == last_non_empty:
            continue

        # Fix Stub Indentation (Pattern B)
        if stripped.startswith('"""Test ') and i > 0:
            prev = fixed_lines[i-1]
            if re.match(r'^\s*def\s+', prev):
                indent = len(prev) - len(prev.lstrip())
                line = ' ' * (indent + 4) + stripped

        intermediate_lines.append(line)
        if stripped:
            last_non_empty = stripped

    # Pass 3: Pattern C - Ensure empty blocks have 'pass'
    final_lines = []
    for i, line in enumerate(intermediate_lines):
        final_lines.append(line)
        if line.strip().endswith(':') and not line.strip().startswith('#'):
            # Look ahead for body
            has_body = False
            for j in range(i + 1, len(intermediate_lines)):
                next_l = intermediate_lines[j]
                if not next_l.strip():
                    continue

                curr_indent = len(line) - len(line.lstrip())
                next_indent = len(next_l) - len(next_l.lstrip())

                if next_indent > curr_indent:
                    has_body = True
                break

            if not has_body:
                indent = len(line) - len(line.lstrip())
                final_lines.append(' ' * (indent + 4) + 'pass')

    result = '\n'.join(final_lines)

    # Pass 4: Pattern D - Final delimiter cleanup if still failing
    try:
        ast.parse(result)
    except SyntaxError:
        # Try removing trailing unmatched delimiters
        lines = result.splitlines()
        cleaned = []
        for l in lines:
            s = l.strip()
            if s in (')', '(', '],', '}', '{'):
                # Check if it parses without this line
                temp = '\n'.join(cleaned + lines[lines.index(l)+1:])
                try:
                    ast.parse(temp)
                    # If it parses, skip this line
                    continue
                except SyntaxError:
                    pass
            cleaned.append(l)
        result = '\n'.join(cleaned)

    return result

def get_broken_files(limit: int) -> list[pathlib.Path]:
    """Find the next batch of broken files."""
    tests_dir = pathlib.Path('tests')
    broken = []
    for f in sorted(tests_dir.rglob('test_*.py')):
        if 'archive' in str(f).lower():
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='replace')
            ast.parse(content)
        except (SyntaxError, Exception):
            broken.append(f)
            if len(broken) >= limit:
                break
    return broken

def main():
    parser = argparse.ArgumentParser(description='Combined Wave Fixer')
    parser.add_argument('--limit', type=int, default=50, help='Files per wave')
    parser.add_argument('--dry-run', action='store_true', help='Do not write changes')
    args = parser.parse_args()

    files = get_broken_files(args.limit)
    if not files:
        print("No broken files found.")
        return

    tracker = ProgressTracker(len(files), "Combined Wave Fix")
    tracker.start()

    fixed_count = 0
    for f in files:
        try:
            content = f.read_text(encoding='utf-8', errors='replace')
            fixed = fix_content(content)

            # Verify
            ast.parse(fixed)

            if fixed != content:
                if not args.dry_run:
                    f.write_text(fixed, encoding='utf-8')
                fixed_count += 1
                tracker.update(1, f"✅ {f.name}")
            else:
                tracker.update(1, f"ℹ️  {f.name} (no change)")
        except Exception as e:
            tracker.update(1, f"❌ {f.name} (failed: {str(e)[:50]})")

    tracker.complete(f"Wave finished. Fixed: {fixed_count}")

    if fixed_count > 0 and not args.dry_run:
        print(f"\nTo commit:\ngit add tests/\ngit commit -m \"Wave Combined: Fix {fixed_count} files\"\ngit push")

if __name__ == '__main__':
    main()
