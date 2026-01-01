"""
Fix split string literals across multiple Python files.
This script fixes the common pattern where string literals were incorrectly
split across lines without proper line continuation.
"""
import sys
from pathlib import Path
from typing import Any

def fix_split_strings_in_file(filepath: Any) -> Any:
    """Fix split string literals in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        original_content: Any = content
        lines: Any = content.split('\n')
        fixed_lines: Any = []
        i: Any = 0
        while i < len(lines):
            line: Any = lines[i]
            if line.strip():
                quote_count: Any = line.count('"') + line.count("'")
                if quote_count % 2 == 1:
                    j: Any = i + 1
                    continuation_lines: Any = []
                    while j < len(lines):
                        next_line: Any = lines[j]
                        if next_line.strip():
                            next_quote_count: Any = next_line.count('"') + next_line.count("'")
                            if next_quote_count > 0:
                                fixed_line: Any = line.rstrip() + ' ' + next_line.lstrip()
                                fixed_lines.append(fixed_line)
                                i: Any = j
                                break
                            else:
                                continuation_lines.append(next_line)
                        j += 1
                    if j >= len(lines):
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            i += 1
        fixed_content: Any = '\n'.join(fixed_lines)
        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception:
        return False

def fix_all_python_files(root_dir: Any) -> Any:
    """Fix split strings in all Python files under root_dir."""
    root_path: Any = Path(root_dir)
    fixed_count: Any = 0
    target_dirs: Any = ['AgenticCore', '16_runtime_runtime', '19_runtime_pipeline']
    for target_dir in target_dirs:
        dir_path: Any = root_path / target_dir
        if dir_path.exists():
            for py_file in dir_path.rglob('*.py'):
                if fix_split_strings_in_file(py_file):
                    fixed_count += 1
if __name__ == '__main__':
    root_dir: Any = '.' if len(sys.argv) < 2 else sys.argv[1]
    fix_all_python_files(root_dir)
