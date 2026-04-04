#!/usr/bin/env python3
"""
Wave 40: Block-Aware Syntax Fix Script v2

Fixed Pattern A detection and fix logic.
"""

import argparse
import ast
import pathlib
import re
import sys
from collections import Counter

# Import existing ProgressTracker
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fast_file_analysis import ProgressTracker


class BlockFixer:
    """Block-aware syntax fixer for 3 corruption patterns."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'total': 0,
            'fixed': 0,
            'failed': 0,
            'patterns': Counter()
        }

    def fix_pattern_A(self, content: str) -> str:
        """Pattern A: Delete # # MOVED: blocks and fix resulting issues"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]

            # Check for MOVED comment
            if re.search(r'#\s*#\s*MOVED:', line):
                # Found start of MOVED block, find the closing ))
                self.stats['patterns']['A'] += 1
                j = i + 1

                # Skip indented body until we find closing ))
                while j < n:
                    if lines[j].strip() == '':
                        j += 1
                        continue
                    if re.search(r'^\s*\)\s*$', lines[j]):
                        break
                    j += 1

                if j < n:
                    # Skip the entire block (from MOVED comment to closing ))
                    i = j + 1
                    continue
                else:
                    # No closing found, keep the line
                    fixed_lines.append(line)
            else:
                # Keep non-MOVED lines
                fixed_lines.append(line)

            i += 1

        # Remove orphaned import blocks
        intermediate_lines = []
        i = 0
        n = len(fixed_lines)

        while i < n:
            line = fixed_lines[i]

            # Skip # REMOVED: lines
            if re.search(r'#\s*REMOVED:', line):
                i += 1
                continue

            # Check for orphaned import opening
            if re.search(r'^\s*from\s+\S+\s+import\s*\(\s*$', line):
                # Look ahead for the closing ))
                j = i + 1
                found_closing = False
                while j < n and j < i + 50:
                    if re.search(r'^\s*\)\s*$', fixed_lines[j]):
                        found_closing = True
                        break
                    j += 1

                if found_closing:
                    # Skip the entire orphaned import block
                    i = j + 1
                    continue
                else:
                    intermediate_lines.append(line)
            else:
                intermediate_lines.append(line)

            i += 1

        # Fix docstring indentation and add pass where needed
        final_lines = []
        i = 0
        n = len(intermediate_lines)

        while i < n:
            line = intermediate_lines[i]
            final_lines.append(line)

            # Check for function definition
            if re.search(r'^(\s+)def\s+\w+', line):
                def_indent = len(re.match(r'^(\s+)', line).group(1))

                # Look ahead for docstring or pass
                j = i + 1
                has_body = False
                while j < n and j < i + 10:
                    next_line = intermediate_lines[j]
                    if next_line.strip() == '':
                        j += 1
                        continue

                    # Check if next line is properly indented
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent > def_indent:
                        has_body = True
                        break
                    else:
                        # Next line is not indented - need to fix
                        break

                if not has_body:
                    # Need to add pass
                    pass_indent = def_indent + 4
                    final_lines.append(' ' * pass_indent + 'pass')

            i += 1

        return '\n'.join(final_lines)

    def fix_pattern_B(self, content: str) -> str:
        """Pattern B: Re-indent stub blocks to match parent def"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]

            # Look for def followed by unindented docstring
            if re.match(r'^(\s+)def\s+\w+', line):
                def_indent = len(line) - len(line.lstrip())

                # Check if next line is unindented stub
                if i + 1 < n and re.match(r'^\"\"\"Test \w+', lines[i + 1]):
                    self.stats['patterns']['B'] += 1

                    # Re-indent the stub block
                    fixed_lines.append(line)  # Keep the def line

                    # Process stub block
                    j = i + 1
                    stub_indent = def_indent + 4  # Correct indent for stub

                    while j < n:
                        stub_line = lines[j]

                        # Stop at next def/class or blank line
                        if (re.match(r'^\s*(def|class|@)', stub_line) or
                            stub_line.strip() == ''):
                            break

                        # Re-indent the stub line
                        if stub_line.strip():
                            fixed_lines.append(' ' * stub_indent + stub_line.lstrip())
                        else:
                            fixed_lines.append('')

                        j += 1

                    i = j - 1  # Will be incremented at end of loop
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        return '\n'.join(fixed_lines)

    def fix_pattern_C(self, content: str) -> str:
        """Pattern C: Insert pass in empty blocks"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            fixed_lines.append(line)

            # Check for lines ending with colon that need a body
            if (re.search(r':\s*$', line) and
                not re.search(r'#.*:', line)):  # Skip comments

                # Check if next line is empty or dedented
                if i + 1 < n:
                    next_line = lines[i + 1] if i + 1 < n else ''
                    current_indent = len(line) - len(line.lstrip())
                    next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else current_indent + 4

                    # If next line is empty or dedented, we need a pass
                    if (next_line.strip() == '' or
                        next_indent <= current_indent or
                        re.match(r'^\s*(def|class|@)', next_line)):

                        self.stats['patterns']['C'] += 1
                        pass_indent = current_indent + 4
                        fixed_lines.append(' ' * pass_indent + 'pass')

            i += 1

        return '\n'.join(fixed_lines)

    def fix_pattern_D(self, content: str) -> str:
        """Pattern D: Basic fixes for unmatched parens, braces"""
        # Simple unmatched paren/brace fix
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Remove unmatched closing braces/parens at end of line
            fixed_line = re.sub(r'[\)\}]$', '', line)
            if fixed_line != line:
                self.stats['patterns']['D'] += 1
            fixed_lines.append(fixed_line)

        return '\n'.join(fixed_lines)

    def fix_file(self, file_path: pathlib.Path, pattern: str) -> bool:
        """Fix a single file for the specified pattern."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')

            # Apply pattern-specific fix
            if pattern == 'A':
                fixed_content = self.fix_pattern_A(content)
            elif pattern == 'B':
                fixed_content = self.fix_pattern_B(content)
            elif pattern == 'C':
                fixed_content = self.fix_pattern_C(content)
            elif pattern == 'D':
                fixed_content = self.fix_pattern_D(content)
            else:
                return False

            # Verify the fix
            try:
                ast.parse(fixed_content)
            except SyntaxError:
                return False

            # Write if not dry run and content changed
            if not self.dry_run and fixed_content != content:
                file_path.write_text(fixed_content, encoding='utf-8')

            self.stats['fixed'] += 1
            return True

        except Exception as e:
            print(f"  Error fixing {file_path}: {e}")
            self.stats['failed'] += 1
            return False

    def process_wave(self, files: list[pathlib.Path], pattern: str) -> dict:
        """Process a wave of files."""
        self.stats = {'total': len(files), 'fixed': 0, 'failed': 0, 'patterns': Counter()}

        tracker = ProgressTracker(len(files), f"Wave {pattern}")
        tracker.start()

        for i, file_path in enumerate(files):
            success = self.fix_file(file_path, pattern)
            status = "✅" if success else "❌"
            tracker.update(1, f"{status} {file_path.name}")

        tracker.complete(f"Fixed: {self.stats['fixed']}, Failed: {self.stats['failed']}")
        return dict(self.stats)


def get_broken_files(pattern: str, limit: int = 50) -> list[pathlib.Path]:
    """Get broken files for a specific pattern."""
    tests_dir = pathlib.Path('tests')
    broken_files = []

    for f in tests_dir.rglob('test_*.py'):
        if 'archive' in str(f).lower():
            continue

        try:
            content = f.read_text(encoding='utf-8', errors='replace')
            ast.parse(content)
            continue
        except SyntaxError as e:
            # Pattern classification
            has_moved = bool(re.search(r'#\s*#\s*MOVED:', content))

            if pattern == 'A' and 'unexpected indent' in e.msg and has_moved:
                broken_files.append(f)
            elif pattern == 'B' and 'unindent does not match' in e.msg:
                broken_files.append(f)
            elif pattern == 'C' and 'expected an indented block' in e.msg:
                broken_files.append(f)
            elif pattern == 'D':
                # Other patterns
                if not (('unexpected indent' in e.msg and has_moved) or
                       ('unindent does not match' in e.msg) or
                       ('expected an indented block' in e.msg)):
                    broken_files.append(f)
        except:
            if pattern == 'D':
                broken_files.append(f)

    # Sort and limit
    broken_files.sort()
    return broken_files[:limit]


def main():
    parser = argparse.ArgumentParser(description='Block-aware syntax fixer v2')
    parser.add_argument('--pattern', choices=['A', 'B', 'C', 'D'], required=True,
                       help='Pattern to fix (A=MOVED blocks, B=stub indent, C=empty blocks, D=other)')
    parser.add_argument('--limit', type=int, default=50,
                       help='Files per wave (default: 50)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without writing')

    args = parser.parse_args()

    # Get files for this pattern
    files = get_broken_files(args.pattern, args.limit)
    print(f"Pattern {args.pattern}: Found {len(files)} files to fix")

    if not files:
        print("No files found for this pattern")
        return

    # Process the wave
    fixer = BlockFixer(dry_run=args.dry_run)
    results = fixer.process_wave(files, args.pattern)

    print("\nResults:")
    print(f"  Total files: {results['total']}")
    print(f"  Fixed: {results['fixed']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Patterns fixed: {dict(results['patterns'])}")

    if not args.dry_run and results['fixed'] > 0:
        print("\nTo commit changes:")
        print("  git add tests/")
        commit_msg = f'Wave {args.pattern}: Fix {results["fixed"]} files'
        print(f"  git commit -m '{commit_msg}'")
        print("  git push")


if __name__ == '__main__':
    main()
