"""
Sovereign domain constants - Re-exported from canonical location.
This module provides waterfall-compliant access to shared constants.
"""

# Architectural Constants
MIN_DEPTH = 3
MAX_DEPTH = 5
MAX_LINES = 200
MIN_LINES = 10

# Exclusion Zones
EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.tox', 'dist', 'build', '.mypy_cache', '.coverage',
    '.vscode', '.idea', '*.swp', '*.swo', '.DS_Store',
    'logs', 'tmp', 'temp', '.tmp',
    '.cache', 'cache', 'data', 'archives',
    'htmlcov', 'coverage.xml', '_build', 'site', '.doctrees',
}

EXCLUDED_FILES = {
    'canon_validator_v2_agentic.py',
    'test_*.py', '*_test.py', 'conftest.py',
    '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
    '*.egg-info', '*.whl', '*.zip', '*.tar.gz',
    '.vscode/settings.json', '.idea/*.xml',
    'Thumbs.db', '*.tmp',
}

ALLOWED_ROOT_FOLDERS = {
    'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'schemas',
    'prompt_governance', 'observability', 'config', 'tests', 'data', 'archives', 'scripts'
}

ALLOWED_ROOT_FILES = {
    'README.md', '.gitignore', 'LICENSE', 'pyproject.toml', 'requirements.txt',
    '.env', 'canon_validator_agentic.py', 'pytest.ini'
}