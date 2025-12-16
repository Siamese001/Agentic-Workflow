#!/usr/bin/env python
"""
Fix remaining syntax errors in test files, particularly:
1. Empty except blocks (add 'pass')
2. Empty function bodies (add 'pass')
3. Unmatched parentheses in imports
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Tuple

class AdvancedSyntaxFixer:
    def __init__(self, tests_dir: str = "tests"):
        self.tests_dir = Path(tests_dir)
        self.fixed_files = []
        self.failed_files = []

    def fix_empty_except_blocks(self, content: str) -> str:
        """Add 'pass' to empty except blocks"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_lines.append(line)

            # Check if this line starts an except block
            if re.match(r'^(\s*)except:', line.strip()):
                # Look ahead to see if the next line is empty or dedented
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    current_indent = len(line) - len(line.lstrip())
                    next_indent = len(next_line) - len(next_line.lstrip())

                    # If next line is empty or dedented, add 'pass'
                    if next_line.strip() == '' or next_indent < current_indent:
                        fixed_lines.append(' ' * (current_indent + 4) + 'pass')

        return '\n'.join(fixed_lines)

    def fix_empty_function_bodies(self, content: str) -> str:
        """Add 'pass' to empty function bodies"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            fixed_lines.append(line)

            # Check if this line starts a function definition
            if re.match(r'^(\s*)def \w+\(.*\):', line.strip()):
                # Look ahead to see if the next line is empty or dedented
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    current_indent = len(line) - len(line.lstrip())
                    next_indent = len(next_line) - len(next_line.lstrip())

                    # If next line is empty or dedented, add 'pass'
                    if next_line.strip() == '' or next_indent < current_indent:
                        fixed_lines.append(' ' * (current_indent + 4) + 'pass')

        return '\n'.join(fixed_lines)

    def fix_unmatched_parentheses_imports(self, content: str) -> str:
        """Fix unmatched parentheses in import statements"""
        # Fix common import patterns with unmatched parentheses
        patterns = [
            (r'from (\w+) import \(\s*\n\s*([^)]+)\n', r'from \1 import (\2)'),
            (r'import (\w+) \(\s*\n\s*([^)]+)\n', r'import \1 (\2)'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        return content

    def fix_triple_quotes(self, content: str) -> str:
        """Fix unmatched triple quotes"""
        # Count triple quotes
        triple_single = content.count("'''")
        triple_double = content.count('"""')

        # Fix odd counts by adding matching quotes at the end
        if triple_single % 2 == 1:
            content += "\n'''"
        if triple_double % 2 == 1:
            content += '\n"""'

        return content

    def fix_missing_closing_brackets(self, content: str) -> str:
        """Fix missing closing brackets in common patterns"""
        # Track bracket counts
        open_parens = content.count('(') - content.count(')')
        open_brackets = content.count('[') - content.count(']')
        open_braces = content.count('{') - content.count('}')

        # Add missing closing brackets
        if open_parens > 0:
            content += ')' * open_parens
        if open_brackets > 0:
            content += ']' * open_brackets
        if open_braces > 0:
            content += '}' * open_braces

        return content

    def validate_syntax(self, content: str) -> Tuple[bool, str]:
        """Check if the content has valid Python syntax"""
        try:
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def fix_file(self, file_path: Path) -> bool:
        """Fix syntax errors in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Apply fixes
            content = original_content
            content = self.fix_empty_except_blocks(content)
            content = self.fix_empty_function_bodies(content)
            content = self.fix_unmatched_parentheses_imports(content)
            content = self.fix_triple_quotes(content)
            content = self.fix_missing_closing_brackets(content)

            # Validate syntax
            is_valid, error = self.validate_syntax(content)

            if is_valid:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            else:
                # Try a more aggressive fix
                content = self.aggressive_fix(content, file_path.name)
                is_valid, error = self.validate_syntax(content)

                if is_valid:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return True
                else:
                    print(f"  ❌ Could not fix {file_path}: {error}")
                    return False

        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")
            return False

    def aggressive_fix(self, content: str, filename: str) -> str:
        """More aggressive fixes for difficult cases"""
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Fix common patterns
            if 'DELETE = # SQL query removed' in line:
                line = '# SQL query removed'
            elif line.strip().startswith('er, get_client'):
                line = line.replace('er, get_client', 'er, get_client')
            elif '"""TODO: Add docstring."""' in line and not line.strip().startswith('"""'):
                line = '"""TODO: Add docstring."""'

            # Fix indentation issues
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if any(keyword in line for keyword in ['def ', 'class ', '@', 'if ', 'for ', 'while ', 'try:', 'except', 'with ']):
                    # This should be indented but isn't - add 4 spaces
                    line = '    ' + line

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_remaining_files(self, failed_files: List[Path] = None) -> Tuple[int, int]:
        """Fix the remaining failed files"""
        print("🔧 Applying advanced fixes to remaining files...")

        if failed_files:
            target_files = failed_files
        else:
            # Find all files that still have syntax errors
            target_files = list(self.tests_dir.rglob("test_*.py"))
            target_files.extend(self.tests_dir.rglob("*_test.py"))

        print(f"Attempting to fix {len(target_files)} files")

        for file_path in target_files:
            print(f"\nFixing: {file_path}")
            if self.fix_file(file_path):
                self.fixed_files.append(file_path)
                print(f"  ✅ Fixed")
            else:
                self.failed_files.append(file_path)

        return len(self.fixed_files), len(self.failed_files)

    def generate_report(self):
        """Generate a report of fixed files"""
        print("\n" + "="*80)
        print("📊 ADVANCED FIX REPORT")
        print("="*80)
        print(f"✅ Successfully fixed: {len(self.fixed_files)} files")
        print(f"❌ Could not fix: {len(self.failed_files)} files")

        if self.failed_files:
            print("\n❌ Still failed files:")
            for file in self.failed_files[:10]:  # Show first 10
                print(f"  - {file}")
            if len(self.failed_files) > 10:
                print(f"  ... and {len(self.failed_files) - 10} more")

        print(f"\n🎯 Success rate: {len(self.fixed_files)/(len(self.fixed_files)+len(self.failed_files))*100:.1f}%")

def main():
    fixer = AdvancedSyntaxFixer()
    fixed, failed = fixer.fix_remaining_files()
    fixer.generate_report()

    if fixed > 0:
        print(f"\n✅ Run 'pytest tests/ --collect-only' to see the results!")

if __name__ == "__main__":
    main()

