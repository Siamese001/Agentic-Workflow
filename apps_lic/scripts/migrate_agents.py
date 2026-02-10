import os
import shutil


def migrate_rescued_agents() -> None:
    """
    Moves the enriched agents from legacy_archive to the apps_lic/engines SSOT.
    """
    # guardian: allow-path-string
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # guardian: allow-path-string
    source_dir = os.path.join(base_dir, "legacy_archive")
    # guardian: allow-path-string
    target_dir = os.path.join(base_dir, "engines")  # SSOT: APP_SPECIFIC_TARGET_SUBFOLDER

    os.makedirs(target_dir, exist_ok=True)

    # guardian: allow-path-string
    init_path = os.path.join(target_dir, "__init__.py")
    # guardian: allow-path-string
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as handle:
            handle.write('"""SSOT Agents Package generated during migration."""\n')

    files_to_move = [
        "CompetitorReconAgent.py",
        "StackModernizationAgent.py",
    ]

    for filename in files_to_move:
        # guardian: allow-path-string
        src = os.path.join(source_dir, filename)
        # guardian: allow-path-string
        dst = os.path.join(target_dir, filename)

        # guardian: allow-path-string
        if os.path.exists(src):
            # guardian: allow-path-string
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
