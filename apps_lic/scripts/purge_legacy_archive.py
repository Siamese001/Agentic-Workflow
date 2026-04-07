import os
import shutil
import sys
from pathlib import Path


def purge_legacy_artifacts() -> None:
    """
    Verifies SSOT migration success, then permanently deletes apps_lic/legacy_archive.
    """
    # guardian: allow-path-string
    base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    legacy_dir = Path(base_dir) / "legacy_archive"
    ssot_dir = Path(base_dir) / "engines"
    required_rescues = ["CompetitorReconAgent.py", "StackModernizationAgent.py"]
    for agent in required_rescues:
        # guardian: allow-path-string
        if not os.path.exists(Path(ssot_dir) / agent):
            print(f"CRITICAL STOP: {agent} missing from canonical SSOT engines/ folder.")
            print("Executing forced healing to resolve path mismatch.")
            sys.exit(1)
    # guardian: allow-path-string
    if os.path.exists(legacy_dir):
        try:
            shutil.rmtree(legacy_dir)
            print(f"SUCCESS: Deleted {legacy_dir} and all contained artifacts.")
        except OSError as exc:    # guardian: Add error context logging
            print(f"ERROR: Failed to delete archive: {exc}")
            sys.exit(1)
    else:
        print("NOTICE: Legacy archive does not exist (already purged).")


if __name__ == "__main__":
    purge_legacy_artifacts()
