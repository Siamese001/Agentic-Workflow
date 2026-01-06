"""Fix AST parse errors by adding pass statements to empty function bodies."""
import ast
import re
from pathlib import Path

target_prefixes = ["agentic_core", "apps_rg", "apps_lic", "apps_shared"]
fixed_count = 0

def fix_empty_function_body(content: str, line_num: int) -> str:
    """Add pass statement after function definition at line_num."""
    lines = content.splitlines(keepends=True)
    
    # Find the function definition line (line_num is 1-indexed)
    if line_num > len(lines):
        return content
    
    func_line_idx = line_num - 1
    func_line = lines[func_line_idx]
    
    # Get indentation of function
    func_indent = len(func_line) - len(func_line.lstrip())
    body_indent = func_indent + 4
    
    # Insert pass statement after function definition
    pass_line = ' ' * body_indent + 'pass\n'
    lines.insert(func_line_idx + 1, pass_line)
    
    return ''.join(lines)

def fix_unexpected_indent(content: str, line_num: int) -> str:
    """Fix unexpected indent by removing extra indentation."""
    lines = content.splitlines(keepends=True)
    
    if line_num > len(lines):
        return content
    
    line_idx = line_num - 1
    line = lines[line_idx]
    
    # Remove 4 spaces of indentation
    if line.startswith('    '):
        lines[line_idx] = line[4:]
    
    return ''.join(lines)

# Process each file with errors
for py_file in Path('.').rglob("*.py"):
    rel_path = py_file.relative_to('.')
    if not any(rel_path.parts[0].startswith(prefix) for prefix in target_prefixes):
        continue
    
    try:
        content = py_file.read_text(encoding="utf-8")
        ast.parse(content)
    except SyntaxError as e:
        if "expected an indented block after function definition" in e.msg:
            print(f"Fixing {py_file}:{e.lineno}")
            new_content = fix_empty_function_body(content, e.lineno)
            py_file.write_text(new_content, encoding="utf-8")
            fixed_count += 1
        elif "unexpected indent" in e.msg:
            print(f"Fixing indent {py_file}:{e.lineno}")
            new_content = fix_unexpected_indent(content, e.lineno)
            py_file.write_text(new_content, encoding="utf-8")
            fixed_count += 1
    except Exception:
        pass

print(f"\nFixed {fixed_count} files")
