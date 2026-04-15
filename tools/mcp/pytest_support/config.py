from __future__ import annotations

import re
from pathlib import Path

from tools.mcp.mcp_bootstrap import REPO_ROOT

# Configuration
TESTS_DIR = REPO_ROOT / "tests"
PYTEST_CONFIG = REPO_ROOT / "pytest.ini"
PYPROJECT_TOML = REPO_ROOT / "pyproject.toml"
MAX_EXECUTION_TIME = 300  # 5 minutes for test runs
MAX_OUTPUT_SIZE = 50000  # characters
DISCOVER_TIMEOUT = 30
CONFIG_TIMEOUT = 15
COVERAGE_TIMEOUT = 120
MAX_TEST_FILE_SIZE = 1_000_000  # 1 MB
ALLOWED_COVERAGE_REPORTS = {
    "term",
    "term-missing",
    "html",
    "xml",
    "json",
    "lcov",
    "annotate",
}

# Characters not permitted in -k / -m expressions (guard against injection)
SAFE_EXPR_RE = re.compile(r"^[\w\s\-.()/\[\],'\"=!<>]+$")

__all__ = [
    "ALLOWED_COVERAGE_REPORTS",
    "CONFIG_TIMEOUT",
    "COVERAGE_TIMEOUT",
    "DISCOVER_TIMEOUT",
    "MAX_EXECUTION_TIME",
    "MAX_OUTPUT_SIZE",
    "MAX_TEST_FILE_SIZE",
    "PYPROJECT_TOML",
    "PYTEST_CONFIG",
    "REPO_ROOT",
    "SAFE_EXPR_RE",
    "TESTS_DIR",
]
