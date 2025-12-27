"""Fix indentation errors in test files where except blocks have misplaced pass statements."""
import re
from pathlib import Path

def fix_except_indentation(file_path):
    """Fix except blocks with misplaced pass/code statements."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    changes = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is an except line
        if re.match(r'^(\s*)except\s+.*:\s*$', line):
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            i += 1
            
            # Check if next line is 'pass' at wrong indentation
            if i < len(lines):
                next_line = lines[i]
                # If next line is 'pass' at same or less indentation, it's wrong
                if next_line.strip() == 'pass' and len(next_line) - len(next_line.lstrip()) <= indent:
                    # Skip this pass
                    i += 1
                    changes += 1
                    
                    # Look for the actual except body on following lines
                    while i < len(lines):
                        body_line = lines[i]
                        body_indent = len(body_line) - len(body_line.lstrip())
                        
                        # If we find code at wrong indentation, fix it
                        if body_line.strip() and body_indent <= indent:
                            # This should be inside the except block
                            fixed_lines.append(' ' * (indent + 4) + body_line.lstrip())
                            i += 1
                            changes += 1
                        else:
                            # Normal line, continue
                            break
                    continue
        
        fixed_lines.append(line)
        i += 1
    
    if changes > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        print(f"Fixed {changes} indentation issues in {file_path}")
        return True
    return False

def main():
    test_files = [
        'tests/core/test_l2_design_layer.py',
        'tests/core/test_llm_mcp_protocol.py',
        'tests/core/test_llm_mcp_protocol_simple.py',
    ]
    
    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            print(f"\nProcessing {file_path}...")
            fix_except_indentation(path)
        else:
            print(f"File not found: {file_path}")

if __name__ == '__main__':
    main()
