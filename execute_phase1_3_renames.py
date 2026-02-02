#!/usr/bin/env python3
"""Execute Phase 1.3: Batch process remaining VALIDATOR files"""
import json
import subprocess
import re
from pathlib import Path

# Load compliance report
with open('ssot_compliance_report.json', 'r') as f:
    report = json.load(f)

# Already processed in Phase 1.1 and 1.2
processed = {
    "analysis_ops", "auditors_guard_ddd_alignment", "BudgetExceededError",
    "cache_invalidation", "check_output_quality", "DeterministicCleaner",
    "guard_observability_footprint", "HealValidatorAgent", "MissionPreflight",
    "NamingAgent", "ReadFileArgs", "register_all_validators",
    "validate_generated_content", "validation_utils",
    "ATSValidationDeterministic", "CampaignBalanceDeterministic",
    "ContentQualityDeterministic", "bootstrap_agent", "budget_auditor",
    "compliance_gate", "TruthKeeper", "SovereignFilesystemMcp",
    "security_controls", "CoreIntegrityVerifier"
}

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

validators_to_rename = []
for violation in report['violations']:
    if violation['classification'] != 'VALIDATOR':
        continue
    if violation['is_naming_compliant']:
        continue
    
    path = violation['path']
    stem = Path(path).stem
    
    if stem in processed:
        continue
    if stem.endswith('_validator'):
        continue
    
    # Skip archives
    if 'archives' in path.lower():
        continue
    
    validators_to_rename.append(path)

print(f"Found {len(validators_to_rename)} remaining VALIDATOR files to rename")

def get_new_path(old_path):
    old_file = Path(old_path)
    snake_name = to_snake_case(old_file.stem)
    if not snake_name.endswith('_validator'):
        new_name = f"{snake_name}_validator.py"
    else:
        new_name = f"{snake_name}.py"
    return str(old_file.parent / new_name)

renames = []
for old_path in validators_to_rename:
    if Path(old_path).exists():
        new_path = get_new_path(old_path)
        renames.append((old_path, new_path))

print(f"Files to rename: {len(renames)}")

success = 0
for old_path, new_path in renames:
    try:
        subprocess.run(['git', 'mv', old_path, new_path], 
                      capture_output=True, text=True, check=True)
        success += 1
        print(f"✓ {success}/{len(renames)}: {Path(old_path).name}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {old_path}: {e.stderr}")

print(f"\n✓ Renamed {success}/{len(renames)} files")
