"""
File: C:/Git/Agentic-Workflow/scripts/verify_global_imports.py
Context: Post-refactor validation tool. Critical Analysis suggests that while files were moved, global import references (blast radius) in consuming files (e.g., main.py, orchestrators) may remain pointing to 'common_utils', causing runtime failures. This script hunts for stale references.
"""

import os
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

MOVED_AGENTS = [
    "executive_title_composer",
    "HardenedAnthropicExecutor",
    "hardened_openai_executor",
    "providers_anthropic_client",
    "Router",
    "strategist_biowriter",
    "utilities_deep_brain_harvest",
]
FORBIDDEN_PATH = "apps_shared.common_utils"
NEW_PATH_HINT = "apps_rg.engines"
ROOT_DIR = str(REPO_ROOT)


def scan_for_stale_imports():
    stale_count = 0
    print(f"{'STATUS':<10} | {'FILE':<60} | {'ISSUE'}")
    print("-" * 100)
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = Path(root) / file
            if file_path.endswith("verify_global_imports.py"):
                continue
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            for _i, line in enumerate(lines):
                for agent in MOVED_AGENTS:
                    if f"from {FORBIDDEN_PATH}" in line and agent in line:
                        print(
                            f"!! STALE   | {file_path.replace(ROOT_DIR, '')[:60]:<60} | Importing '{agent}' from old path"
                        )
                        stale_count += 1
                    elif f"import {FORBIDDEN_PATH}.{agent}" in line:
                        print(
                            f"!! STALE   | {file_path.replace(ROOT_DIR, '')[:60]:<60} | Direct import of '{agent}' from old path"
                        )
                        stale_count += 1
    if stale_count == 0:
        print("\nSUCCESS: No stale imports detected. Refactor integrity verified.")
        sys.exit(0)
    else:
        print(f"\nFAILURE: Found {stale_count} stale imports. Run global search and replace.")
        sys.exit(1)


if __name__ == "__main__":
    scan_for_stale_imports()
