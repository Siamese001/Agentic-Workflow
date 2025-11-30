import os

APPS_ROOT = "apps"

# -------------------------------------------------------------------
# BLUEPRINT: TARGET FOLDER + FILE STRUCTURE FOR apps/
# -------------------------------------------------------------------

BLUEPRINT = {
    "resume_app": {
        "workflows": [
            "app_resume_generation_workflow.py",
            "app_resume_research_workflow.py",
        ],
        "controllers": [
            "app_resume_controller.py",
            "app_resume_pipeline_router.py",
        ],
        "adapters": [
            "app_resume_engine_adapter.py",
            "app_resume_memory_adapter.py",
        ],
        "serializers": [
            "app_resume_output_serializer.py",
            "app_resume_metadata_serializer.py",
        ],
        "validators": [
            "app_resume_input_validator.py",
            "app_resume_schema_validator.py",
        ],
    },
    "outreach_app": {
        "workflows": [
            "app_outreach_generation_workflow.py",
            "app_outreach_research_workflow.py",
        ],
        "controllers": [
            "app_outreach_controller.py",
            "app_outreach_pipeline_router.py",
        ],
        "adapters": [
            "app_outreach_engine_adapter.py",
            "app_outreach_memory_adapter.py",
        ],
        "serializers": [
            "app_outreach_message_serializer.py",
            "app_outreach_metadata_serializer.py",
        ],
        "validators": [
            "app_outreach_input_validator.py",
            "app_outreach_schema_validator.py",
        ],
    },
    "shared_app": {
        "workflows": [
            "app_shared_preprocessing.py",
            "app_shared_postprocessing.py",
        ],
        "controllers": [
            "app_shared_controller.py",
        ],
        "adapters": [
            "app_shared_logging_adapter.py",
            "app_shared_config_adapter.py",
        ],
        "serializers": [
            "app_shared_error_serializer.py",
            "app_shared_response_serializer.py",
        ],
        "validators": [
            "app_shared_request_validator.py",
            "app_shared_format_validator.py",
        ],
    },
    "services": {
        "telemetry": [
            "app_telemetry_service.py",
        ],
        "cache": [
            "app_cache_service.py",
        ],
        "errors": [
            "app_error_service.py",
        ],
        "config_loader": [
            "app_config_loader_service.py",
        ],
        "rate_limiting": [
            "app_rate_limit_service.py",
        ],
        "security": [
            "app_security_service.py",
        ],
    },
    "api": {
        "resume": [
            "app_resume_api.py",
        ],
        "outreach": [
            "app_outreach_api.py",
        ],
        "admin": [
            "app_admin_api.py",
        ],
        "health": [
            "app_health_api.py",
        ],
        "middleware": [
            "app_api_middleware.py",
        ],
        "routers": [
            "app_api_router.py",
        ],
    },
    "cli": {
        # use "root" to mean files directly under apps/cli/
        "root": [
            "app_resume_cli.py",
            "app_outreach_cli.py",
            "app_admin_cli.py",
        ],
    },
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
        "reports": [],
        "dev_guides": [],
        "playbooks": [],
    },
}

# Legacy/obsolete folders to delete once everything is migrated
LEGACY_FOLDERS = [
    os.path.join(APPS_ROOT, "deployment"),
    os.path.join(APPS_ROOT, "evaluation"),
    os.path.join(APPS_ROOT, "outreach"),
    os.path.join(APPS_ROOT, "resume"),
    os.path.join(APPS_ROOT, "outreach_engine"),
    os.path.join(APPS_ROOT, "resume_engine"),
]


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        print(f"[DRY RUN CREATE] {path}")
    else:
        # comment out if you don't want noise
        print(f"[DRY RUN EXISTS] {path}")


def create_folder_structure() -> None:
    """
    Ensure the entire target folder structure for apps/ exists
    according to the BLUEPRINT above.
    """
    for top_level, subs in BLUEPRINT.items():
        base_path = os.path.join(APPS_ROOT, top_level)
        ensure_dir(base_path)

        for subfolder, files in subs.items():
            if subfolder == "root":
                continue
            sub_path = os.path.join(base_path, subfolder)
            ensure_dir(sub_path)


def delete_legacy_folders() -> None:
    """
    Delete old/legacy folders that no longer should exist under apps/.
    Only removes them if they are present.
    """
    print("\n=== DRY RUN: Deleting legacy folders (if they still exist) ===")
    for folder in LEGACY_FOLDERS:
        if os.path.exists(folder):
            print(f"[DRY RUN DELETE] {folder}")
            # List contents before deletion for verification
            try:
                contents = os.listdir(folder)
                print(f"  [CONTAINS] {', '.join(contents)}")
            except Exception as e:
                print(f"  [ERROR] Could not list contents: {e}")
        else:
            print(f"[DRY RUN SKIP]   {folder} (not found)")


def file_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isfile(path)


def write_skeleton_file(path: str, description: str) -> None:
    """
    Create a minimal but meaningful skeleton file, only if it does not exist.
    """
    if file_exists(path):
        print(f"[DRY RUN SKIP FILE EXISTS] {path}")
        return

    print(f"[DRY RUN CREATE FILE] {path} - {description}")
    # Don't actually create file in dry run


def create_placeholders_for_blueprint() -> None:
    """
    For every file defined in the BLUEPRINT, create skeletons where they do not exist.
    This ensures no folder is empty and all expected files exist as targets
    for future Windsurf hydration.
    """
    print("\n=== DRY RUN: Creating placeholder skeleton files for missing blueprint files ===")

    for top_level, subs in BLUEPRINT.items():
        base_path = os.path.join(APPS_ROOT, top_level)

        for subfolder, files in subs.items():
            if subfolder == "root":
                # files directly under the top-level folder
                sub_path = base_path
            else:
                sub_path = os.path.join(base_path, subfolder)

            ensure_dir(sub_path)

            for filename in files:
                file_path = os.path.join(sub_path, filename)
                description = f"{top_level}/{subfolder} – {filename}" if subfolder != "root" else f"{top_level} – {filename}"
                write_skeleton_file(file_path, description)


def gap_report() -> None:
    """
    Print a simple gap report: which blueprint folders are still empty
    (no .py or .md files), so you can see where implementation is needed.
    """
    print("\n=== DRY RUN: GAP REPORT (blueprint folders lacking any files) ===")
    for top_level, subs in BLUEPRINT.items():
        base_path = os.path.join(APPS_ROOT, top_level)

        for subfolder in subs.keys():
            folder_path = base_path if subfolder == "root" else os.path.join(base_path, subfolder)
            if not os.path.exists(folder_path):
                print(f"[DRY RUN MISSING FOLDER] {folder_path}")
                continue

            entries = [
                f for f in os.listdir(folder_path)
                if f.endswith(".py") or f.endswith(".md") or f.endswith(".json")
            ]
            if not entries:
                print(f"[DRY RUN EMPTY] {folder_path}")

    print("=== DRY RUN END GAP REPORT ===\n")


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== DRY RUN STEP 1: Ensure target apps/ folder structure exists ===")
    create_folder_structure()

    print("\n=== DRY RUN STEP 2: Delete legacy folders under apps/ ===")
    delete_legacy_folders()

    print("\n=== DRY RUN STEP 3: Create placeholder skeleton files for empty blueprint slots ===")
    create_placeholders_for_blueprint()

    print("\n=== DRY RUN STEP 4: Run gap report (for visibility) ===")
    gap_report()

    print("=== DRY RUN: APPS MIGRATION + PLACEHOLDER SETUP COMPLETE ===\n")
