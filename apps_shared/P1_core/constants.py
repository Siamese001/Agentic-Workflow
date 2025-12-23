"""Global architectural constants and governance laws."""

# Law 1: The Law of Depth - All functional files must exist at Depth 3-5
MIN_DEPTH = 3                      # e.g., domain/component/unit.py
MAX_DEPTH = 5                      # Maximum nesting depth

# Law 2: The Law of Atomicity - Files must be subatomic, not noise or monoliths
MAX_LINES = 200                    # Maximum file size (subatomic limit)
MIN_LINES = 10                     # Minimum file size (anti-noise limit)

# Law 3: The Law of The Void - Root directory is sacred
# [SSOT] Import from structure_blueprint.py instead of hardcoding
# [GRAVITY FIX] Apps should not define structure - import from core
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "agentic_core" / "config" / "P1_core"))
from structure_blueprint import ROOT_WHITELIST
ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
ALLOWED_ROOT_FILES = {
    'README.md', '.gitignore', 'LICENSE', 'pyproject.toml', 'requirements.txt',
    '.env', 'canon_validator_agentic.py', 'pytest.ini'
}

# CONFIGURATION: EXCLUSION ZONES (Strict Subatomic)
EXCLUDED_DIRS = {
    # System & Environment
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    # Build & Dependencies
    'node_modules', '.tox', 'dist', 'build', '.mypy_cache', '.coverage',
    # IDE & Editor
    '.vscode', '.idea', '*.swp', '*.swo', '.DS_Store',
    # Logs & Temp
    'logs', 'tmp', 'temp', '.tmp',
    # Data & Cache
    '.cache', 'cache', 'data', 'archives',
    # Test Artifacts
    '.pytest_cache', 'htmlcov', '.coverage', 'coverage.xml',
    # Documentation Build
    '_build', 'site', '.doctrees',
}

EXCLUDED_FILES = {
    # Only the active validator and runner
    'canon_validator_v2_agentic.py',
    # Test files
    'test_*.py', '*_test.py', 'conftest.py',
    # Cache & Data files
    '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
    # Build artifacts
    '*.egg-info', '*.whl', '*.zip', '*.tar.gz',
    # IDE files
    '.vscode/settings.json', '.idea/*.xml',
    # OS files
    'Thumbs.db', '*.tmp',
}
