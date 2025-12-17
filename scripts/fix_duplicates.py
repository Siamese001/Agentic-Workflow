#!/usr/bin/env python3
"""Fix duplicate class definitions and syntax errors in canon_validator_agentic.py"""

import re
from pathlib import Path

def fix_file():
    file_path = Path(__file__).parent / 'canon_validator_agentic.py'
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Track class definitions and their line numbers
    class_defs = {}
    class_pattern = re.compile(r'^class (\w+)\(')
    
    for i, line in enumerate(lines):
        match = class_pattern.match(line)
        if match:
            class_name = match.group(1)
            if class_name not in class_defs:
                class_defs[class_name] = []
            class_defs[class_name].append(i)
    
    # Find duplicates
    duplicates = {k: v for k, v in class_defs.items() if len(v) > 1}
    
    print(f"Found {len(duplicates)} classes with duplicates:")
    for name, line_nums in duplicates.items():
        print(f"  {name}: lines {[l+1 for l in line_nums]}")
    
    # Keep only the LAST occurrence of each duplicate class
    # (assuming the last one is the correct/complete definition)
    lines_to_remove = set()
    
    for class_name, line_nums in duplicates.items():
        # Remove all but the last occurrence
        for line_num in line_nums[:-1]:
            # Find the end of this class (next class definition or end of file)
            end_line = len(lines)
            for i in range(line_num + 1, len(lines)):
                if class_pattern.match(lines[i]):
                    end_line = i
                    break
            
            # Mark all lines in this class for removal
            for i in range(line_num, end_line):
                lines_to_remove.add(i)
            
            print(f"  Removing duplicate {class_name} at lines {line_num+1}-{end_line}")
    
    # Create cleaned content
    cleaned_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
    
    # Write back
    backup_path = file_path.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"\nBackup saved to: {backup_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"\nCleaned file:")
    print(f"  Original: {len(lines)} lines")
    print(f"  Cleaned: {len(cleaned_lines)} lines")
    print(f"  Removed: {len(lines) - len(cleaned_lines)} lines")
    
    # Verify syntax
    try:
        import ast
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("\n✅ Syntax check: PASSED")
        return True
    except SyntaxError as e:
        print(f"\n❌ Syntax check: FAILED at line {e.lineno}")
        print(f"   {e.msg}")
        return False

if __name__ == '__main__':
    success = fix_file()
    exit(0 if success else 1)
