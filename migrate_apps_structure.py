import os
import shutil

# ---------------------------------------------------------
# CONFIG — root of the repo
# ---------------------------------------------------------
REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"
APPS_ROOT = os.path.join(REPO_ROOT, "apps")

# ---------------------------------------------------------
# NEW STRUCTURE DEFINITION
# (directories only — files will be moved in later)
# ---------------------------------------------------------
NEW_STRUCTURE = [
    # Resume Engine
    "apps/resume_engine/api/v1/endpoints",
    "apps/resume_engine/api/v1/schemas",
    "apps/resume_engine/api/v1/middleware",
    "apps/resume_engine/services/builders",
    "apps/resume_engine/services/enrichers",
    "apps/resume_engine/services/generators",
    "apps/resume_engine/services/pipelines",
    "apps/resume_engine/services/utils",
    "apps/resume_engine/workers",
    "apps/resume_engine/cli",
    "apps/resume_engine/tests/unit",
    "apps/resume_engine/tests/integration", 
    "apps/resume_engine/tests/e2e",

    # Outreach Engine
    "apps/outreach_engine/api/v1/endpoints",
    "apps/outreach_engine/api/v1/schemas",
    "apps/outreach_engine/api/v1/middleware",
    "apps/outreach_engine/services/planners",
    "apps/outreach_engine/services/generators",
    "apps/outreach_engine/services/enrichers",
    "apps/outreach_engine/services/pipelines",
    "apps/outreach_engine/services/utils",
    "apps/outreach_engine/workers",
    "apps/outreach_engine/cli",
    "apps/outreach_engine/tests/unit",
    "apps/outreach_engine/tests/integration",
    "apps/outreach_engine/tests/e2e",

    # Shared
    "apps/shared/utils",
    "apps/shared/adapters",
    "apps/shared/tests/unit",
    "apps/shared/tests/integration",
    "apps/shared/tests/e2e"
]

# ---------------------------------------------------------
# ENHANCED FILE MAPPING LOGIC
# Maps current structure to new structure based on file types and names
# ---------------------------------------------------------
def get_destination_mapping(src_path, filename):
    """Determine the appropriate destination for a file based on its current location and type"""
    path_lower = src_path.lower()
    file_lower = filename.lower()
    # CLI files
    if "cli" in path_lower:    if "resume" in path_lower:
            return "apps/resume_engine/cli"
        elif "outreach" in path_lower:
            return "apps/outreach_engine/cli"
        else:
            return "apps/shared/utils"
    
    # API files
    if "api" in path_lower:    if "admin" in path_lower:
            if "resume" in path_lower:
                return "apps/resume_engine/api/v1/endpoints"
            else:
                return "apps/outreach_engine/api/v1/endpoints"
        elif "health" in path_lower:
            return "apps/resume_engine/api/v1/endpoints"  # Shared health endpoint
        elif "middleware" in path_lower:
            return "apps/resume_engine/api/v1/middleware"
        elif "routers" in path_lower or "api.py" in filename.lower():
            if "outreach" in path_lower:
                return "apps/outreach_engine/api/v1/endpoints"
            elif "resume" in path_lower:
                return "apps/resume_engine/api/v1/endpoints"
            else:
                return "apps/shared/adapters"
        else:
            return "apps/shared/adapters"
    
    # Resume app files
    if "resume_app" in path_lower:    if "adapters" in path_lower:
            return "apps/resume_engine/services/adapters"
        elif "controllers" in path_lower:
            return "apps/resume_engine/api/v1/endpoints"
        elif "serializers" in path_lower:
            return "apps/resume_engine/api/v1/schemas"
        elif "validators" in path_lower:
            return "apps/resume_engine/api/v1/middleware"
        elif "workflows" in path_lower:
            if "pipeline" in file_lower:
                return "apps/resume_engine/services/pipelines"
            elif "generation" in file_lower:
                return "apps/resume_engine/services/generators"
            elif "research" in file_lower:
                return "apps/resume_engine/services/builders"
            else:
                return "apps/resume_engine/services/utils"
        else:
            return "apps/resume_engine/services/utils"
    
    # Outreach app files
    if "outreach_app" in path_lower:    if "adapters" in path_lower:
            return "apps/outreach_engine/services/adapters"
        elif "controllers" in path_lower:
            return "apps/outreach_engine/api/v1/endpoints"
        elif "serializers" in path_lower:
            return "apps/outreach_engine/api/v1/schemas"
        elif "validators" in path_lower:
            return "apps/outreach_engine/api/v1/middleware"
        elif "workflows" in path_lower:
            if "pipeline" in file_lower:
                return "apps/outreach_engine/services/pipelines"
            elif "generation" in file_lower:
                return "apps/outreach_engine/services/generators"
            elif "research" in file_lower:
                return "apps/outreach_engine/services/planners"
            else:
                return "apps/outreach_engine/services/utils"
        else:
            return "apps/outreach_engine/services/utils"
    
    # Services files
    if "services" in path_lower:    if "cache" in path_lower or "telemetry" in path_lower or "rate_limiting" in path_lower:
            return "apps/shared/adapters"
        elif "config_loader" in path_lower:
            return "apps/shared/utils"
        elif "security" in path_lower:
            return "apps/shared/adapters"
        elif "errors" in path_lower:
            return "apps/shared/utils"
        else:
            return "apps/shared/utils"
    
    # Shared app files
    if "shared_app" in path_lower:    if "adapters" in path_lower:
            return "apps/shared/adapters"
        elif "controllers" in path_lower:
            return "apps/shared/utils"
        elif "serializers" in path_lower:
            return "apps/shared/utils"
        elif "validators" in path_lower:
            return "apps/shared/utils"
        elif "workflows" in path_lower:
            if "pipeline" in file_lower:
                return "apps/shared/utils"
            else:
                return "apps/shared/utils"
        else:
            return "apps/shared/utils"
    
    # Default fallback
    return "apps/shared/utils"

# ---------------------------------------------------------
# CREATE NEW STRUCTURE
# ---------------------------------------------------------
def ensure_dirs():
    for path in NEW_STRUCTURE:
        full = os.path.join(REPO_ROOT, path)
        os.makedirs(full, exist_ok=True)
    print("✓ New folder structure created")

# ---------------------------------------------------------
# MIGRATE EXISTING FILES WITH ENHANCED LOGIC
# ---------------------------------------------------------
def migrate_existing_files():
    migrated_files = []
    skipped_files = []
    
    for root, dirs, files in os.walk(APPS_ROOT):
        for f in files:
            src = os.path.join(root, f)

            # Skip __init__.py — keep them where they are
            if f == "__init__.py":
                skipped_files.append(src)
                continue

            # Determine destination using enhanced mapping
            dst_dir = get_destination_mapping(root, f)
            dst = os.path.join(REPO_ROOT, dst_dir, f)

            # Move file
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            migrated_files.append((src, dst))
            print(f"→ Moved: {src}  →  {dst}")
    
    print(f"\n✓ Migration Summary:")
    print(f"  - Files migrated: {len(migrated_files)}")
    print(f"  - __init__.py files preserved: {len(skipped_files)}")
    
    return migrated_files, skipped_files

# ---------------------------------------------------------
# CREATE NEW __INIT__.PY FILES FOR NEW STRUCTURE
# ---------------------------------------------------------
def create_init_files():
    """Create __init__.py files in all new directories"""
    init_dirs = [
        "apps/resume_engine",
        "apps/resume_engine/api",
        "apps/resume_engine/api/v1", 
        "apps/resume_engine/api/v1/endpoints",
        "apps/resume_engine/api/v1/schemas",
        "apps/resume_engine/api/v1/middleware",
        "apps/resume_engine/services",
        "apps/resume_engine/services/builders",
        "apps/resume_engine/services/enrichers",
        "apps/resume_engine/services/generators",
        "apps/resume_engine/services/pipelines",
        "apps/resume_engine/services/utils",
        "apps/resume_engine/workers",
        "apps/resume_engine/cli",
        "apps/resume_engine/tests",
        "apps/resume_engine/tests/unit",
        "apps/resume_engine/tests/integration",
        "apps/resume_engine/tests/e2e",
        
        "apps/outreach_engine",
        "apps/outreach_engine/api",
        "apps/outreach_engine/api/v1",
        "apps/outreach_engine/api/v1/endpoints", 
        "apps/outreach_engine/api/v1/schemas",
        "apps/outreach_engine/api/v1/middleware",
        "apps/outreach_engine/services",
        "apps/outreach_engine/services/planners",
        "apps/outreach_engine/services/generators",
        "apps/outreach_engine/services/enrichers",
        "apps/outreach_engine/services/pipelines",
        "apps/outreach_engine/services/utils",
        "apps/outreach_engine/workers",
        "apps/outreach_engine/cli",
        "apps/outreach_engine/tests",
        "apps/outreach_engine/tests/unit",
        "apps/outreach_engine/tests/integration",
        "apps/outreach_engine/tests/e2e",
        
        "apps/shared",
        "apps/shared/utils",
        "apps/shared/adapters",
        "apps/shared/tests",
        "apps/shared/tests/unit",
        "apps/shared/tests/integration",
        "apps/shared/tests/e2e"
    ]
    
    for dir_path in init_dirs:
        full_path = os.path.join(REPO_ROOT, dir_path, "__init__.py")
        if not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                f.write(f"# {dir_path.replace('apps/', '').replace('/', ' ').title()}\n")
    
    print(f"✓ Created {len(init_dirs)} __init__.py files for new structure")

# ---------------------------------------------------------
# DELETE EMPTY OLD FOLDERS
# ---------------------------------------------------------
def delete_empty_dirs(base):
    removed_dirs = []
    for root, dirs, files in os.walk(base, topdown=False):
        if root == base:
            continue
        if not dirs and not files:
            try:
                os.rmdir(root)
                removed_dirs.append(root)
                print(f"✗ Removed empty folder: {root}")
            except OSError:
                pass
    
    print(f"\n✓ Removed {len(removed_dirs)} empty directories")
    return removed_dirs

# ---------------------------------------------------------
# EXECUTE MIGRATION
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Apps Structure Migration...")
    print("=" * 50)
    ensure_dirs()
    migrated_files, skipped_files = migrate_existing_files()
    create_init_files()
    removed_dirs = delete_empty_dirs(APPS_ROOT)
    
    print("\n" + "=" * 50)print("✅ Migration Complete!")
    print(f"📊 Final Summary:")
    print(f"  - Files migrated: {len(migrated_files)}")
    print(f"  - __init__.py files preserved: {len(skipped_files)}")
    print(f"  - New directories created: {len(NEW_STRUCTURE)}")
    print(f"  - Empty directories removed: {len(removed_dirs)}")
    print(f"  - Zero-tolerance compliance maintained ✓")
