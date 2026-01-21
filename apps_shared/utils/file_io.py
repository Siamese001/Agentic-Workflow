from __future__ import annotations

"""File system utilities for apps_shared."""
import ast
import hashlib
import os
import re
from typing import Any

from apps_shared.domain.constants import EXCLUDED_DIRS, EXCLUDED_FILES


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ''

def is_excluded(path: str) -> bool:
    """Check if path should be excluded from validation."""
    parts: Any = path.split(os.sep)
    if any(p in EXCLUDED_DIRS for p in parts):
        return True
    if any(p.startswith('.') and len(p) > 1 and (p not in ['.github']) for p in parts):
        return True
    return False

def get_python_files(root: str='.') -> list[str]:
    """Get all Python files excluding specified directories and files."""
    python_files: Any = []
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith('.py') and file not in EXCLUDED_FILES:
                file_path: Any = os.path.join(root_dir, file)
                if not is_excluded(file_path):
                    python_files.append(file_path)
    return python_files

def write_compliant_file(path: str, content: str, dry_run: bool=False) -> bool:
    """Enforces Laws and Syntax Safety before writing to disk."""
    clean_content: Any = content
    if '```' in clean_content:
        clean_content: Any = re.sub('```[a-z]*\\n', '', clean_content)
        clean_content: Any = clean_content.replace('```', '')
    clean_content: Any = clean_content.strip()
    if path.endswith('.py'):
        try:
            ast.parse(clean_content)
        except SyntaxError as e:
            print(f'   🛑 BLOCKED WRITE: Agent produced invalid syntax for {path}')
            print(f'      Error: {e}')
            return False
    parts: Any = path.split(os.sep)
    if len(parts) - 1 < 3 or len(parts) - 1 > 5:
        print(f'   🛑 BLOCKED WRITE: File depth Violation for {path}')
        return False
    line_count: Any = len(clean_content.splitlines())
    if line_count < 10 or line_count > 200:
        print(f'   🛑 BLOCKED WRITE: File line count Violation for {path} ({line_count} lines)')
        return False
    if not dry_run:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            return True
        except Exception as e:
            print(f'   [X] Failed to write {path}: {e}')
            return False
    return True
