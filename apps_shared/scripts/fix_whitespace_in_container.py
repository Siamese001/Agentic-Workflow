"""Simple script to fix trailing whitespace and Missing newlines."""
import os
from typing import Any
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
from pathlib import Path

def fix_whitespace_in_file(filepath: Any) -> Any:
    """Fix trailing whitespace and ensure file ends with newline."""
    try:
        with open(filepath, encoding='utf-8') as f:
            lines: Any = f.readlines()
        fixed_lines: Any = []
        for line in lines:
            fixed_line: Any = line.rstrip()
            fixed_lines.append(fixed_line)
        if fixed_lines and fixed_lines[-1]:
            fixed_lines.append('')
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in fixed_lines:
                f.write(line + '\n')
        return True
    except Exception:
        return False

def fix_all_files(root_dir: Any) -> Any:
    """Fix whitespace in all Python files."""
    fixed_count: Any = 0
    for root, _dirs, files in os.walk(root_dir):
        _dirs[:] = [d for d in _dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith('.py'):
                filepath: Any = Path(root) / file
                if fix_whitespace_in_file(filepath):
                    fixed_count += 1
    return fixed_count
if __name__ == '__main__':
    count: Any = fix_all_files('.')
