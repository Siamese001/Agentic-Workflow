import os


# ============================================================
# TARGET SUBFOLDER DEFINITIONS
# ============================================================

BASE = "apps"

TARGET_STRUCTURE = {
    "config": {
        "environment": [],
        "models": [],
        "validation": [],
        "system": [],
        "logging": [],
        "windsurf": [],
    },

    "services": {
        "telemetry": [],
        "cache": [],
        "errors": [],
        "config_loader": [],
        "rate_limiting": [],
        "security": [],
    },

    "docs": {
        "architecture": [],
        "validation": [],
        "reports": ["progress_reports", "gap_reports"],
        "dev_guides": [],
        "playbooks": [],
    },

    "api": {
        "resume": [],
        "outreach": [],
        "admin": [],
        "health": [],
        "middleware": [],
        "routers": [],
    }
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
    """Create the entire standardized apps/ folder structure."""
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
# FILE CLASSIFICATION LOGIC
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

    return "system"  # fallback


def classify_service_file(filename):
    name = filename.lower()

    if "telemetry" in name:
        return "telemetry"
    if "cache" in name:
        return "cache"
    if "error" in name:
        return "errors"
    if "config" in name:
        return "config_loader"
    if "rate" in name:
        return "rate_limiting"
    if "auth" in name or "security" in name:
        return "security"

    return "errors"  # fallback


def classify_docs_file(filename):
    name = filename.lower()

    if "architecture" in name:
        return "architecture"
    if "validation" in name:
        return "validation"
    if "report" in name:
        return "reports"
    if "guide" in name or "dev" in name:
        return "dev_guides"
    if "playbook" in name:
        return "playbooks"

    return "architecture"  # fallback


def classify_api_file(filename):
    name = filename.lower()

    if "resume" in name:
        return "resume"
    if "outreach" in name:
        return "outreach"
    if "admin" in name:
        return "admin"
    if "health" in name:
        return "health"
    if "middleware" in name:
        return "middleware"

    return "routers"  # fallback


# ============================================================
# FILE MIGRATION LOGIC (DRY RUN)
# ============================================================

def move_config_files():
    src = os.path.join(BASE, "config")
    if not os.path.exists(src):
        return

    for root, dirs, files in os.walk(src):
        for f in files:
            # Handle both .py and .json files in config
            if f.endswith((".json", ".py", ".ini", ".toml")):
                target = classify_config_file(f)
                dest = os.path.join(BASE, "config", target, f)
                src_path = os.path.join(root, f)
                if os.path.abspath(dest) != os.path.abspath(src_path):
                    print(f"[DRY RUN MOVE] {src_path} → {dest}")
                    # shutil.move(src_path, dest)  # Commented out for dry run


def move_service_files():
    # Currently services folder empty — but future-proof patterns
    src = os.path.join(BASE, "services")
    if not os.path.exists(src):
        return

    for root, dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".py"):
                target = classify_service_file(f)
                dest = os.path.join(BASE, "services", target, f)
                src_path = os.path.join(root, f)
                if os.path.abspath(dest) != os.path.abspath(src_path):
                    print(f"[DRY RUN MOVE] {src_path} → {dest}")
                    # shutil.move(src_path, dest)  # Commented out for dry run


def move_docs_files():
    src = os.path.join(BASE, "docs")
    if not os.path.exists(src):
        return

    for root, dirs, files in os.walk(src):
        for f in files:
            if f.lower().endswith((".md", ".txt")):
                target = classify_docs_file(f)
                dest = os.path.join(BASE, "docs", target, f)
                src_path = os.path.join(root, f)
                if os.path.abspath(dest) != os.path.abspath(src_path):
                    print(f"[DRY RUN MOVE] {src_path} → {dest}")
                    # shutil.move(src_path, dest)  # Commented out for dry run


def move_api_files():
    src = os.path.join(BASE, "api")
    if not os.path.exists(src):
        return

    for root, dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".py"):
                target = classify_api_file(f)
                dest = os.path.join(BASE, "api", target, f)
                src_path = os.path.join(root, f)
                if os.path.abspath(dest) != os.path.abspath(src_path):
                    print(f"[DRY RUN MOVE] {src_path} → {dest}")
                    # shutil.move(src_path, dest)  # Commented out for dry run


# ============================================================
# CLEANUP OLD EMPTY FOLDERS
# ============================================================

def delete_empty_folders():
    for root, dirs, files in os.walk(BASE, topdown=False):
        if root == BASE:
            continue
        if not dirs and not files:
            print(f"[DRY RUN DELETE EMPTY] {root}")
            # os.rmdir(root)  # Commented out for dry run


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n=== DRY RUN: Creating target apps subfolder structure ===")
    create_target_folders()

    print("\n=== DRY RUN: Migrating config files ===")
    move_config_files()

    print("\n=== DRY RUN: Migrating services files ===")
    move_service_files()

    print("\n=== DRY RUN: Migrating docs files ===")
    move_docs_files()

    print("\n=== DRY RUN: Migrating api files ===")
    move_api_files()

    print("\n=== DRY RUN: Cleaning up empty folders ===")
    delete_empty_folders()

    print("\n=== DRY RUN: APPS SUBFOLDER MIGRATION COMPLETE ===\n")
