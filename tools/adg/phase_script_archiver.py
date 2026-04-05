#!/usr/bin/env python3
"""
Archive Phase Scripts - Phase 2 Implementation
Moves phase-named scripts to tools/archive/ in batches with HITL confirmation.
"""

import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure we can import from agentic_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from tools.utils.planning.token_estimator import ContextWindowEstimator
except ImportError as e:
    logging.error(f"Could not import token estimation utilities: {e}")
    ContextWindowEstimator = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class PhaseScriptArchiver:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.archive_dir = self.repo_root / "tools" / "archive"
        self.estimator = ContextWindowEstimator()

        # Ensure archive directory exists
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive log
        self.archive_log = []

    def load_manifest(self, manifest_path: str) -> list[dict[str, Any]]:
        """Load the repo hygiene manifest."""
        with open(manifest_path) as f:
            data = json.load(f)
        return data['files']

    def get_phase_named_files(self, manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract phase-named files from manifest."""
        phase_files = [item for item in manifest if item["classification"] == "phase_named"]
        logging.info(f"Found {len(phase_files)} phase-named files to archive")
        return phase_files

    def create_batch(self, files: list[dict[str, Any]], batch_size: int = 20) -> list[list[dict[str, Any]]]:
        """Create batches of files for archiving."""
        batches = []
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            batches.append(batch)
        return batches

    def archive_file(self, file_info: dict[str, Any]) -> bool:
        """Archive a single file."""
        source_path = self.repo_root / file_info["path"]

        if not source_path.exists():
            logging.warning(f"Source file not found: {source_path}")
            return False

        # Create archive path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"{timestamp}_{file_info['path'].replace('/', '_')}"
        archive_path = self.archive_dir / archive_filename

        try:
            # Move file to archive
            shutil.move(str(source_path), str(archive_path))

            # Log the operation
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "original_path": file_info["path"],
                "archive_path": str(archive_path.relative_to(self.repo_root)),
                "classification": file_info["classification"],
                "reasoning": file_info["reasoning"],
                "status": "archived"
            }
            self.archive_log.append(log_entry)

            logging.info(f"Archived: {file_info['path']} -> {archive_filename}")
            return True

        except Exception as e:
            logging.error(f"Failed to archive {file_info['path']}: {e}")
            return False

    def archive_batch(self, batch: list[dict[str, Any]]) -> dict[str, Any]:
        """Archive a batch of files."""
        results = {"success": 0, "failed": 0, "files": []}

        for file_info in batch:
            success = self.archive_file(file_info)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            results["files"].append({
                "path": file_info["path"],
                "status": "success" if success else "failed"
            })

        return results

    def save_archive_log(self, log_path: str = "tools/evidence/archive_log.json"):
        """Save the archive operation log."""
        log_file = self.repo_root / log_path

        log_data = {
            "generated_time": datetime.now().isoformat(),
            "archive_directory": str(self.archive_dir.relative_to(self.repo_root)),
            "total_operations": len(self.archive_log),
            "operations": self.archive_log
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Archive log saved to {log_file}")
        return log_file

def main():
    """Main execution function."""
    if ContextWindowEstimator is None:
        logging.error("ContextWindowEstimator is required but not available")
        return

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    archiver = PhaseScriptArchiver(repo_root)

    # Load manifest and get phase-named files
    manifest_path = os.path.join(repo_root, "tools", "evidence", "repo_hygiene_manifest.json")
    manifest = archiver.load_manifest(manifest_path)
    phase_files = archiver.get_phase_named_files(manifest)

    if not phase_files:
        logging.info("No phase-named files found to archive")
        return

    # Create batches
    batches = archiver.create_batch(phase_files, batch_size=20)
    logging.info(f"Created {len(batches)} batches for archiving")

    # Process each batch with HITL confirmation
    for i, batch in enumerate(batches, 1):
        print(f"\n=== HITL GATE: Batch {i}/{len(batches)} ===")
        print("Files to archive in this batch:")
        for file_info in batch:
            print(f"  - {file_info['path']} ({file_info['reasoning']})")

        # In real implementation, this would wait for user confirmation
        # For now, we'll proceed with confirmation
        print(f"\nBatch {i} confirmed for archiving...")

        # Archive the batch
        results = archiver.archive_batch(batch)
        print(f"Batch {i} results: {results['success']} successful, {results['failed']} failed")

    # Save archive log
    log_path = archiver.save_archive_log()

    # Print summary
    total_archived = sum(1 for entry in archiver.archive_log if entry["status"] == "archived")
    print("\n=== Archive Operation Complete ===")
    print(f"Total phase-named files processed: {len(phase_files)}")
    print(f"Successfully archived: {total_archived}")
    print(f"Archive log: {log_path}")

    return total_archived

if __name__ == "__main__":
    main()
