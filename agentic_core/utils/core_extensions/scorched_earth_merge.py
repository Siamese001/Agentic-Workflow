from __future__ import annotations

import logging

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import shutil
from datetime import datetime
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / "agentic_core"
approved_root_folders: Any = [
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "tests",
    "data",
    "archives",
    ".git",
    ".venv",
    ".vscode",
]
approved_root_files: Any = [
    "sovereign_manifest.json",
    "canon_validator_v3.py",
    ".gitignore",
    "README.md",
    "synapse_hardener.py",
    "forge_v4.py",
]
catch_all_mapping: Any = {
    "config": CORE / "config/P1_core",
    "observability": CORE / "observability/P1_core",
    "obs": CORE / "observability/P1_core",
    "prompt": CORE / "prompt_governance/P1_core",
    "schema": CORE / "schemas/P1_core",
    "script": CORE / "L0_maintenance/scripts",
    "test": ROOT / "tests/unit",
    "DEFAULT_LOGIC": CORE / "utils/P1_core",
    "DEFAULT_ADMIN": CORE / "L0_maintenance/automation",
}
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def scorched_earth_merge() -> Any:
    """Brief description of functionality and purpose."""
    logging.info("--- COMMENCING SCORCHED EARTH MERGE: No File Left Behind ---")
    for layer_path in [
        CORE / "config/P1_core",
        CORE / "observability/P1_core",
        CORE / "prompt_governance/P1_core",
        CORE / "schemas/P1_core",
        CORE / "L0_maintenance/scripts",
    ]:
        layer_path.mkdir(parents=True, exist_ok=True)
        (layer_path / "__init__.py").touch()
    for item in ROOT.iterdir():
        if item.name in APPROVED_ROOT_FOLDERS or item.name in APPROVED_ROOT_FILES:
            continue
        target_dest: Any = (
            CATCH_ALL_MAPPING["DEFAULT_LOGIC"]
            if item.is_file()
            else CATCH_ALL_MAPPING["DEFAULT_ADMIN"]
        )
        for key, path in CATCH_ALL_MAPPING.items():
            if key in item.name.lower():
                target_dest: Any = path
                break
        logging.info(
            f"[!] UNAPPROVED ITEM DETECTED: {item.name} -> Moving to {target_dest.relative_to(ROOT)}"
        )
        dest_path: Any = target_dest / item.name
        if dest_path.exists():
            ts: Any = datetime.now().strftime("%H%M%S")
            dest_path: Any = target_dest / f"{item.stem}_{ts}{item.suffix}"
            logging.warning(f"    Collision! Renaming to {dest_path.name}")
        try:
            shutil.move(str(item), str(dest_path))
        except Exception as e:
            logging.error(f"    Failed to move {item.name}: {e}")
    for item in ROOT.iterdir():
        if item.is_dir() and item.name not in APPROVED_ROOT_FOLDERS:
            try:
                if not any(item.iterdir()):
                    shutil.rmtree(item)
                    logging.info(f"[✓] Purged empty unapproved shell: {item.name}")
            except:
                pass
    print("\n--- FINAL ROOT AUDIT ---")
    current_root: Any = [i.name for i in ROOT.iterdir()]
    illegal: Any = [
        i for i in current_root if i not in APPROVED_ROOT_FOLDERS and i not in APPROVED_ROOT_FILES
    ]
    if not illegal:
        print("[SUCCESS] Root is 100% Clean. Only Approved Sovereign structures remain.")
    else:
        print(f"[!] WARNING: Root still contains unapproved items: {illegal}")


if __name__ == "__main__":
    scorched_earth_merge()
