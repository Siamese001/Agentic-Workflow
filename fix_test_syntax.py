#!/usr/bin/env python
"""
Fix common syntax errors in test files to enable test discovery.

This script batch-fixes the most common syntax issues:
1. PYTEST constant not defined (replace with pytest)
2. Indentation errors (normalize to 4 spaces)
3. Incomplete assignments (DELETE = # SQL query removed)
4. Unmatched parentheses
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Tuple

class TestSyntaxFixer:
    def __init__(self, tests_dir: str = "tests"):
        self.tests_dir = Path(tests_dir)
        self.fixed_files = []
        self.failed_files = []
        
    def fix_pytest_references(self, content: str) -> str:
        """Replace PYTEST with pytest throughout the file"""
        # Fix PYTEST.MARK.SKIP -> pytest.mark.skip
        content = re.sub(r'PYTEST\.MARK\.SKIP', r'pytest.mark.skip', content, flags=re.IGNORECASE)
        content = re.sub(r'PYTEST\.MARK', r'pytest.mark', content, flags=re.IGNORECASE)
        content = re.sub(r'PYTEST\.RAISES', r'pytest.raises', content, flags=re.IGNORECASE)
        content = re.sub(r'PYTEST\.FIXTURE', r'pytest.fixture', content, flags=re.IGNORECASE)
        content = re.sub(r'@PYTEST\.', r'@pytest.', content, flags=re.IGNORECASE)
        content = re.sub(r'PYTEST\.', r'pytest.', content, flags=re.IGNORECASE)
        return content
    
    def fix_indentation(self, content: str) -> str:
        """Normalize indentation to 4 spaces"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip() == '':
                fixed_lines.append('')
                continue
                
            # Count leading spaces
            leading_spaces = len(line) - len(line.lstrip(' '))
            # Convert tabs to spaces
            line = line.replace('\t', '    ')
            
            # Normalize to 4-space multiples
            if leading_spaces > 0:
                stripped = line.lstrip(' ')
                # Round up to nearest 4
                indent = ((leading_spaces + 3) // 4) * 4
                line = ' ' * indent + stripped
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_incomplete_assignments(self, content: str) -> str:
        """Fix incomplete assignments like 'DELETE = # SQL query removed'"""
        # Fix DELETE = # SQL query removed
        content = re.sub(r'DELETE\s*=\s*#\s*SQL\s+query\s+removed', 
                        '# SQL query removed', content, flags=re.IGNORECASE)
        
        # Fix other incomplete assignments
        patterns = [
            (r'(\w+)\s*=\s*#\s*(.+)', r'# \2'),
            (r'(\w+)\s*=\s*"""(.*)"""', r'# \2'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_unmatched_parentheses(self, content: str) -> str:
        """Attempt to fix unmatched parentheses in common patterns"""
        # Fix common unmatched parentheses patterns
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix @pytest.fixture indentation issues
            if '@pytest.fixture' in line and not line.startswith('    '):
                line = '    ' + line
            
            # Fix def statements after decorators
            if i > 0 and lines[i-1].strip().startswith('@pytest.fixture'):
                if line.startswith('def ') and not line.startswith('    '):
                    line = '    ' + line
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
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
            content = self.fix_pytest_references(content)
            content = self.fix_indentation(content)
            content = self.fix_incomplete_assignments(content)
            content = self.fix_unmatched_parentheses(content)
            
            # Validate syntax
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
    
    def fix_all_files(self) -> Tuple[int, int]:
        """Fix all test files in the directory"""
        print("🔧 Fixing test syntax errors...")
        
        # Find all Python test files
        test_files = list(self.tests_dir.rglob("test_*.py"))
        test_files.extend(self.tests_dir.rglob("*_test.py"))
        
        print(f"Found {len(test_files)} test files")
        
        for file_path in test_files:
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
        print("📊 FIX REPORT")
        print("="*80)
        print(f"✅ Successfully fixed: {len(self.fixed_files)} files")
        print(f"❌ Could not fix: {len(self.failed_files)} files")
        
        if self.failed_files:
            print("\n❌ Failed files:")
            for file in self.failed_files:
                print(f"  - {file}")
        
        print(f"\n🎯 Success rate: {len(self.fixed_files)/(len(self.fixed_files)+len(self.failed_files))*100:.1f}%")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix syntax errors in test files")
    parser.add_argument("--dir", default="tests", help="Tests directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    
    args = parser.parse_args()
    
    fixer = TestSyntaxFixer(args.dir)
    
    if args.dry_run:
        print("🔍 Dry run mode - no files will be modified")
        # Just count files
        test_files = list(Path(args.dir).rglob("test_*.py"))
        test_files.extend(Path(args.dir).rglob("*_test.py"))
        print(f"Found {len(test_files)} test files to potentially fix")
    else:
        fixed, failed = fixer.fix_all_files()
        fixer.generate_report()
        
        if fixed > 0:
            print(f"\n✅ Run 'pytest tests/ --collect-only' to see the results!")

if __name__ == "__main__":
    main()
