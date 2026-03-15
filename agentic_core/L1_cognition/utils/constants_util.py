from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "constants_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "constants_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "constants_util")
"""
Sovereign domain constants - Re-exported from canonical location.
This module provides waterfall-compliant access to shared constants.
[SSOT] All structural constants derived from structure_blueprint.py
"""
from typing import Any

from agentic_core.L0_routing.config import (
    ROOT_PROTECTED_FILES,
    ROOT_WHITELIST,
)
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR, DEPTH_RULES

depth_map: Any = dict(DEPTH_RULES)
max_lines: Any = 200
min_lines: Any = 10
excluded_dirs: Any = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".tox",
    "dist",
    "build",
    ".mypy_cache",
    ".coverage",
    ".vscode",
    ".idea",
    ".DS_Store",
    "logs",
    "tmp",
    "temp",
    ".tmp",
    ".cache",
    "cache",
    "data",
    ARCHIVES_DIR,
    "htmlcov",
    "_build",
    "site",
    ".doctrees",
}
excluded_files: Any = {"canon_validator_v2_agentic.py", "conftest.py", ".DS_Store", "Thumbs.db"}
allowed_root_folders: Any = set(ROOT_WHITELIST)
allowed_root_files: Any = ROOT_PROTECTED_FILES
