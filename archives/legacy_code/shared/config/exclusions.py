#!/usr/bin/env python3
"""
Single Source of Truth for what constitutes "Junk" files and directories.
Shared between Maintenance Pipeline (Phase A) and Runtime Pipeline (Phase B).
"""

# Directories to exclude from scanning and indexing
EXCLUDED_DIRS = {
    '.git', '.memory', '.vscode', '.venv', 'venv', 'env',
    'archives', 'archive', 'data', 'dataset', 'datasets',
    '__pycache__', '.pytest_cache', 'node_modules', 'logs',
    '.idea', '.ruff_cache', '.pytest_cache', 'build', 'dist',
    'eggs', '.ipynb_checkpoints'
}

# File patterns to exclude (glob patterns)
EXCLUDED_FILE_PATTERNS = [
    '*_backup.py', '*_old.py', 'result_*.py', 'temp_*.py',
    'canon_validator_backup.py', '*_copy.py', '*_duplicate.py',
    '*_v2.py', '*_v3.py', '*_test_backup.py'
]

# Specific files to exclude by name
EXCLUDED_FILES = {
    'canon_validator.py',
    'canon_validator_backup.py',
    'canon_validator_v2_agentic.py',
    'auto_canon.py',
    '.DS_Store',
    'Thumbs.db'
}

# File extensions to exclude from processing
EXCLUDED_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.pyi',
    '.log', '.tmp', '.bak', '.swp',
    '.swo', '.orig', '.rej', '.patch'
}

def is_excluded_path(path: str) -> bool:
    """
    Check if a path should be excluded based on directory and file patterns.

    Args:
        path: File path to check

    Returns:
        True if path should be excluded, False otherwise
    """
    import os
    from fnmatch import fnmatch

    # Split path into components
    parts = path.split(os.sep)

    # Check if any directory is excluded
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True

    # Check file name
    filename = os.path.basename(path)
    if filename in EXCLUDED_FILES:
        return True

    # Check file extension
    _, ext = os.path.splitext(filename)
    if ext.lower() in EXCLUDED_EXTENSIONS:
        return True

    # Check file patterns
    for pattern in EXCLUDED_FILE_PATTERNS:
        if fnmatch(filename, pattern):
            return True

    return False

def get_python_files(root_dir: str = '.') -> list[str]:
    """
    Get all Python files that are not excluded.

    Args:
        root_dir: Root directory to scan

    Returns:
        List of Python file paths
    """
    import os

    python_files = []

    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories from the walk
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not is_excluded_path(file_path):
                    # Normalize path
                    file_path = os.path.normpath(file_path)
                    python_files.append(file_path)

    return python_files
