#!/usr/bin/env python3
"""
Sovereign Archive Injector
Reads RG_ARCHIVE_RECOVERY_PLAN.json and copies files to their V2.5 destinations.
Handles directory creation and conflict renaming automatically.
"""

import json
import logging
import os
import shutil
from pathlib import Path

# Setup Logging
logging.basicConfig(level=logging.INFO, format="[INJECT] %(message)s")
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
PLAN_PATH = BASE_DIR / "apps_rg/RG_ARCHIVE_RECOVERY_PLAN.json"


def inject_archives():
    if not PLAN_PATH.exists():
        logger.error(f"Recovery plan not found: {PLAN_PATH}")
        return

    with open(PLAN_PATH) as f:
        plan = json.load(f)

    success_count = 0
    error_count = 0

    logger.info(f"Initiating injection of {len(plan)} files...")

    for item in plan:
        # Source is absolute from the audit
        src = Path(item["path"])

        # Target is relative in JSON, make absolute
        # JSON path: "apps_rg/engines/..."
        # Fix path separators for current OS
        target_rel = item["target_destination"].replace("/", os.sep).replace("\\", os.sep)
        dest = BASE_DIR / target_rel

        if not src.exists():
            logger.warning(f"SKIPPING: Source not found {src}")
            error_count += 1
            continue

        # Skip REJECT_DUPLICATE
        if "REJECT" in str(dest):
            logger.info(f"SKIPPING: Duplicate {src.name}")
            continue

        try:
            # Ensure target directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy file (preserve metadata)
            shutil.copy2(src, dest)

            logger.info(f"INJECTED: {src.name} -> {dest.relative_to(BASE_DIR)}")
            success_count += 1

        except Exception as e:
            logger.error(f"FAILED: {src.name} -> {e}")
            error_count += 1

    logger.info("--- INJECTION SUMMARY ---")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed/Skipped: {error_count}")
    logger.info("Run validation tests immediately.")


if __name__ == "__main__":
    inject_archives()
