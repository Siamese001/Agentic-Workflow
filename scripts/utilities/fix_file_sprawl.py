#!/usr/bin/env python3
"""
Fix file sprawl violations by moving orphan files into appropriate subdirectories.
import logging

LOGGER = logging.getLogger(__name__)

"""

import shutil
from pathlib import Path

# Define target directories for orphan files
TARGET_DIRECTORIES = {
    # observability/ files
    "observability/control_plane_routing_pipeline.py": "observability/pipeline/",
    "observability/golden_state_gating.py": "observability/golden_state/",
    "observability/golden_state_runner.py": "observability/golden_state/",
    "observability/golden_state_scorer.py": "observability/golden_state/",
    "observability/health_metrics.py": "observability/metrics/",
    "observability/observability.py": "observability/core/",
    "observability/repair_policies.py": "observability/policies/",
    "observability/runtime_observability_agentic_collectors.py": (
        "observability/runtime/collectors/"
    ),
    "observability/runtime_observability_agentic_spans.py": "observability/runtime/spans/",
    "observability/runtime_observability_collectors.py": "observability/runtime/collectors/",
    "observability/runtime_observability_spans.py": "observability/runtime/spans/",
    "observability/security_controls.py": "observability/security/",
    "observability/simulation.py": "observability/simulation/",
    # config/ files
    "config/config.py": "config/core/",
    "config/graph_store_neo4j.py": "config/database/",
    "config/l5_policy.py": "config/policy/",
    "config/l5___init__.py": "config/policy/",
    "config/prompts.json": "config/prompts/",
    "config/security_controls.py": "config/security/",
    "config/tests__deprecated_conftest.py": "config/tests/",
    # shared/ files
    "shared/config.py": "shared/core/",
    "shared/exceptions.py": "shared/core/",
    "shared/models.py": "shared/core/",
    "shared/placeholder_stub.py": "shared/stubs/",
    "shared/reasoning_config.py": "shared/reasoning/",
    "shared/reasoning_prompt.py": "shared/reasoning/",
    "shared/workflow_types.py": "shared/types/",
    # scripts/ files
    "scripts/check_canonical_structure.py": "scripts/validation/",
    "scripts/fix_kwargs_correct.py": "scripts/validation/",
    "scripts/fix_kwargs_hints.py": "scripts/validation/",
    "scripts/fix_kwargs_hints_v2.py": "scripts/validation/",
    "scripts/fix_kwargs_simple.py": "scripts/validation/",
    "scripts/comment_archive_imports.py": "scripts/validation/",
    "scripts/populate_hardened_code.py": "scripts/setup/",
    "scripts/zero_loss_merge_engine.py": "scripts/merge/",
}


def move_file_with_import_updates(source: Path, target_dir: Path) -> None:
    """Move a file to target directory and update its imports."""
    # Create target directory if needed
    target_dir.mkdir(parents=True, exist_ok=True)

    # Move the file
    target_file = target_dir / source.name
    # Moving file silently
    shutil.move(str(source), str(target_file))

    # Update imports in the moved file
    if target_file.suffix == ".py":
        update_imports_in_file(target_file)


def update_imports_in_file(file_path: Path) -> None:
    """# SQL removed: Update import statements in a Python file after moving."""
    try:
        CONTENT = file_path.read_text(encoding="utf-8")
        original_content = content

        # Update relative imports based on the file's new location
        file_path.relative_to(Path(".")).parts

        # This is a simplified update - in practice, you'd need more sophisticated logic
        # to handle all import scenarios

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            # Updated imports in file_path
    except Exception as e:
        # Warning: Could not update imports in file_path
        logger.info(f"Warning: Could not update imports in {file_path}: {e}")


def handle_invalid_layers() -> None:
    """Handle invalid layer directories in apps_lic."""
    invalid_layers = {
        "apps_lic/core": "apps_lic/L2_execution",
        "apps_lic/planning": "apps_lic/L1_cognition",
        "apps_lic/rag": "apps_lic/L2_execution",
    }

    for old_dir, new_dir in invalid_layers.items():
        old_path = Path(old_dir)
        new_path = Path(new_dir)

        if old_path.exists():
            # Renaming directory old_path -> new_path
            # Move the entire directory
            if new_path.exists():
                # Merge directories if target exists
                for item in old_path.iterdir():
                    shutil.move(str(item), str(new_path / item.name))
                old_path.rmdir()
            else:
                shutil.move(str(old_path), str(new_path))


def main() -> None:
    """Main function to fix file sprawl."""
    ROOT = Path(".")

    # Move individual files
    for source_path, target_dir_str in TARGET_DIRECTORIES.items():
        SOURCE = root / source_path
        target_dir = root / target_dir_str

        if source.exists():
            move_file_with_import_updates(source, target_dir)
        else:
            # File not found: source
            logger.info(f"File not found: {source}")

    # Handle invalid layer directories
    handle_invalid_layers()

    # File sprawl fix complete!
    # Note: You may need to manually update import statements in other files that reference these...


if __name__ == "__main__":
    main()
