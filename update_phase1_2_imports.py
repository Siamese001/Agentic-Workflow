#!/usr/bin/env python3
"""Update imports for Phase 1.2 renamed validators"""
from pathlib import Path

renames_map = {
    "ATSValidationDeterministic": "ats_validation_deterministic_validator",
    "CampaignBalanceDeterministic": "campaign_balance_deterministic_validator",
    "ContentQualityDeterministic": "content_quality_deterministic_validator",
    "bootstrap_agent": "bootstrap_agent_validator",
    "budget_auditor": "budget_auditor_validator",
    "compliance_gate": "compliance_gate_validator",
    "TruthKeeper": "truth_keeper_validator",
    "SovereignFilesystemMcp": "sovereign_filesystem_mcp_validator",
    "security_controls": "security_controls_validator",
    "CoreIntegrityVerifier": "core_integrity_verifier_validator",
}

def update_imports_in_file(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        for old_name, new_name in renames_map.items():
            content = content.replace(
                f"from agentic_core.L0_maintenance.deterministic.{old_name} import",
                f"from agentic_core.L0_maintenance.deterministic.{new_name} import"
            )
            content = content.replace(
                f"from agentic_core.L0_maintenance.scripts.{old_name} import",
                f"from agentic_core.L0_maintenance.scripts.{new_name} import"
            )
            content = content.replace(
                f"from agentic_core.L1_cognition.thought_engine.{old_name} import",
                f"from agentic_core.L1_cognition.thought_engine.{new_name} import"
            )
            content = content.replace(
                f"from agentic_core.L4_state.validation_context.{old_name} import",
                f"from agentic_core.L4_state.validation_context.{new_name} import"
            )
            content = content.replace(
                f"from agentic_core.config.blueprint_sovereign.{old_name} import",
                f"from agentic_core.config.blueprint_sovereign.{new_name} import"
            )
            content = content.replace(
                f"from agentic_core.domain.{old_name} import",
                f"from agentic_core.domain.{new_name} import"
            )
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error: {file_path}: {e}")
        return False

root = Path('.')
updated = []
for py_file in root.rglob('*.py'):
    if 'phase1' in py_file.name or 'update_' in py_file.name:
        continue
    if update_imports_in_file(py_file):
        updated.append(py_file)
        print(f"✓ Updated: {py_file}")

print(f"\n✓ Updated {len(updated)} files")
