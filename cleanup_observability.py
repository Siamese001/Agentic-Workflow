import os
import shutil

ROOT = "observability"

# Correct Level-5 folders
VALID_FOLDERS = {
    "alerts",
    "dashboards",
    "pipelines",
    "telemetry",
    "tracing"
}

# Where old files should go
MOVE_REMAINDERS = {
    "model_costs.json": ("telemetry", "cost_tracking.yaml"),
    "cost_metrics.json": ("telemetry", "metrics.yaml"),
    "token_usage.json": ("telemetry", "metrics.yaml"),
}

YAML_STUB = "# Placeholder YAML configuration file\n"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_stub(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(YAML_STUB)

def move_file_safely(src, dest_folder, target_yaml=None):
    ensure_dir(dest_folder)

    if target_yaml:
        dest = os.path.join(dest_folder, target_yaml)
        print(f"[STUB] Creating stub for YAML target: {dest}")
        create_stub(dest)
    else:
        dest = os.path.join(dest_folder, os.path.basename(src))
        print(f"[MOVE] Moving {src} → {dest}")
        shutil.move(src, dest)

def cleanup_dir(path):
    if os.path.exists(path) and not os.listdir(path):
        print(f"[DELETE] Removing empty folder: {path}")
        os.rmdir(path)

def cleanup():
    print("\n=== OBSERVABILITY CLEANUP STARTED ===\n")

    ensure_dir(ROOT)

    # STEP 1 — Handle left-over folders: cost/ and metrics/
    leftovers = ["cost", "metrics"]
    for old_folder in leftovers:
        folder_path = os.path.join(ROOT, old_folder)
        if not os.path.exists(folder_path):
            continue

        print(f"[FOUND] Legacy folder: {folder_path}")

        for file in os.listdir(folder_path):
            src = os.path.join(folder_path, file)

            # If file is mapped → move properly
            if file in MOVE_REMAINDERS:
                new_folder, yaml_target = MOVE_REMAINDERS[file]
                dest_folder = os.path.join(ROOT, new_folder)
                move_file_safely(src, dest_folder, yaml_target)
            else:
                # Unknown: deposit safely into telemetry/
                dest_folder = os.path.join(ROOT, "telemetry")
                move_file_safely(src, dest_folder)

        # Delete if empty
        cleanup_dir(folder_path)

    # STEP 2 — Remove __pycache__ if present
    pycache = os.path.join(ROOT, "__pycache__")
    if os.path.isdir(pycache):
        print(f"[DELETE] Removing {pycache}")
        shutil.rmtree(pycache)

    # STEP 3 — Validate final structure
    print("\n=== VALIDATING FINAL STRUCTURE ===\n")

    current = set(os.listdir(ROOT))
    missing = VALID_FOLDERS - current
    extra = current - VALID_FOLDERS

    if missing:
        print(f"[ERROR] Missing required Level-5 folders: {missing}")
    else:
        print("[OK] All required Level-5 folders present.")

    if extra:
        print(f"[WARNING] Unexpected folders remain: {extra}")
    else:
        print("[OK] No invalid folders remain.")

    print("\n=== CLEANUP COMPLETE ===\n")


if __name__ == "__main__":
    cleanup()
