"""Fix all indentation errors in test files."""
import os
import re
from pathlib import Path

def fix_file_indentation(filepath):
    """Fix indentation errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: except Exception as e:\npass\ncode at wrong indent
        # Fix: except Exception as e:\n    code
        pattern1 = r'([ \t]*)except Exception as e:\n(pass\n)?([^\s])'
        def fix_except_block(match):
            indent = match.group(1)
            has_pass = match.group(2)
            next_char = match.group(3)
            # Return properly indented except block
            return f'{indent}except Exception as e:\n{indent}    {next_char}'
        
        content = re.sub(pattern1, fix_except_block, content)
        
        # Pattern 2: Lines that start with logger/return at wrong indentation after except
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is an except line
            if re.match(r'^(\s*)except\s+.*:\s*$', line):
                indent_level = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                i += 1
                
                # Process following lines
                while i < len(lines):
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    # Skip empty lines
                    if not next_line.strip():
                        fixed_lines.append(next_line)
                        i += 1
                        continue
                    
                    # If line starts with logger/return/import at wrong indent
                    if next_indent <= indent_level and next_line.strip():
                        # Check if it should be part of except block
                        if any(next_line.lstrip().startswith(x) for x in ['logger.', 'return ', 'import ', 'traceback.']):
                            # Re-indent to be inside except block
                            fixed_lines.append(' ' * (indent_level + 4) + next_line.lstrip())
                            i += 1
                        else:
                            # This is a new block, stop processing except
                            break
                    else:
                        # Normal indentation, keep it
                        fixed_lines.append(next_line)
                        i += 1
                        # If we're back to normal indentation, stop
                        if next_indent <= indent_level:
                            break
            else:
                fixed_lines.append(line)
                i += 1
        
        content = '\n'.join(fixed_lines)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"ℹ️  No changes: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all test files with indentation errors."""
    test_dir = Path('tests/core')
    
    problem_files = [
        'test_llm_mcp_protocol.py',
        'test_llm_mcp_protocol_simple.py',
    ]
    
    fixed_count = 0
    for filename in problem_files:
        filepath = test_dir / filename
        if filepath.exists():
            if fix_file_indentation(filepath):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
