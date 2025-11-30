import os
import shutil

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

            # Skip config/, docs/ (should not move)
            if "\\config\\" in full.lower() or "\\docs\\" in full.lower():
                continue

            # Skip __init__.py files to preserve module structure
            if f == "__init__.py":
                continue

            # Skip new structure paths to avoid re-moving - use more robust path matching
            full_normalized = os.path.normpath(full)
            skip_new_structure = False
            for app in TARGET_TREE.keys():
                app_path = os.path.normpath(os.path.join(ROOT, app))
                if full_normalized.startswith(app_path):
                    skip_new_structure = True
                    break

            if skip_new_structure:
                continue

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
# MIGRATION
# ============================================================

def migrate_file(path):
    filename = os.path.basename(path)

    app, dest_path = infer_target_path(path, filename)
    ensure(os.path.dirname(dest_path))

    print(f"[MOVE] {path} → {dest_path}")
    shutil.move(path, dest_path)


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
            print(f"[DELETE] {full}")
            shutil.rmtree(full)


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
    print("\n=== Building target apps/ structure ===")
    build_new_structure()

    print("\n=== Collecting existing files ===")
    to_move = collect_existing_files()
    print(f"Found {len(to_move)} files to migrate.\n")

    print("=== Migrating files ===")
    for f in to_move:
        migrate_file(f)

    print("\n=== Deleting old folders ===")
    delete_old_folders()

    print("\n=== GAP REPORT ===")
    gap_report()

    print("\n=== MIGRATION COMPLETE ===\n")
