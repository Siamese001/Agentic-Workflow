import os
import shutil


# ============================================================
# CONSERVATIVE SUBFOLDER DEFINITIONS (CONFIG & DOCS ONLY)
# ============================================================

BASE = "apps"

# Only organize config and docs - preserve api/, services/, and all app directories
TARGET_STRUCTURE = {
    "config": {
        "environment": [],
        "models": [],
        "validation": [],
        "system": [],
        "logging": [],
        "windsurf": [],
    },

    "docs": {
        "architecture": [],
        "validation": [],
        "reports": ["progress_reports", "gap_reports"],
        "dev_guides": [],
        "playbooks": [],
    }
}

# Directories to preserve (never delete or modify)
PRESERVE_DIRECTORIES = {
    "api", "services", "cli", "resume_app", "outreach_app", "shared_app"
}


# ============================================================
# FOLDER CREATION HELPER
# ============================================================

def ensure(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[CREATE] {path}")
    else:
        print(f"[EXISTS] {path}")


def create_target_folders():
    """Create only config and docs subfolder structure."""
    for top_level, subfolders in TARGET_STRUCTURE.items():
        top_path = os.path.join(BASE, top_level)
        ensure(top_path)

        for sub, children in subfolders.items():
            sub_path = os.path.join(top_path, sub)
            ensure(sub_path)

            for child in children:
                child_path = os.path.join(sub_path, child)
                ensure(child_path)


# ============================================================
# IMPROVED FILE CLASSIFICATION LOGIC
# ============================================================

def classify_config_file(filename):
    """Determine correct config/ subfolder based on filename keywords."""
    name = filename.lower()

    if "env" in name:
        return "environment"
    if "model" in name:
        return "models"
    if "schema" in name or "validate" in name:
        return "validation"
    if "log" in name:
        return "logging"
    if "windsurf" in name:
        return "windsurf"
    if "mypy" in name or "pytest" in name or "pyproject" in name:
        return "validation"  # Development tools go in validation

    return "system"  # fallback


def classify_docs_file(filename):
    """Improved docs classification based on content keywords."""
    name = filename.lower()

    # Priority classification for compound keywords
    if "violations" in name and "progress" in name:
        return "validation"
    if "validation" in name and ("report" in name or "gap" in name):
        return "validation"
    if "report" in name and ("progress" in name or "infrastructure" in name or "final" in name):
        return "reports"
    if "validation" in name:
        return "validation"
    if "architecture" in name or "design" in name or "pillar" in name:
        return "architecture"
    if "guide" in name or "dev" in name:
        return "dev_guides"
    if "playbook" in name:
        return "playbooks"
    if "technical" in name or "debt" in name:
        return "architecture"  # Technical docs go to architecture

    return "architecture"  # fallback


# ============================================================
# SAFE FILE MIGRATION LOGIC
# ============================================================

def move_config_files():
    """Safely move config files to appropriate subfolders."""
    src = os.path.join(BASE, "config")
    if not os.path.exists(src):
        return

    moved_files = []
    for root, dirs, files in os.walk(src):
        # Skip newly created subfolders to avoid re-moving files
        if any(subfolder in root for subfolder in TARGET_STRUCTURE["config"].keys()):
            continue

        for f in files:
            if f.endswith((".json", ".py", ".ini", ".toml")):
                target = classify_config_file(f)
                dest = os.path.join(BASE, "config", target, f)
                src_path = os.path.join(root, f)

                if os.path.abspath(dest) != os.path.abspath(src_path):
                    print(f"[MOVE] {src_path} → {dest}")
                    shutil.move(src_path, dest)
                    moved_files.append(f)

    print(f"Moved {len(moved_files)} config files")


def move_docs_files():
    """Safely move docs files to appropriate subfolders."""
    src = os.path.join(BASE, "docs")
    if not os.path.exists(src):
        return

    moved_files = []
    for root, dirs, files in os.walk(src):
        # Skip newly created subfolders to avoid re-moving files
        if any(subfolder in root for subfolder in TARGET_STRUCTURE["docs"].keys()):
            continue

        for f in files:
            if f.lower().endswith((".md", ".txt")):
                target = classify_docs_file(f)
                dest = os.path.join(BASE, "docs", target, f)
                src_path = os.path.join(root, f)

                if os.path.abspath(dest) != os.path.abspath(src_path):
                    print(f"[MOVE] {src_path} → {dest}")
                    shutil.move(src_path, dest)
                    moved_files.append(f)

    print(f"Moved {len(moved_files)} docs files")


# ============================================================
# SAFE CLEANUP (ONLY CONFIG/DOCS EMPTY FOLDERS)
# ============================================================

def cleanup_config_docs_empty_folders():
    """Only clean up empty folders in config and docs, preserve all app directories."""
    for root, dirs, files in os.walk(BASE, topdown=False):
        # Skip preserved directories entirely
        if any(preserve_dir in root for preserve_dir in PRESERVE_DIRECTORIES):
            continue

        # Only clean config and docs subfolders
        if not (root.startswith(os.path.join(BASE, "config")) or
                root.startswith(os.path.join(BASE, "docs"))):
            continue

        if root == BASE:
            continue

        if not dirs and not files:
            print(f"[DELETE EMPTY] {root}")
            os.rmdir(root)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n=== CONSERVATIVE: Creating config & docs subfolder structure ===")
    create_target_folders()

    print("\n=== CONSERVATIVE: Migrating config files ===")
    move_config_files()

    print("\n=== CONSERVATIVE: Migrating docs files ===")
    move_docs_files()

    print("\n=== CONSERVATIVE: Cleaning up empty config/docs folders ===")
    cleanup_config_docs_empty_folders()

    print("\n=== CONSERVATIVE SUBFOLDER MIGRATION COMPLETE ===")
    print("Preserved: api/, services/, cli/, resume_app/, outreach_app/, shared_app/")
