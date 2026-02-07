from __future__ import annotations
from pathlib import Path

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint_config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.utils.ssot_discovery_validator import get_data_files, get_python_files


def get_existing_file_hashes() -> dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    existing: Any = {}
    repo_root: Any = Path(".")
    sovereign_roots: Any = {
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        "schemas",
        "prompt_governance",
        "observability",
        "config",
        "data",
        ARCHIVES_DIR,
        "docs",
    }
    for root in sovereign_roots:
        root_path: Any = repo_root / root
        if root_path.exists():
            # Phase 6.4: Use ssot_discovery instead of rglob
            for file_path in get_python_files(root_path):
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in get_data_files(root_path, extensions=[".json"]):
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in get_data_files(root_path, extensions=[".md"]):
                existing[file_path.name] = get_file_hash(file_path)
    return existing
