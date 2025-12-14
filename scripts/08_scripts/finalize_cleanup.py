#!/usr/bin/env python3
"""Finalize cleanup - handle orphans and clean merged files."""

import os
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path("/workspace")
BACKUP_DIR = ROOT / "archives" / f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_finaliz
    e"

def backup_file(file_path: Path):
    """Docstring."""
import logging

logger = logging.getLogger(__name__)

    """Backup a file before modification."""
    if file_path.exists():
        backup_path = BACKUP_DIR / file_path.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        logger.info(f"  ✓ Backed up: {file_path.relative_to(ROOT)}")

def clean_merged_file(file_path: Path):
    """Remove duplicate imports and docstrings from merged files."""
    if not file_path.exists():
        logger.info(f"  ⚠ File not found: {file_path.relative_to(ROOT)}")
        return

    logger.info(f"Cleaning: {file_path.relative_to(ROOT)}")
    backup_file(file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by merge markers
    parts = content.split('# ============================================')

    if len(parts) <= 1:
        logger.info(f"  ℹ No merge markers found")
        return

    # Keep first part (original)
    cleaned = parts[0].rstrip()

    # Process merged parts
    for i in range(1, len(parts)):
        part = parts[i]
        lines = part.split('\n')

        # Skip merge comment lines
        code_lines = []
        skip_header = True

        for line in lines:
            stripped = line.strip()

            if skip_header:
                # Skip merge comments, docstrings, and imports
                if not stripped:
                    continue
                if stripped.startswith('#'):
                    continue
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                if stripped.startswith('from ') or stripped.startswith('import '):
                    continue
                skip_header = False

            code_lines.append(line)

        # Add cleaned content
        if code_lines:
            cleaned += '\n\n' + '\n'.join(code_lines).strip()

    # Write cleaned content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned + '\n')

    logger.info(f"  ✓ Cleaned")

def rename_orphan(src: Path, dst: Path):
    """Rename orphan file by removing _2 suffix."""
    if not src.exists():
        logger.info(f"  ⚠ File not found: {src.relative_to(ROOT)}")
        return

    backup_file(src)
    src.rename(dst)
    logger.info(f"  ✓ Renamed: {src.name} → {dst.name}")

def main():
    """Docstring."""
    logger.info("=" * 50)
    logger.info("Finalizing Duplicate File Cleanup")
    logger.info("=" * 50)
    logger.info()

    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Backup directory: {BACKUP_DIR.relative_to(ROOT)}")
    logger.info()

    # Step 1: Clean merged files
    logger.info("━" * 50)
    logger.info("STEP 1: Clean merged files")
    logger.info("━" * 50)
    logger.info()

    merged_files = [
        ROOT / "config/config_models.py",
        ROOT / "config/logic/data_access/get_info/load_planning_models.py",
        ROOT / "apps_lic/L1_cognition/P3_aggregate/lic_archetypes_models.py",
        ROOT / "apps_lic/L2_execution/data_models_models.py",
        ROOT / "apps_rg/L1_cognition/k25_models.py",
        ROOT / "schemas/logic/data_access/get_schema_request/load_schema_planning_models.py",
        ROOT / "shared/configuration/config_types_part.py",
        ROOT / "shared/core/config_types_part.py",
        ROOT / "shared/core/exceptions_impl_part.py",
        ROOT / "shared/core/models_types_part.py",
        ROOT / "shared/errors/exceptions_impl_part.py",
        ROOT / "shared/result_types_types_part.py",
        ROOT / "shared/types/models_types_part.py",
    ]

    for file_path in merged_files:
        clean_merged_file(file_path)

    # Step 2: Rename orphans
    logger.info()
    logger.info("━" * 50)
    logger.info("STEP 2: Rename orphan files")
    logger.info("━" * 50)
    logger.info()

    orphans = [
        (ROOT / "apps_lic/L1_cognition/P3_aggregate/route_models_2.py",
         ROOT / "apps_lic/L1_cognition/P3_aggregate/route_models.py"),
        (ROOT / "apps_rg/L1_cognition/P3_aggregate/brief_models_2.py",
         ROOT / "apps_rg/L1_cognition/P3_aggregate/brief_models.py"),
        (ROOT / "apps_rg/L3_orchestration/wf_types_models_2.py",
         ROOT / "apps_rg/L3_orchestration/wf_types_models.py"),
        (ROOT / "config/logic/data_access/get_info/load_models_2.py",
         ROOT / "config/logic/data_access/get_info/load_models.py"),
        (ROOT / "observability/pipeline/data_access/get_info/obs_models_2.py",
         ROOT / "observability/pipeline/data_access/get_info/obs_models.py"),
        (ROOT / "shared/safety/const_ai_part_2.py",
         ROOT / "shared/safety/const_ai_part.py"),
        (ROOT / "shared/types/wf_types_part_2.py",
         ROOT / "shared/types/wf_types_part.py"),
    ]

    for src, dst in orphans:
        rename_orphan(src, dst)

    logger.info()
    logger.info("━" * 50)
    logger.info("✅ Finalization Complete!")
    logger.info("━" * 50)
    logger.info()
    logger.info("Summary:")
    logger.info(f"  - Cleaned {len(merged_files)} merged files")
    logger.info(f"  - Renamed {len(orphans)} orphan files")
    logger.info(f"  - Backup: {BACKUP_DIR.relative_to(ROOT)}")

if __name__ == '__main__':
    main()
