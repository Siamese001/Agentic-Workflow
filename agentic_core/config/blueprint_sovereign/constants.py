"""
SSOT for Sovereign Constants and Exclusion Lists.

This module centralizes all exclusion patterns and constants that were
previously scattered across multiple files:
- ssot_discovery.py (hardcoded excludes)
- structure_blueprint.py (SOVEREIGN_EXCLUDED_FOLDERS)
- canon_validator_config.py (EXCLUDED_DIRS)

SSOT Consolidation (Jan 20, 2026):
All agents should import exclusion lists from here.
"""
from typing import FrozenSet, List, Set

# ============================================================================
# UNIFIED EXCLUSION LIST - SSOT
# ============================================================================
# Merges logic from: ssot_discovery.py, scripts, and validators
# Use this as the single source of truth for directory exclusions.

DEFAULT_EXCLUDE_DIRS: FrozenSet[str] = frozenset({
    # Backup/Archive
    ".sovereign_healing_backup",
    "archives",
    
    # Version Control
    ".git", ".svn", ".hg",
    
    # Python
    "__pycache__", ".pytest_cache", ".mypy_cache",
    ".eggs", "dist", "build",
    
    # Virtual Environments
    "venv", ".venv", "env", ".env",
    
    # IDE
    ".idea", ".vscode",
    
    # Dependencies
    "node_modules",
    
    # Coverage/Reports
    "htmlcov", ".coverage", "coverage_html",
    
    # Misc
    ".tox", ".ruff_cache",
    "logs", "tmp", "temp", "cache",
    "data", "raw",
    
    # Legacy
    "legacy_code", "legacy_engines", "legacy_resume_gen",
    "stubs",
})

# ============================================================================
# ACTIVE CANON KEYS - Defines enforced structure
# ============================================================================
ACTIVE_CANON_KEYS: List[int] = list(range(0, 20))

# ============================================================================
# FORBIDDEN PATTERNS - Strictly forbidden in filenames
# ============================================================================
FORBIDDEN_PATTERNS_RAW: List[str] = [
    " ",           # No spaces
    "__pycache__",
    ".DS_Store",
    "tmp_",
    "temp_",
    "backup_",
    "old_",
]

# ============================================================================
# CANON SIGNALS - High-signal keywords for file naming
# ============================================================================
CANON_SIGNALS: Set[str] = {
    'agent', 'manager', 'engine', 'validator', 'healer', 'auditor',
    'enforcer', 'detector', 'orchestrator', 'coordinator', 'pruner',
    'mapper', 'handler', 'guardian', 'governor', 'sentinel', 'strategy',
    'reasoning', 'fission', 'workflow', 'state', 'memory', 'cache',
    'safety', 'guardrail', 'prompt', 'persona', 'schema', 'blueprint',
    'template', 'context', 'ledger', 'Historian', 'audit', 'coverage',
    'vector', 'embedding', 'pinecone', 'redis', 'compliance', 'drift',
    'hierarchy', 'Span', 'depth', 'naming', 'rescue', 'integrity',
    'gravity', 'subatomic', 'gemini'
}

# ============================================================================
# NAMING EXEMPT FILES - Infrastructure files exempt from naming validation
# ============================================================================
NAMING_EXEMPT_FILES: FrozenSet[str] = frozenset({
    # Python infrastructure
    '__init__.py', '__main__.py', 'conftest.py', 'setup.py',
    # Config files
    'pyproject.toml', '.env', '.gitignore', '.dockerignore',
    'Dockerfile', 'Makefile', 'requirements.txt',
    # Documentation
    'README.md', 'CHANGELOG.md', 'LICENSE', 'LICENSE.md',
    'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',
    # IDE/Editor
    '.editorconfig', '.prettierrc', '.eslintrc',
    # Git
    '.gitattributes',
})

# ============================================================================
# NAMING EXEMPT DIRS - Directories exempt from naming validation
# ============================================================================
NAMING_EXEMPT_DIRS: FrozenSet[str] = frozenset({
    'archives', 'data', 'legacy_code', 'legacy_engines',
    '__pycache__', '.git', '.venv', 'venv', 'node_modules',
    '.pytest_cache', '.mypy_cache', 'coverage_html',
    'dist', 'build', '.tox', 'logs',
})

# ============================================================================
# ALLOWED DUPLICATE FILENAMES - Files permitted to exist in multiple dirs
# ============================================================================
ALLOWED_DUPLICATE_FILENAMES: FrozenSet[str] = frozenset({
    # Python package infrastructure (MUST exist in every package)
    '__init__.py',
    '__main__.py',
    
    # Testing infrastructure (pytest requires these in test directories)
    'conftest.py',
    
    # Common module patterns (legitimate per-package definitions)
    'context.py',
    'config.py',
    'constants.py',
    'exceptions.py',
    'types.py',
    'models.py',
    'base.py',
    'utils.py',
    'helpers.py',
    'common.py',
    
    # Observability patterns (per-engine instrumentation)
    'observability.py',
    'metrics.py',
    'logging.py',
    'tracing.py',
    
    # Autonomous agent patterns (per-engine autonomy)
    'proactive.py',
    'autonomous.py',
    'self_healing.py',
    
    # Prompt patterns (per-domain prompts)
    'prompts.py',
    'templates.py',
})

# ============================================================================
# PYTHON STDLIB MODULES - For import analysis
# ============================================================================
PYTHON_STDLIB_MODULES: FrozenSet[str] = frozenset({
    'os', 'sys', 'pathlib', 'logging', 'asyncio', 'typing', 'dataclasses',
    'collections', 'json', 're', 'datetime', 'functools', 'itertools',
    'abc', 'enum', 'contextlib', 'threading', 'time', 'random', 'math',
    'urllib', 'http', 'socket', 'subprocess', 'shutil', 'hashlib', 'uuid',
    'copy', 'io', 'traceback', 'inspect', 'importlib', 'warnings', 'pickle'
})

# ============================================================================
# VALIDATED FILE EXTENSIONS - Extensions that NamingAgent should validate
# ============================================================================
VALIDATED_FILE_EXTENSIONS: FrozenSet[str] = frozenset({
    # Python
    '.py',
    # Templates
    '.jinja', '.jinja2', '.j2',
    # Config
    '.json', '.yaml', '.yml', '.toml',
    # Documentation
    '.md', '.txt', '.rst',
    # Web
    '.html', '.css', '.js', '.ts',
})

__all__ = [
    "DEFAULT_EXCLUDE_DIRS",
    "ACTIVE_CANON_KEYS",
    "FORBIDDEN_PATTERNS_RAW",
    "CANON_SIGNALS",
    "NAMING_EXEMPT_FILES",
    "NAMING_EXEMPT_DIRS",
    "ALLOWED_DUPLICATE_FILENAMES",
    "PYTHON_STDLIB_MODULES",
    "VALIDATED_FILE_EXTENSIONS",
]
