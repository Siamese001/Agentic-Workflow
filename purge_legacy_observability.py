import shutil
from pathlib import Path


def purge_legacy_observability():
    project_root = Path.cwd()
    legacy_path = project_root / "agentic_core" / "observability"

    if legacy_path.exists():
        print(f"🗑️ Removing legacy ghost directory: {legacy_path}")
        # Standard safety check: ensure no critical files are left
        shutil.rmtree(legacy_path)
        print("✅ Purge complete. Legacy directory eliminated.")
    else:
        print("ℹ️ Legacy directory already removed or does not exist.")


if __name__ == "__main__":
    purge_legacy_observability()
