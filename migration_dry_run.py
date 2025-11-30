import os

# ============================================================
# TARGET BLUEPRINT FOR APPS/
# ============================================================

ROOT = "apps"

TARGET_TREE = {
    "resume_app": {
        "workflows": [
            "app_resume_generation_workflow.py",
            "app_resume_research_workflow.py"
        ],
        "controllers": [
            "app_resume_controller.py",
            "app_resume_pipeline_router.py"
        ],
        "adapters": [
            "app_resume_engine_adapter.py",
            "app_resume_memory_adapter.py"
        ],
        "serializers": [
            "app_resume_output_serializer.py",
            "app_resume_metadata_serializer.py"
        ],
        "validators": [
            "app_resume_input_validator.py",
            "app_resume_schema_validator.py"
        ]
    },

    "outreach_app": {
        "workflows": [
            "app_outreach_generation_workflow.py",
            "app_outreach_research_workflow.py"
        ],
        "controllers": [
            "app_outreach_controller.py",
            "app_outreach_pipeline_router.py"
        ],
        "adapters": [
            "app_outreach_engine_adapter.py",
            "app_outreach_memory_adapter.py"
        ],
        "serializers": [
            "app_outreach_message_serializer.py",
            "app_outreach_metadata_serializer.py"
        ],
        "validators": [
            "app_outreach_input_validator.py",
            "app_outreach_schema_validator.py"
        ]
    },

    "shared_app": {
        "workflows": [
            "app_shared_preprocessing.py",
            "app_shared_postprocessing.py"
        ],
        "controllers": ["app_shared_controller.py"],
        "adapters": [
            "app_shared_logging_adapter.py",
            "app_shared_config_adapter.py"
        ],
        "serializers": [
            "app_shared_error_serializer.py",
            "app_shared_response_serializer.py"
        ],
        "validators": [
            "app_shared_request_validator.py",
            "app_shared_format_validator.py"
        ],
    },

    "services": {
        "root": [
            "app_telemetry_service.py",
            "app_cache_service.py",
            "app_error_service.py",
            "app_config_service.py",
            "app_rate_limit_service.py"
        ]
    },

    "cli": {
        "root": [
            "app_resume_cli.py",
            "app_outreach_cli.py",
            "app_admin_cli.py"
        ]
    },

    "api": {
        "root": [
            "app_resume_api.py",
            "app_outreach_api.py",
            "app_health_api.py",
            "app_admin_api.py"
        ]
    }
}


# ============================================================
# DIRECTORY HELPERS
# ============================================================

def ensure(path):
    if not os.path.exists(path):
        os.makedirs(path)


def build_new_structure():
    """Create blueprint tree under apps/."""
    for app_name, subs in TARGET_TREE.items():
        app_root = os.path.join(ROOT, app_name)
        ensure(app_root)

        for subfolder in subs.keys():
            if subfolder == "root":
                continue
            ensure(os.path.join(app_root, subfolder))


def collect_existing_files():
    """Collect all .py files under apps/ that are not already in new structure."""
    files = []
    for root, dirs, fs in os.walk(ROOT):
        for f in fs:
            if not f.endswith(".py"):
                continue
            full = os.path.join(root, f)

            print(f"[DEBUG] Processing: {full}")  # Debug line

            # Skip config/, docs/ (should not move)
            if "\\config\\" in full.lower() or "\\docs\\" in full.lower():
                print(f"[DEBUG] Skipping config/docs: {full}")
                continue

            # Skip __init__.py files to preserve module structure
            if f == "__init__.py":
                print(f"[DEBUG] Skipping __init__.py: {full}")
                continue

            # Skip new structure paths to avoid re-moving - use more robust path matching
            full_normalized = os.path.normpath(full)
            skip_new_structure = False
            for app in TARGET_TREE.keys():
                app_path = os.path.normpath(os.path.join(ROOT, app))
                if full_normalized.startswith(app_path):
                    print(f"[DEBUG] Skipping new structure: {full}")
                    skip_new_structure = True
                    break

            if skip_new_structure:
                continue

            print(f"[DEBUG] Adding to migration list: {full}")
            files.append(full)
    return files


# ============================================================
# INFERENCE RULES (OLD → NEW MAPPING)
# ============================================================

def infer_target_path(filepath, filename):
    low = filepath.lower()

    # outreach_engine → outreach_app
    if "outreach_engine" in low or "outreach" in low:
        app = "outreach_app"
    # resume_engine → resume_app
    elif "resume_engine" in low or "resume" in low:
        app = "resume_app"
    # deployment → api or controllers depending on filename
    elif "deployment" in low:
        if "api" in filename.lower():
            app, sub = "api", "root"
            return app, os.path.join(ROOT, app, filename)
        elif "auth" in filename.lower():
            app, sub = "shared_app", "validators"
            return app, os.path.join(ROOT, app, sub, filename)
        else:
            app = "shared_app"
    # evaluation → shared_app
    elif "evaluation" in low:
        app = "shared_app"
    else:
        # default: shared app bucket
        app = "shared_app"

    # infer subsystem by keyword
    if any(k in filename.lower() for k in ["workflow", "pipeline"]):
        sub = "workflows"
    elif "controller" in filename.lower():
        sub = "controllers"
    elif "adapter" in filename.lower():
        sub = "adapters"
    elif "serializer" in filename.lower():
        sub = "serializers"
    elif "validator" in filename.lower():
        sub = "validators"
    else:
        # fallback: root-level for the specific app
        sub = "root"

    dest_dir = os.path.join(ROOT, app, sub) if sub != "root" else os.path.join(ROOT, app)
    return app, os.path.join(dest_dir, filename)


# ============================================================
# MIGRATION (DRY RUN)
# ============================================================

def migrate_file(path):
    filename = os.path.basename(path)

    app, dest_path = infer_target_path(path, filename)
    ensure(os.path.dirname(dest_path))

    print(f"[DRY RUN MOVE] {path} → {dest_path}")
    # shutil.move(path, dest_path)  # Commented out for dry run


def delete_old_folders():
    """Remove folders like apps/outreach_engine, apps/resume_engine, apps/outreach, apps/resume."""
    OLD = [
        "outreach_engine",
        "resume_engine",
        "outreach",
        "resume"
    ]
    for f in OLD:
        full = os.path.join(ROOT, f)
        if os.path.exists(full):
            print(f"[DRY RUN DELETE] {full}")
            # shutil.rmtree(full)  # Commented out for dry run


def gap_report():
    print("\n=== GAP REPORT ===\n")
    for app_name, subs in TARGET_TREE.items():
        print(f"[APP] {app_name}")
        for subfolder in subs.keys():
            if subfolder == "root":
                folder = os.path.join(ROOT, app_name)
            else:
                folder = os.path.join(ROOT, app_name, subfolder)

            if os.path.exists(folder):
                py_files = [f for f in os.listdir(folder) if f.endswith(".py")]
                if not py_files:
                    print(f"  [EMPTY] {folder}")
            else:
                print(f"  [NOT EXISTS] {folder}")
    print("\n=== END GAP REPORT ===\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n=== DRY RUN: Building target apps/ structure ===")
    build_new_structure()

    print("\n=== DRY RUN: Collecting existing files ===")
    to_move = collect_existing_files()
    print(f"Found {len(to_move)} files to migrate:\n")
    for f in to_move:
        print(f"  - {f}")
    print()

    print("=== DRY RUN: Migrating files ===")
    for f in to_move:
        migrate_file(f)

    print("\n=== DRY RUN: Deleting old folders ===")
    delete_old_folders()

    print("\n=== GAP REPORT ===")
    gap_report()

    print("\n=== DRY RUN COMPLETE ===\n")
