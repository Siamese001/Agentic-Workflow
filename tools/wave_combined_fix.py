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
from typing import List, Tuple

# Try to import ProgressTracker from fast_file_analysis
try:
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from fast_file_analysis import ProgressTracker
except ImportError:
    # Fallback if not available
    class ProgressTracker:
        def __init__(self, total, description):
            self.total = total
            self.description = description
        def start(self): print(f"Starting {self.description}...")
        def update(self, n, msg=""): pass
        def complete(self, msg=""): print(f"Completed: {msg}")

def fix_content(content: str) -> str:
    """Apply all fix patterns to content."""
    lines = content.split('\n')
    
    # 1. Remove MOVED blocks and REMOVED lines (Pattern A)
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.search(r'#\s*#\s*MOVED:', line):
            i += 1
            # Skip indented lines or orphaned parentheses
            while i < len(lines) and (lines[i].startswith('    ') or re.match(r'^\s*\)\s*$', lines[i])):
                i += 1
            continue
        if re.search(r'#\s*REMOVED:', line):
            i += 1
            continue
        fixed_lines.append(line)
        i += 1
    
    # 2. Fix Stub Indentation (Pattern B)
    # Look for unindented docstrings/bodies immediately after def
    intermediate_lines = []
    for i, line in enumerate(fixed_lines):
        if i > 0 and re.match(r'^\"\"\"Test \w+', line):
            # Check if previous line was a def
            prev_line = fixed_lines[i-1]
            if re.match(r'^(\s+)def\s+', prev_line):
                def_indent = len(prev_line) - len(prev_line.lstrip())
                intermediate_lines.append(' ' * (def_indent + 4) + line.strip())
                continue
        intermediate_lines.append(line)

    # 3. Add pass for empty blocks (Pattern C)
    final_lines = []
    for i, line in enumerate(intermediate_lines):
        final_lines.append(line)
        if re.search(r':\s*$', line) and not re.search(r'#.*:', line):
            if i + 1 < len(intermediate_lines):
                next_line = intermediate_lines[i + 1]
                # If next line is empty or a new definition at same/lesser indent
                if (next_line.strip() == '' or 
                    re.match(r'^\s*(def|class|@)', next_line)):
                    curr_indent = len(line) - len(line.lstrip())
                    final_lines.append(' ' * (curr_indent + 4) + 'pass')
            elif i == len(intermediate_lines) - 1:
                # End of file
                curr_indent = len(line) - len(line.lstrip())
                final_lines.append(' ' * (curr_indent + 4) + 'pass')

    # 4. Miscellaneous Cleanups (Pattern D)
    result = '\n'.join(final_lines)
    # Remove trailing unmatched delimiters often left by corrupt migrations
    result = re.sub(r'[\)\}]$', '', result, flags=re.MULTILINE)
    
    return result

def get_broken_files(limit: int) -> List[pathlib.Path]:
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
