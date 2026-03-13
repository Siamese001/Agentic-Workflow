from __future__ import annotations

import logging

from agentic_core.L2_execution.tools import write_gateway as _wg

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from pathlib import Path

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
from typing import Any

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L5_safety.config.structure_blueprint import CORE_SUBFOLDER_MAP

core_map: Any = CORE_SUBFOLDER_MAP
external_map: Any = {
    "apps_rg": ["engines", "templates", "P1_core"],
    "apps_lic": ["engines", "templates", "P1_core"],
    "apps_shared": ["models", "utils", "P1_core"],
    "tests": ["unit", "integration", "e2e", "performance", "fixtures", "security"],
    "data": ["raw", "processed", "vectordb"],
    "archives": ["logs", "backups", "refactors"],
}
annexation_plan: Any = {
    "config": CORE / "config/P1_core",
    "observability": CORE / "observability/P1_core",
    "prompt_governance": CORE / "prompt_governance/P1_core",
    "schemas": CORE / "schemas/P1_core",
    "scripts": CORE / "L0_routing/scripts",
    "prompt_templates": CORE / "prompt_governance/P2_prompts",
}


def forge_fortress() -> Any:
    """Brief description of functionality and purpose."""
    logging.info("FORTRESS FORGE: Initializing System Reconstruction...")
    for layer, stages in CORE_MAP.items():
        layer_path: Any = CORE / layer
        _wg.ensure_dir(layer_path)
        _wg.touch_file(layer_path / "__init__.py")
        for stage in stages:
            stage_path: Any = layer_path / stage
            _wg.ensure_dir(stage_path)
            _wg.touch_file(stage_path / "__init__.py")
            logging.debug(f"Stage Verified: {layer}/{stage}")
    for folder, stages in EXTERNAL_MAP.items():
        folder_path: Any = ROOT / folder
        _wg.ensure_dir(folder_path)
        for stage in stages:
            stage_path: Any = folder_path / stage
            _wg.ensure_dir(stage_path)
            if folder not in ["data", ARCHIVES_DIR]:
                _wg.touch_file(stage_path / "__init__.py")
    for old_name, destination in ANNEXATION_PLAN.items():
        old_path: Any = ROOT / old_name
        if old_path.exists() and old_path.is_dir():
            logging.info(f"Annexing {old_name} territory into Sovereign Core...")
            for item in old_path.iterdir():
                if item.name in CORE_MAP.keys() or item.name == "__init__.py":
                    continue
                target: Any = destination / item.name
                try:
                    if not target.exists():
                        _wg.move_path(str(item), str(target))
                        logging.info(f"  [MOVED] {item.name}")
                    else:
                        logging.warning(f"  [COLLISION] {item.name} exists in target. Manual merge required.")
                # guardian: allow-silent-swallow
                except Exception as e:
                    logging.error(f"  [FAILED] Move {item.name}: {e}")
            if not any(old_path.iterdir()):
                try:
                    _wg.remove_dir(old_path)
                # guardian: allow-silent-swallow
                except:
                    pass
    logging.info("--- FORGE COMPLETE: Sovereign Architecture In Place ---")


if __name__ == "__main__":
    forge_fortress()
