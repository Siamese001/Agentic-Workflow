
"""Global architectural constants and governance laws."""

# [SSOT] Import from structure_blueprint.py instead of hardcoding
import sys

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent.parent / "agentic_core" / "config" / "P1_core")
)

# Law 3: The Law of The Void - Root directory is sacred
# [SSOT HARDENING] Import derived roots from the Sovereign Enforcer
ALLOWED_ROOT_FILES = {
    "README.md",
    ".gitignore",
    "LICENSE",
    "pyproject.toml",
    "requirements.txt",
    ".env",
    "canon_validator_agentic.py",
    "pytest.ini",
}

# CONFIGURATION: EXCLUSION ZONES (Strict Subatomic)
EXCLUDED_DIRS = {
    # System & Environment
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    # Build & Dependencies
    "node_modules",
    ".tox",
    "dist",
    "build",
    ".mypy_cache",
    ".coverage",
    # IDE & Editor
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    ".DS_Store",
    # Logs & Temp
    "logs",
    "tmp",
    "temp",
    ".tmp",
    # Data & Cache
    ".cache",
    "cache",
    "data",
    "archives",
    # Test Artifacts
    "htmlcov",
    "coverage.xml",
    # Documentation Build
    "_build",
    "site",
    ".doctrees",
}

EXCLUDED_FILES = {
    # Only the active validator and runner
    "canon_validator_v2_agentic.py",
    # Test files
    "test_*.py",
    "*_test.py",
    "conftest.py",
    # Cache & Data files
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    # Build artifacts
    "*.egg-info",
    "*.whl",
    "*.zip",
    "*.tar.gz",
    # IDE files
    ".vscode/settings.json",
    ".idea/*.xml",
    # OS files
    "Thumbs.db",
    "*.tmp",
}