import os
import sys
from typing import Any, List, Dict, Optional

def get_existing_file_hashes() -> Dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    existing = {}
    repo_root = Path(".")

    sovereign_roots = {
        "agentic_core", "apps_lic", "apps_rg", "apps_shared",
        "schemas", "prompt_governance", "observability", "config",
        "data", "archives", "docs"  # Added docs
    }

    for root in sovereign_roots:
        root_path = repo_root / root
        if root_path.exists():
            # Check .py, .json, and .md files
            for file_path in root_path.rglob("*.py"):
                if "__pycache__" in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in root_path.rglob("*.json"):
                if "__pycache__" in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in root_path.rglob("*.md"):
                if "__pycache__" in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)

    return existing
