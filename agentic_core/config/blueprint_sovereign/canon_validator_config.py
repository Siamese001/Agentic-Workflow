"""
Canon Validator Configuration
Defines exclusion zones and constants for validation.
"""

import os

EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs',
    'archives', 'data',
}

EXCLUDED_FILES = {
    'canon_validator.py',
    'canon_validator_backup.py',
    'canon_validator_v2_agentic.py',
    'auto_canon.py',
    '.DS_Store'
}

# Healing configuration
MAX_HEALING_PER_FILE = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
GLOBAL_HEALING_BUDGET = int(os.getenv('GLOBAL_HEALING_BUDGET', '50'))

def is_excluded(path: str) -> bool:
    """Check if a path should be excluded from validation."""
    path_parts = path.split(os.sep)
    
    # Check directory exclusions
    for part in path_parts:
        if part in EXCLUDED_DIRS:
            return True
    
    # Check file exclusions
    filename = os.path.basename(path)
    if filename in EXCLUDED_FILES:
        return True
    
    return False
