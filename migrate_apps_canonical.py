import os
import shutil

# ============================================================================================
# CONFIG — ROOT PATH
# ============================================================================================
REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"
APPS = os.path.join(REPO_ROOT, "apps")

# ============================================================================================
# TARGET FOLDER STRUCTURE (canonical L5 alignment)
# ============================================================================================
TARGET_DIRS = [
    # Resume Engine
    "resume_engine/api/v1/endpoints",
    "resume_engine/api/v1/middleware",
    "resume_engine/api/v1/schemas",
    "resume_engine/services/builders",
    "resume_engine/services/enrichers",
    "resume_engine/services/generators",
    "resume_engine/services/pipelines",
    "resume_engine/services/utils",
    "resume_engine/workers",
    "resume_engine/tests/unit",
    "resume_engine/tests/integration",
    "resume_engine/tests/e2e",
    "resume_engine/cli",

    # Outreach Engine
    "outreach_engine/api/v1/endpoints",
    "outreach_engine/api/v1/middleware",
    "outreach_engine/api/v1/schemas",
    "outreach_engine/services/planners",
    "outreach_engine/services/generators",
    "outreach_engine/services/enrichers",
    "outreach_engine/services/pipelines",
    "outreach_engine/services/utils",
    "outreach_engine/workers",
    "outreach_engine/tests/unit",
    "outreach_engine/tests/integration",
    "outreach_engine/tests/e2e",
    "outreach_engine/cli",

    # Shared
    "shared/adapters",
    "shared/utils",
    "shared/tests/unit",
    "shared/tests/integration",
    "shared/tests/e2e",
]

# ============================================================================================
# CREATE TARGET STRUCTURE
# ============================================================================================
def create_structure():
    for path in TARGET_DIRS:
        os.makedirs(os.path.join(APPS, path), exist_ok=True)
    print("✓ Target folder structure ensured")


# ============================================================================================
# SMART DESTINATION ROUTER — maps file → correct folder
# ============================================================================================
def resolve_destination(file_path):
    f = os.path.basename(file_path).lower()
    original = file_path.lower()

    # ---------------------------
    # Resume Engine routing
    # ---------------------------
    if "resume" in original:
        if "endpoint" in f or "api" in f:
            return "resume_engine/api/v1/endpoints"
        if "middleware" in f:
            return "resume_engine/api/v1/middleware"
        if "schema" in f:
            return "resume_engine/api/v1/schemas"
        if "builder" in f:
            return "resume_engine/services/builders"
        if "enrich" in f:
            return "resume_engine/services/enrichers"
        if "generate" in f or "generator" in f:
            return "resume_engine/services/generators"
        if "pipeline" in f:
            return "resume_engine/services/pipelines"
        if "worker" in f:
            return "resume_engine/workers"
        if "cli" in f:
            return "resume_engine/cli"
        return "resume_engine/services/utils"

    # ---------------------------
    # Outreach Engine routing
    # ---------------------------
    if "outreach" in original:
        if "endpoint" in f or "api" in f:
            return "outreach_engine/api/v1/endpoints"
        if "middleware" in f:
            return "outreach_engine/api/v1/middleware"
        if "schema" in f:
            return "outreach_engine/api/v1/schemas"
        if "planner" in f:
            return "outreach_engine/services/planners"
        if "generate" in f:
            return "outreach_engine/services/generators"
        if "enrich" in f:
            return "outreach_engine/services/enrichers"
        if "pipeline" in f:
            return "outreach_engine/services/pipelines"
        if "worker" in f:
            return "outreach_engine/workers"
        if "cli" in f:
            return "outreach_engine/cli"
        return "outreach_engine/services/utils"

    # ---------------------------
    # Shared routing
    # ---------------------------
    return "shared/utils"


# ============================================================================================
# MIGRATE FILES
# ============================================================================================
def migrate_files():
    for root, dirs, files in os.walk(APPS):
        for f in files:
            if f == "__init__.py":
                continue

            src = os.path.join(root, f)
            rel = os.path.relpath(src, APPS)

            # Ignore files already in the correct structure
            if any(rel.startswith(t) for t in TARGET_DIRS):
                continue

            dst_dir = resolve_destination(src)
            dst_full = os.path.join(APPS, dst_dir, f)

            os.makedirs(os.path.dirname(dst_full), exist_ok=True)
            shutil.move(src, dst_full)
            print(f"→ Moved {src} → {dst_full}")


# ============================================================================================
# CLEANUP OLD EMPTY FOLDERS
# ============================================================================================
def cleanup():
    for root, dirs, files in os.walk(APPS, topdown=False):
        if root == APPS:
            continue
        if not dirs and not files:
            try:
                os.rmdir(root)
                print(f"✗ Removed empty: {root}")
            except OSError:
                pass


# ============================================================================================
# RUN EVERYTHING
# ============================================================================================
if __name__ == "__main__":
    print("\n=== Building Canonical Apps Structure ===")
    create_structure()
    print("\n=== Migrating Files to New Structure ===")
    migrate_files()
    print("\n=== Cleaning Up Old Empty Folders ===")
    cleanup()
    print("\n✓ ALL DONE — apps folder aligned to canonical structure.")
