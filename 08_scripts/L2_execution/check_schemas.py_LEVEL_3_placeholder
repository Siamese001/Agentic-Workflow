import shutil
from pathlib import Path

ROOT = Path().resolve()

# ============================================================
# TARGET STRUCTURE
# ============================================================

TARGET_DIR_MAP = {
    # L1 Planning
    "l1": "l1_planning",
    "l1/integration": "l1_planning/integration",
    "l1/unit": "l1_planning/unit",

    # L2 Execution
    "l2": "l2_execution",
    "l2/integration": "l2_execution/integration",
    "l2/unit": "l2_execution/unit",

    # L3 Orchestration
    "l3": "l3_orchestration",
    "l3/orchestration": "l3_orchestration/dag",

    # L4 Memory
    "l4": "l4_memory",
    "l4/memory": "l4_memory/providers",

    # L5 Safety
    "l5": "l5_safety",
    "l5/safety": "l5_safety/rules",
}

# ============================================================
# CREATE NEW STRUCTURE
# ============================================================

def ensure_directories():
    print("\n[STEP] Creating new target directory structure...\n")
    for src, target in TARGET_DIR_MAP.items():
        new_path = ROOT / "tests" / target
        if not new_path.exists():
            new_path.mkdir(parents=True, exist_ok=True)
            print(f"[CREATE] {new_path}")


# ============================================================
# MOVE FILES
# ============================================================

def move_file(src_path: Path, dst_path: Path):
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[MOVE] {src_path}  ->  {dst_path}")
    shutil.move(str(src_path), str(dst_path))


def migrate_files():
    print("\n[STEP] Migrating files to new structure...\n")

    for old_key, new_key in TARGET_DIR_MAP.items():
        old_folder = ROOT / "tests" / old_key
        new_folder = ROOT / "tests" / new_key

        if not old_folder.exists():
            continue

        for item in old_folder.iterdir():
            if item.name == "__pycache__":
                continue
            if item.is_dir():
                continue  # handled recursively by map
            if item.is_file():
                dst = new_folder / item.name
                move_file(item, dst)


# ============================================================
# CLEANUP OLD DIRECTORIES
# ============================================================

def delete_if_empty(path: Path):
    """Deletes folder if completely empty."""
    try:
        if path.exists() and path.is_dir() and len(list(path.iterdir())) == 0:
            print(f"[DELETE] Empty folder removed Ã¢â€ â€™ {path}")
            path.rmdir()
    except Exception as e:
        print(f"[WARN] Could not delete {path}: {e}")


def cleanup_old_folders():
    print("\n[STEP] Cleaning up old folders...\n")
    for old_key in sorted(TARGET_DIR_MAP.keys(), reverse=True):
        old_path = ROOT / "tests" / old_key
        delete_if_empty(old_path)

    # Delete top-level l1..l5 dirs if now empty
    for top in ["l1", "l2", "l3", "l4", "l5"]:
        delete_if_empty(ROOT / "tests" / top)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print(f"[INFO] Test migration starting at repo root:\n {ROOT}\n")

    ensure_directories()
    migrate_files()
    cleanup_old_folders()

    print("\n[SUCCESS] Migration complete. New test structure is ready.\n")

if __name__ == "__main__":
    main()
