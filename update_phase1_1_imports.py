#!/usr/bin/env python3
"""Update imports for Phase 1.1 renamed validators"""

from pathlib import Path

# Map of old names to new names
renames_map = {
    "analysis_ops": "analysis_ops_validator",
    "auditors_guard_ddd_alignment": "auditors_guard_ddd_alignment_validator",
    "BudgetExceededError": "budget_exceeded_error_validator",
    "cache_invalidation": "cache_invalidation_validator",
    "check_output_quality": "check_output_quality_validator",
    "DeterministicCleaner": "deterministic_cleaner_validator",
    "guard_observability_footprint": "guard_observability_footprint_validator",
    "HealValidatorAgent": "heal_validator_agent_validator",
    "MissionPreflight": "mission_preflight_validator",
    "NamingAgent": "naming_agent_validator",
    "ReadFileArgs": "read_file_args_validator",
    "register_all_validators": "register_all_validators_validator",
    "validate_generated_content": "validate_generated_content_validator",
    "validation_utils": "validation_utils_validator",
}


def update_imports_in_file(file_path: Path) -> bool:
    """Update imports in a single file. Returns True if changes were made."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        for old_name, new_name in renames_map.items():
            # Pattern 1: from agentic_core.L5_safety.validators.OldName import
            pattern1 = f"from agentic_core.L5_safety.validators.{old_name} import"
            replacement1 = f"from agentic_core.L5_safety.validators.{new_name} import"
            content = content.replace(pattern1, replacement1)

            # Pattern 2: import agentic_core.L5_safety.validators.OldName
            pattern2 = f"import agentic_core.L5_safety.validators.{old_name}"
            replacement2 = f"import agentic_core.L5_safety.validators.{new_name}"
            content = content.replace(pattern2, replacement2)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


# Find all Python files
root = Path(".")
python_files = list(root.rglob("*.py"))

updated_files = []
for py_file in python_files:
    # Skip our own scripts
    if "phase1" in py_file.name or "execute_" in py_file.name:
        continue

    if update_imports_in_file(py_file):
        updated_files.append(py_file)
        print(f"✓ Updated: {py_file}")

print(f"\n✓ Updated {len(updated_files)} files")
if updated_files:
    print("\nUpdated files:")
    for f in updated_files[:20]:  # Show first 20
        print(f"  - {f}")
    if len(updated_files) > 20:
        print(f"  ... and {len(updated_files) - 20} more")
