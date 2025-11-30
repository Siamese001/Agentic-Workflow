import os
import shutil

# ============================================================
# CONFIGURE TARGET STRUCTURE
# ============================================================

NEW_STRUCTURE = {
    "tests/data": [],
    "tests/fixtures": [],
    "tests/e2e": [],
    "tests/integration": [],
    "tests/l1/integration": [],
    "tests/l1/unit": [],
    "tests/l2/integration": [],
    "tests/l2/unit": [],
    "tests/l3/orchestration": [],
    "tests/l4/memory": [],
    "tests/l5/safety": [],
    "tests/regression": [],
}

# ============================================================
# HELPERS
# ============================================================

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"[CREATE] {path}")

def safe_move(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    print(f"[MOVE] {src} → {dst}")
    shutil.move(src, dst)

def delete_if_empty(folder):
    """Deletes folder if empty (recursively upward)."""
    if not os.path.exists(folder):
        return
    if len(os.listdir(folder)) == 0:
        print(f"[DELETE] Empty folder removed: {folder}")
        os.rmdir(folder)

def merge_files_into_new_structure(ROOT):
    """Moves all files from old test structure into the new canonical structure."""
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "tests")):
        # Skip __pycache__ always
        if "__pycache__" in dirpath:
            continue
        for f in filenames:
            if f.endswith(".pyc"):
                continue
            src = os.path.join(dirpath, f)

            # Already in correct place?
            for target in NEW_STRUCTURE:
                target_path = os.path.join(ROOT, target)
                if src.startswith(target_path):
                    break
            else:
                # Not in target structure, decide new location by file name
                dst = route_file(src, ROOT)
                safe_move(src, dst)

        # Try deleting folders after file moves
        if dirpath != os.path.join(ROOT, "tests"):
            delete_if_empty(dirpath)

def route_file(path, ROOT):
    """
    Determines the correct new destination folder for a file.
    Extendable with any mapping rules.
    """

    name = os.path.basename(path).lower()

    # E2E
    if "e2e" in name:
        return os.path.join(ROOT, "tests/e2e", os.path.basename(path))

    # Regression
    if "regression" in name:
        return os.path.join(ROOT, "tests/regression", os.path.basename(path))

    # L1 planners
    if "planner" in name:
        if "integration" in path.lower():
            return os.path.join(ROOT, "tests/l1/integration", os.path.basename(path))
        return os.path.join(ROOT, "tests/l1/unit", os.path.basename(path))

    # L2 executors
    if "executor" in name:
        if "integration" in path.lower():
            return os.path.join(ROOT, "tests/l2/integration", os.path.basename(path))
        return os.path.join(ROOT, "tests/l2/unit", os.path.basename(path))

    # L3 orchestration
    if "dag" in name or "self_correction" in name:
        return os.path.join(ROOT, "tests/l3/orchestration", os.path.basename(path))

    # L4 memory
    if "memory" in name or "provider" in name:
        return os.path.join(ROOT, "tests/l4/memory", os.path.basename(path))

    # L5 safety
    if "policy" in name or "filter" in name or "validator" in name or "injection" in name:
        return os.path.join(ROOT, "tests/l5/safety", os.path.basename(path))

    # Fallback → drop into integration folder
    return os.path.join(ROOT, "tests/integration", os.path.basename(path))

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    # Detect root from the current working directory
    cwd = os.getcwd()
    print(f"[ROOT] Starting in: {cwd}")

    # Ensure canonical directories exist
    for folder in NEW_STRUCTURE:
        ensure_dir(os.path.join(cwd, folder))

    # Begin merge
    merge_files_into_new_structure(cwd)

    print("\n[MIGRATION COMPLETE] All files moved and old folders deleted when empty.\n")

if __name__ == "__main__":
    main()
