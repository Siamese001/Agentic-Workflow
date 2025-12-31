#!/usr/bin/env python3
"""Rename all snake_case Agent files to PascalCase."""
from pathlib import Path
import re

def snake_to_pascal(snake_str):
    """Convert snake_case to PascalCase."""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

# Files to rename (old_path, new_name)
renames = [
    ('agentic_core/L5_safety/guardrails/dependency_pruning_agent.py', 'DependencyPruningAgent.py'),
    ('agentic_core/L5_safety/guardrails/duplicate_code_detector_agent.py', 'DuplicateCodeDetectorAgent.py'),
    ('agentic_core/L5_safety/guardrails/git_hygiene_agent.py', 'GitHygieneAgent.py'),
    ('agentic_core/L5_safety/guardrails/gravity_enforcer_agent.py', 'GravityEnforcerAgent.py'),
    ('agentic_core/L5_safety/guardrails/policy_neural_auto_immune_agent.py', 'PolicyNeuralAutoImmuneAgent.py'),
    ('agentic_core/L5_safety/guardrails/test_coverage_guardian_agent.py', 'TestCoverageGuardianAgent.py'),
    ('agentic_core/L5_safety/guardrails/unused_cleanup_agent.py', 'UnusedCleanupAgent.py'),
    ('agentic_core/L5_safety/validators/governance_agent.py', 'GovernanceAgent.py'),
    ('agentic_core/observability/metrics/hierarchy_enforcer_agent.py', 'HierarchyEnforcerAgent.py'),
    ('agentic_core/utils/core_extensions/dead_code_detector_agent.py', 'DeadCodeDetectorAgent.py'),
    ('agentic_core/utils/core_extensions/drift_detection_drift_detector_agent.py', 'DriftDetectionDriftDetectorAgent.py'),
    ('agentic_core/utils/core_extensions/drift_detector_agent.py', 'DriftDetectorAgent.py'),
    ('agentic_core/utils/core_extensions/global_compliance_aggregator_agent.py', 'GlobalComplianceAggregatorAgent.py'),
    ('agentic_core/utils/core_extensions/naming_law_healer_agent.py', 'NamingLawHealerAgent.py'),
]

renamed = []
for old_path_str, new_name in renames:
    old_path = Path(old_path_str)
    if not old_path.exists():
        print(f"SKIP: {old_path} (not found)")
        continue
    
    new_path = old_path.parent / new_name
    
    # Handle case-insensitive filesystems (Windows)
    if new_path.exists() and new_path.samefile(old_path):
        # Same file, need temp rename
        temp_path = old_path.parent / f"{new_name}.temp"
        old_path.rename(temp_path)
        temp_path.rename(new_path)
        print(f"RENAMED (via temp): {old_path} -> {new_path}")
    else:
        old_path.rename(new_path)
        print(f"RENAMED: {old_path} -> {new_path}")
    
    renamed.append((old_path_str, new_path))

print(f"\n✓ Renamed {len(renamed)} files")

# Generate import update mappings
print("\n=== Import Update Mappings ===")
for old_path_str, new_path in renamed:
    old_module = old_path_str.replace('/', '.').replace('.py', '')
    new_module = str(new_path).replace('\\', '.').replace('/', '.').replace('.py', '')
    print(f"{old_module} -> {new_module}")
