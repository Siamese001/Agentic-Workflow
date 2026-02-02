#!/usr/bin/env python3
"""Execute Phase 1.1 validator renames"""

import subprocess
import sys

renames = [
    (
        "agentic_core\\L5_safety\\validators\\analysis_ops.py",
        "agentic_core\\L5_safety\\validators\\analysis_ops_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\auditors_guard_ddd_alignment.py",
        "agentic_core\\L5_safety\\validators\\auditors_guard_ddd_alignment_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\BudgetExceededError.py",
        "agentic_core\\L5_safety\\validators\\budget_exceeded_error_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\cache_invalidation.py",
        "agentic_core\\L5_safety\\validators\\cache_invalidation_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\check_output_quality.py",
        "agentic_core\\L5_safety\\validators\\check_output_quality_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\DeterministicCleaner.py",
        "agentic_core\\L5_safety\\validators\\deterministic_cleaner_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\guard_observability_footprint.py",
        "agentic_core\\L5_safety\\validators\\guard_observability_footprint_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\HealValidatorAgent.py",
        "agentic_core\\L5_safety\\validators\\heal_validator_agent_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\MissionPreflight.py",
        "agentic_core\\L5_safety\\validators\\mission_preflight_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\NamingAgent.py",
        "agentic_core\\L5_safety\\validators\\naming_agent_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\ReadFileArgs.py",
        "agentic_core\\L5_safety\\validators\\read_file_args_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\register_all_validators.py",
        "agentic_core\\L5_safety\\validators\\register_all_validators_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\validate_generated_content.py",
        "agentic_core\\L5_safety\\validators\\validate_generated_content_validator.py",
    ),
    (
        "agentic_core\\L5_safety\\validators\\validation_utils.py",
        "agentic_core\\L5_safety\\validators\\validation_utils_validator.py",
    ),
]

# Note: First 2 already done, skip them
already_done = 2
success_count = already_done
failed = []

for old_path, new_path in renames[already_done:]:
    try:
        result = subprocess.run(
            ["git", "mv", old_path, new_path], capture_output=True, text=True, check=True
        )
        success_count += 1
        old_name = old_path.split("\\")[-1]
        new_name = new_path.split("\\")[-1]
        print(f"✓ {success_count}/{len(renames)}: {old_name} -> {new_name}")
    except subprocess.CalledProcessError as e:
        failed.append((old_path, e.stderr))
        print(f"✗ Failed: {old_path}: {e.stderr}")

print(f"\n✓ Successfully renamed {success_count}/{len(renames)} files")
if failed:
    print(f"✗ Failed: {len(failed)} files")
    for path, error in failed:
        print(f"  - {path}: {error}")
    sys.exit(1)
