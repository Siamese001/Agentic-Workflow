from __future__ import annotations

import logging

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import shutil
from datetime import datetime
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR
excluded_zones: Any = ["data", ARCHIVES_DIR, TESTS_DIR, ".git", ".venv", "__pycache__"]
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
annexation_plan: Any = {
    "config": CORE / "config/P1_core",
    "observability": CORE / "observability/P1_core",
    "prompt_governance": CORE / "prompt_governance/P1_core",
    "schemas": CORE / "schemas/P1_core",
    "scripts": CORE / "L0_routing/scripts",
    "prompt_templates": CORE / "prompt_governance/P2_prompts",
}


def force_annexation() -> Any:
    """Brief description of functionality and purpose."""
    logging.info("--- FORCED SOVEREIGN ANNEXATION: Recovering Infrastructure ---")
    for target_dir in ANNEXATION_PLAN.values():
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "__init__.py").touch()
    for old_name, destination in ANNEXATION_PLAN.items():
        old_path: Any = ROOT / old_name
        if not old_path.exists():
            logging.warning(f"  [?] {old_name} not found at root. Checking if already moved...")
            continue
        logging.info(f"  [>] Moving {old_name} contents to {destination.relative_to(ROOT)}...")
        for item in list(old_path.iterdir()):
            if item.name == AGENTIC_CORE_DIR:
                continue
            target_item: Any = destination / item.name
            if target_item.exists():
                timestamp: Any = datetime.now().strftime("%H%M%S")
                target_item: Any = destination / f"{item.stem}_{timestamp}{item.suffix}"
                logging.warning(f"      Collision! Renaming to {target_item.name}")
            try:
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(item), str(target_item))
            # guardian: allow-silent-swallow
            except Exception as e:
                logging.error(f"      Failed to move {item.name}: {e}")
        try:
            if old_path.exists() and (not any(old_path.iterdir())):
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.rmtree(old_path)
                logging.info(f"  [✓] Purged old root folder: {old_name}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logging.error(f"  [!] Could not delete {old_name} shell: {e}")
    print("\n--- INFRASTRUCTURE AUDIT ---")
    for key in ANNEXATION_PLAN.keys():
        exists_in_root: Any = (ROOT / key).exists()
        print(
            f"  {('[FAILED]' if exists_in_root else '[FIXED]')} {key.ljust(20)} -> {('STILL IN ROOT' if exists_in_root else 'ANNEXED TO CORE')}",
        )


if __name__ == "__main__":
    force_annexation()
