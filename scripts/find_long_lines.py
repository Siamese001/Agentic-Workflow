#!/usr/bin/env python3
"""Find all lines longer than 100 characters."""

import os

def find_long_lines():
    """Find all lines longer than 100 characters."""
    violations = []
    
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        if '.venv' in dirs:
            dirs.remove('.venv')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if len(line.rstrip()) > 100:
                                violations.append(f"(
                                    {filepath}:{line_num} - {len(line.rstrip())} chars 
                                )"
                                print(f"{filepath}:{line_num} - {len(line.rstrip())} chars")
                                print(f"  {line[:150]}...")
                                print()
                except Exception as e:
                    pass
    
    print(f"\nTotal violations: {len(violations)}")

if __name__ == "__main__":
    find_long_lines()
