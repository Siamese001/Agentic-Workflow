import os
import shutil

ROOT = "runtime"

# Exact root-level files found in your runtime folder.
ROOT_FILES = {
    "context_manager.py",
    "cost_tracking.json",
    "execution_budget_manager.py",
    "executor.py",
    "metrics.json",
    "metrics.py",
    "observability.py",
    "policy_engine.py",
    "runtime_utils.py",
    "telemetry.py",
    "tool_registry.py",
}

# Canonical OpenAI agentic runtime folder structure.
TARGET_DIRS = {
    "inference": [
        "executor.py",
        "execution_budget_manager.py",
        "context_manager.py",
        "runtime_utils.py",
    ],
    "orchestration": [
        "policy_engine.py",
        "tool_registry.py",
    ],
    "routing": [],
    "safety_runtime": [],
    "state": [],
    "cost": [
        "cost_tracking.json",
    ],
    "telemetry": [
        "telemetry.py",
        "metrics.py",
        "metrics.json",
    ],
    "mcp_middleware": [],
    "utils": [
        "observability.py",
    ],
}

# These folders MUST NOT be deleted, ever.
PRESERVE_DIRS = {
    "cache", ".pytest_cache", ".ruff_cache", ".venv", "tmp",
    "config", "core", "data", "environment", "eval", "infra",
    "logs", "meta", "ops", "router", "schemas", "tests"
}

def ensure_structure():
    print("\n=== Creating canonical runtime folders ===")
    for folder in TARGET_DIRS:
        path = os.path.join(ROOT, folder)
        os.makedirs(path, exist_ok=True)
        print(f"âœ” ensured: {path}")

def move_files():
    print("\n=== Moving root-level runtime files ===")
    for folder, files in TARGET_DIRS.items():
        dest = os.path.join(ROOT, folder)
        for fname in files:
            src = os.path.join(ROOT, fname)
            dst = os.path.join(dest, fname)
            if os.path.exists(src):
                print(f"â†’ {src}  â†’  {dst}")
                shutil.move(src, dst)

def cleanup_empty_dirs():
    print("\n=== Cleaning up old empty runtime folders ===")

    for entry in os.listdir(ROOT):
        path = os.path.join(ROOT, entry)

        # Skip files
        if os.path.isfile(path):
            continue

        # Skip preserved directories
        if entry in PRESERVE_DIRS or entry in TARGET_DIRS:
            continue

        # Delete ONLY if empty
        try:
            if not os.listdir(path):
                print(f"âœ– removing empty folder: {path}")
                os.rmdir(path)
        except Exception:
            pass

def main():
    print("### BEGIN RUNTIME MIGRATION ###")
    ensure_structure()
    move_files()
    cleanup_empty_dirs()
    print("\n### MIGRATION COMPLETE ###")

if __name__ == "__main__":
    main()
