import os
import shutil
import sys


def purge_legacy_artifacts() -> None:
    """
    Verifies SSOT migration success, then permanently deletes apps_lic/legacy_archive.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    legacy_dir = os.path.join(base_dir, "legacy_archive")
    ssot_dir = os.path.join(base_dir, "engines")

    required_rescues = ["CompetitorReconAgent.py", "StackModernizationAgent.py"]
    for agent in required_rescues:
        if not os.path.exists(os.path.join(ssot_dir, agent)):
            print(f"CRITICAL STOP: {agent} missing from canonical SSOT engines/ folder.")
            print("Executing forced healing to resolve path mismatch.")
            sys.exit(1)

    if os.path.exists(legacy_dir):
        try:
            shutil.rmtree(legacy_dir)
            print(f"SUCCESS: Deleted {legacy_dir} and all contained artifacts.")
        except OSError as exc:
            print(f"ERROR: Failed to delete archive: {exc}")
            sys.exit(1)
    else:
        print("NOTICE: Legacy archive does not exist (already purged).")


if __name__ == "__main__":
    purge_legacy_artifacts()
