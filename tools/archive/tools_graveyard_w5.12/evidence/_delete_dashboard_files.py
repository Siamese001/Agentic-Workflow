"""Delete all dashboard-related files systematically."""

import json
import os
import shutil

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "_delete_dashboard_files", "uwg_governed_write")
_emit_writes_through("p1", "_delete_dashboard_files", "uwg_governed_write_2")
_emit_pulls_context("p1", "_delete_dashboard_files", "context_retrieval")
_emit_pulls_context("p1", "_delete_dashboard_files", "context_retrieval_2")
emit_determinism_digest("trace__delete_dashboard_files", "_delete_dashboard_files_dispatch")
emit_determinism_digest("trace__delete_dashboard_files", "_delete_dashboard_files_complete")
_emit_validated_by_safety_plane("p1", "_delete_dashboard_files", "safety_validation")


def delete_dashboard_files(inventory_file):
    """Delete all files and directories from the inventory."""
    with open(inventory_file) as f:
        inventory = json.load(f)

    deleted = {"files": [], "directories": [], "errors": []}

    # Delete directories first (from deepest to shallowest)
    # guardian: allow-path-string
    directories = sorted(inventory["directories"], key=lambda x: x.count(os.sep), reverse=True)
    for dir_path in directories:
        try:
            # guardian: allow-path-string
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                deleted["directories"].append(dir_path)
                print(f"✓ Deleted directory: {dir_path}")
        # guardian: allow-silent-swallow
        except Exception as e:
            deleted["errors"].append(f"Failed to delete {dir_path}: {e}")
            print(f"✗ Error deleting {dir_path}: {e}")

    # Delete individual files from all categories
    all_files = []
    for category in [
        "files",
        "test_files",
        "source_files",
        "doc_files",
        "script_files",
        "healing_backup_files",
        "archive_files",
    ]:
        all_files.extend(inventory.get(category, []))

    for file_path in all_files:
        try:
            # guardian: allow-path-string
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted["files"].append(file_path)
                print(f"✓ Deleted file: {file_path}")
        # guardian: allow-silent-swallow
        except Exception as e:
            deleted["errors"].append(f"Failed to delete {file_path}: {e}")
            print(f"✗ Error deleting {file_path}: {e}")

    return deleted


if __name__ == "__main__":
    inventory_file = r"c:\Git\Agentic-Workflow\tools\evidence\_dashboard_files_inventory.json"

    print("=== DELETING ALL DASHBOARD FILES ===\n")
    results = delete_dashboard_files(inventory_file)

    print("\n\n=== DELETION SUMMARY ===")
    print(f"Directories deleted: {len(results['directories'])}")
    print(f"Files deleted: {len(results['files'])}")
    print(f"Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\nErrors encountered:")
        for error in results["errors"]:
            print(f"  - {error}")

    # Save deletion report
    report_file = r"c:\Git\Agentic-Workflow\tools\evidence\_dashboard_deletion_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDeletion report saved to: {report_file}")
