"""
File: C:/Git/Agentic-Workflow/scripts/verify_global_imports.py
Context: Post-refactor validation tool. Hunts for stale common_utils references.
"""

import sys
from pathlib import Path

from agentic_core.utils.fs_util import iter_scanned_files
from tqdm import tqdm

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


def _resolve_repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _resolve_repo_root()
ROOT_DIR = str(REPO_ROOT)


def scan_for_stale_imports():
    stale_count = 0
    print(f"{'STATUS':<10} | {'FILE':<60} | {'ISSUE'}")
    print("-" * 100)
    for file_path in tqdm(iter_scanned_files(ROOT_DIR, suffixes=(".py",)), desc="Processing", unit="item"):
        if file_path.name == "verify_global_imports.py":
            continue
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        rel_path = str(file_path).replace(ROOT_DIR, "")
        for line in lines:
            for agent in MOVED_AGENTS:
                if f"from {FORBIDDEN_PATH}" in line and agent in line:
                    print(
                        f"!! STALE   | {rel_path[:60]:<60} | Importing '{agent}' from old path; hint={NEW_PATH_HINT}"
                    )
                    stale_count += 1
                elif f"import {FORBIDDEN_PATH}.{agent}" in line:
                    print(
                        f"!! STALE   | {rel_path[:60]:<60} | Direct import of '{agent}' from old path; hint={NEW_PATH_HINT}"
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
