"""
Enhanced cleanup script that moves files to sovereign silos
"""

import argparse
import logging
import os
import shutil
from typing import Any
from tqdm import tqdm

try:
    from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import (
        AGENTIC_CORE_DIR,
        OPS_SCRIPTS_DIR,
        SCRIPTS_DIR,
        TESTS_DIR,
    )
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    AGENTIC_CORE_DIR = AGENTIC_CORE_DIR
    SCRIPTS_DIR = OPS_SCRIPTS_DIR
    TESTS_DIR = TESTS_DIR
logging.basicConfig(level=logging.INFO, format="%(message)s")
Logger: Any = logging.getLogger(__name__)


def move_files_to_silos() -> Any:
    """Move Python files from root to appropriate sovereign silos"""
    Logger.info("📁 Moving files to sovereign silos...")
    silo_mappings: Any = {
        AGENTIC_CORE_DIR: [
            "ActionNode",
            "agent_logic",
            "CognitiveNode",
            "ConsensusEngine",
            "core_utils",
            "action_registry",
            "agent_capabilities",
        ],
        APPS_LIC_DIR: ["CanonValidatorAgent", "canon_keys", "validator", "canon"],
        APPS_RG_DIR: ["orchestrator", "llm_client", "connection_manager", "monitor_blackboard"],
        APPS_SHARED_DIR: ["db_manager", "etl_pipeline", "FactChecker", "clarity_brevity_filter"],
        SCRIPTS_DIR: [
            "clean_duplicates",
            "fix_",
            "assess_dependencies",
            "check_pinecone",
            "clear_data",
            "canary_monitor",
            "bad_actor",
            "debug_whitelist",
        ],
        TESTS_DIR: ["test_", "tests_", "_test"],
    }
    moved_count: Any = 0
    # guardian: allow-path-string
    root_files: Any = [f for f in os.listdir("/app") if f.endswith(".py") and os.path.isfile(f"/app/{f}")]
    for filename in tqdm(root_files, desc="Processing", unit="item"):
        if filename in ["entrypoint.sh", "Dockerfile", "docker-compose.yml", "requirements.txt"]:
            continue
        target_silo: Any = None
        filename_lower: Any = filename.lower()
        for silo, keywords in silo_mappings.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    target_silo: Any = silo
                    break
            if target_silo:
                break
        if not target_silo:
            target_silo: Any = APPS_SHARED_DIR
        silo_path: Any = f"/app/{target_silo}"
        os.makedirs(silo_path, exist_ok=True)
        src_path: Any = f"/app/{filename}"
        dst_path: Any = f"{silo_path}/{filename}"
        try:
            # guardian: allow-path-string
            if not os.path.exists(dst_path):
                shutil.move(src_path, dst_path)
                Logger.info(f"📁 Moved {filename} -> {target_silo}/")
                moved_count += 1
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"❌ Failed to move {filename}: {e}")
    Logger.info(f"\n✨ Moved {moved_count} files to sovereign silos")
    return moved_count


def main() -> Any:
    """Brief description of functionality and purpose."""
    parser: Any = argparse.ArgumentParser(description="Move files to sovereign silos")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be moved without actually moving"
    )
    args: Any = parser.parse_args()
    if args.dry_run:
        Logger.info("🔍 DRY RUN - No files will be moved")
    else:
        move_files_to_silos()


if __name__ == "__main__":
    main()
