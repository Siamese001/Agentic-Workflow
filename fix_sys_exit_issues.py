"""Fix sys.exit() calls at module level that prevent pytest collection."""
import re
from pathlib import Path

def fix_sys_exit_in_file(filepath):
    """Remove or comment out sys.exit() calls at module level."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Pattern: sys.exit(1) at module level (not inside a function/class)
        # Replace with pass or comment it out
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Check if line contains sys.exit
            if 'sys.exit(' in line and not line.strip().startswith('#'):
                # Check if it's at module level (not indented inside a function)
                # Look back to see if we're inside a function/class
                indent = len(line) - len(line.lstrip())
                
                # If indent is 0 or very small (4 spaces = inside except at module level)
                if indent <= 4:
                    # Comment it out instead of removing
                    new_lines.append(line.replace('sys.exit(', '# sys.exit('))
                    print(f"  Fixed sys.exit in {filepath.name} at line {i+1}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        if new_content != original_content:
            filepath.write_text(new_content, encoding='utf-8')
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix all test files with sys.exit issues."""
    test_dir = Path('tests')
    fixed_count = 0
    
    for test_file in test_dir.rglob('*.py'):
        if fix_sys_exit_in_file(test_file):
            print(f"[FIXED] {test_file}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
