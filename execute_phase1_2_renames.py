#!/usr/bin/env python3
"""Execute Phase 1.2: Domain pilot validators across L0-L6 layers"""
import subprocess
import re
from pathlib import Path

# Domain pilot validators - 2-3 per layer
validators = [
    # L0_maintenance/deterministic
    "agentic_core\\L0_maintenance\\deterministic\\ATSValidationDeterministic.py",
    "agentic_core\\L0_maintenance\\deterministic\\CampaignBalanceDeterministic.py",
    "agentic_core\\L0_maintenance\\deterministic\\ContentQualityDeterministic.py",
    # L0_maintenance/scripts
    "agentic_core\\L0_maintenance\\scripts\\bootstrap_agent.py",
    "agentic_core\\L0_maintenance\\scripts\\budget_auditor.py",
    "agentic_core\\L0_maintenance\\scripts\\compliance_gate.py",
    # L1_cognition
    "agentic_core\\L1_cognition\\thought_engine\\TruthKeeper.py",
    # L2_execution
    "agentic_core\\L2_execution\\tool_registry\\ExecutorGuard.py",
    # L4_state
    "agentic_core\\L4_state\\validation_context\\SovereignFilesystemMcp.py",
    # config/blueprint_sovereign
    "agentic_core\\config\\blueprint_sovereign\\security_controls.py",
    # domain
    "agentic_core\\domain\\CoreIntegrityVerifier.py",
]

def to_snake_case(name):
    """Convert PascalCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_new_name(old_path):
    """Get the new validator name."""
    old_file = Path(old_path)
    old_name = old_file.stem
    
    snake_name = to_snake_case(old_name)
    
    if not snake_name.endswith('_validator'):
        new_name = f"{snake_name}_validator.py"
    else:
        new_name = f"{snake_name}.py"
    
    return str(old_file.parent / new_name)

renames = []
for old_path in validators:
    if Path(old_path).exists():
        new_path = get_new_name(old_path)
        renames.append((old_path, new_path))
        print(f"Will rename: {Path(old_path).name} -> {Path(new_path).name}")
    else:
        print(f"Skipping (not found): {old_path}")

print(f"\nTotal files to rename: {len(renames)}")

success_count = 0
failed = []

for old_path, new_path in renames:
    try:
        result = subprocess.run(
            ['git', 'mv', old_path, new_path],
            capture_output=True,
            text=True,
            check=True
        )
        success_count += 1
        old_name = Path(old_path).name
        new_name = Path(new_path).name
        print(f"✓ {success_count}/{len(renames)}: {old_name} -> {new_name}")
    except subprocess.CalledProcessError as e:
        failed.append((old_path, e.stderr))
        print(f"✗ Failed: {old_path}: {e.stderr}")

print(f"\n✓ Successfully renamed {success_count}/{len(renames)} files")
if failed:
    print(f"✗ Failed: {len(failed)} files")
