#!/usr/bin/env python3
"""
Sovereign V2.5 Migration Executor for apps_rg
Reads RG_AUDIT_MANIFEST.json and physically restructures the repository.
usage: python scripts/rg_migrate_structure.py
"""

import json
import logging
import os
import re
import shutil
from pathlib import Path

from agentic_core.L0_routing.config import (
    APPS_RG_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.config.path_constants import TOOLS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [MIGRATE] - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define Root relative to this script (scripts/ -> root)
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_RG_DIR = BASE_DIR / APPS_RG_DIR
MANIFEST_PATH = APPS_RG_DIR / "RG_AUDIT_MANIFEST.json"

# Approved Sovereign Structure
DIRS = {
    "engines": APPS_RG_DIR / "engines",
    "tools": APPS_RG_DIR / "shared/tools",
    "types": APPS_RG_DIR / "domain/types",
    "legacy": APPS_RG_DIR / "legacy",
    "quarantine": APPS_RG_DIR / "legacy/quarantine_broken",
}


class MigrationExecutor:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.manifest = self._load_manifest()
        self.moved_files: dict[str, str] = {}  # old_name -> new_full_path

    def _load_manifest(self) -> dict:
        if not MANIFEST_PATH.exists():
            raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")
        with open(MANIFEST_PATH) as f:
            return json.load(f)

    def _ensure_dirs(self):
        """Create target directories if they don't exist."""
        for name, path in DIRS.items():
            if not path.exists():
                logger.info(f"Creating directory: {path}")
                if not self.dry_run:
                    path.mkdir(parents=True, exist_ok=True)
                    # Create __init__.py for python packages
                    if name in [TOOLS_DIR, "types", "engines"]:
                        init_file = path / "__init__.py"
                        if not init_file.exists():
                            init_file.touch()

    def _move_file(self, src_rel: str, dest_dir: Path, new_name: str = None) -> bool:
        """Move a file safely from relative path (e.g., apps_rg/engines/file.py)."""
        # Handle path normalization
        src_clean = src_rel.replace("\\", "/")
        src_path = BASE_DIR / src_clean

        if not src_path.exists():
            logger.warning(f"Source file not found: {src_path}")
            return False

        filename = new_name if new_name else src_path.name
        dest_path = dest_dir / filename

        if self.dry_run:
            logger.info(f"[DRY RUN] Move {src_path.name} -> {dest_path}")
            return True

        try:
            shutil.move(str(src_path), str(dest_path))
            self.moved_files[src_path.stem] = str(dest_path)
            logger.info(f"Moved: {src_path.name} -> {dest_path}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to move {src_path.name}: {e}")
            return False

    def process_quarantine(self):
        """Move broken files to legacy/quarantine."""
        broken = self.manifest.get("actions", {}).get("fix_syntax_errors", [])
        logger.info(f"Processing {len(broken)} broken files...")
        for f in broken:
            self._move_file(f, DIRS["quarantine"])

    def process_legacy(self):
        """Archive legacy files."""
        legacy = self.manifest.get("actions", {}).get("archive_legacy", [])
        logger.info(f"Archiving {len(legacy)} legacy files...")
        for f in legacy:
            self._move_file(f, DIRS["legacy"])

    def process_types(self):
        """Rename and move Imposter Agents to domain/types."""
        types_map = self.manifest.get("actions", {}).get("move_to_domain_types", {})
        logger.info(f"Migrating {len(types_map)} type definitions...")
        for src, new_name in types_map.items():
            self._move_file(src, DIRS["types"], new_name=new_name)

    def process_tools(self):
        """Move stateless tools to shared/tools."""
        tools = self.manifest.get("actions", {}).get("move_to_tools", [])
        logger.info(f"Migrating {len(tools)} stateless tools...")
        for f in tools:
            self._move_file(f, DIRS["tools"])

    def process_unknowns(self):
        """Leave Unknowns in Engines but Log them (Passive Review)."""
        # Per review: Do not move unknowns blindly. Just log them.
        unknowns = self.manifest.get("actions", {}).get("unknown_require_manual_review", [])
        logger.info(
            f"PENDING REVIEW: {len(unknowns)} files remain in engines/ for manual classification.",
        )

    def patch_imports(self):
        """Scan apps_rg/engines/ and update imports for moved tools/types."""
        if self.dry_run:
            return

        logger.info("Starting Import Patching Sequence...")

        # 1. Patch Tools Imports
        tools = [Path(p).stem for p in self.manifest.get("actions", {}).get("move_to_tools", [])]
        if tools:
            # Matches: from apps_rg.engines.toolname import ...
            # guardian: allow-path-string
            pattern = r"from apps_rg\.engines\.(" + "|".join(map(re.escape, tools)) + r")"
            replacement = r"from apps_rg.tools.\1"
            self._apply_regex_patch(pattern, replacement)

        # 2. Patch Types Imports
        types_map = self.manifest.get("actions", {}).get("move_to_domain_types", {})
        for src, new_filename in types_map.items():
            old_module = Path(src).stem
            new_module = Path(new_filename).stem

            # Case: from apps_rg.engines.OldAgent import X
            p1 = f"from apps_rg.engines.{old_module}"
            r1 = f"from apps_rg.types.{new_module}"
            self._apply_string_replace(p1, r1)

    def _apply_regex_patch(self, pattern: str, replacement: str):
        """Apply regex sub to all .py files in apps_rg."""
        regex = re.compile(pattern)
        for root, dirs, files in os.walk(APPS_RG_DIR):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for file in files:
                if file.endswith(".py"):
                    path = Path(root) / file
                    try:
                        content = path.read_text(encoding="utf-8")
                        if regex.search(content):
                            new_content = regex.sub(replacement, content)
                            path.write_text(new_content, encoding="utf-8")
                            logger.info(f"Patched imports in {path.name}")
                    # guardian: allow-silent-swallow
                    except Exception as e:
                        logger.error(f"Failed to patch {path.name}: {e}")

    def _apply_string_replace(self, old: str, new: str):
        for root, dirs, files in os.walk(APPS_RG_DIR):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for file in files:
                if file.endswith(".py"):
                    path = Path(root) / file
                    try:
                        content = path.read_text(encoding="utf-8")
                        if old in content:
                            new_content = content.replace(old, new)
                            path.write_text(new_content, encoding="utf-8")
                            logger.info(f"Replaced '{old}' in {path.name}")
                    # guardian: allow-silent-swallow
                    except Exception as e:
                        logger.error(f"Failed to patch {path.name}: {e}")

    def execute(self):
        logger.info("=== STARTING SOVEREIGN MIGRATION ===")
        self._ensure_dirs()
        self.process_quarantine()
        self.process_legacy()
        self.process_types()
        self.process_tools()
        self.process_unknowns()
        self.patch_imports()
        logger.info("=== MIGRATION COMPLETE ===")


if __name__ == "__main__":
    # Safety: Run immediately
    executor = MigrationExecutor(dry_run=False)
    executor.execute()
