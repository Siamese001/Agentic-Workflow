import os
import shutil


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def migrate_rescued_agents() -> None:
    """
    Moves the enriched agents from legacy_archive to the apps_lic/engines SSOT.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(base_dir, "legacy_archive")
    target_dir = os.path.join(base_dir, "engines")  # SSOT: APP_SPECIFIC_TARGET_SUBFOLDER

    os.makedirs(target_dir, exist_ok=True)

    init_path = os.path.join(target_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as handle:
            handle.write('"""SSOT Agents Package generated during migration."""\n')

    files_to_move = [
        "CompetitorReconAgent.py",
        "StackModernizationAgent.py",
    ]

    for filename in files_to_move:
        src = os.path.join(source_dir, filename)
        dst = os.path.join(target_dir, filename)

        if os.path.exists(src):
            if os.path.exists(dst):
                print(
                    f"WARNING: Target {filename} already exists in engines/. "
                    "Overwriting with Enriched version.",
                )

            shutil.move(src, dst)
            print(f"SUCCESS: Moved {filename} to {target_dir}")
        else:
            print(f"ERROR: Source file {filename} not found in archive.")


if __name__ == "__main__":
    migrate_rescued_agents()
