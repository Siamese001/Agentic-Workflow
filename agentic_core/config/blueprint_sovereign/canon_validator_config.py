"""
Canon Validator Configuration
Defines exclusion zones and constants for validation.
"""
import os
excluded_dirs: Any = {'.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', 'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs', 'archives', 'data'}
excluded_files: Any = {'canon_validator.py', 'canon_validator_backup.py', 'canon_validator_v2_agentic.py', 'auto_canon.py', '.DS_Store'}
max_healing_per_file: Any = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
global_healing_budget: Any = int(os.getenv('GLOBAL_HEALING_BUDGET', '50'))

def is_excluded(path: str) -> bool:
    """Check if a path should be excluded from validation."""
    path_parts: Any = path.split(os.sep)
    for part in path_parts:
        if part in EXCLUDED_DIRS:
            return True
    filename: Any = os.path.basename(path)
    if filename in EXCLUDED_FILES:
        return True
    return False
