#!/usr/bin/env python3
"""Update all imports for renamed Agent files."""
from pathlib import Path
import re

# Mapping of old module names to new module names
RENAMES = {
    # Already renamed by git mv
    'healer_agent': 'HealerAgent',
    'meta_learning_agent': 'MetaLearningAgent',
    'agent_registry_validator_agent': 'AgentRegistryValidatorAgent',
    'P1_core_semantic_territory_mapper_agent': 'P1CoreSemanticTerritoryMapperAgent',
    'P1_core_territory_healer_agent': 'P1CoreTerritoryHealerAgent',
    'semantic_territory_mapper_agent': 'SemanticTerritoryMapperAgent',
    'territory_healer_agent': 'TerritoryHealerAgent',
    'code_formatter_agent': 'CodeFormatterAgent',
    
    # Renamed by Python script
    'dependency_pruning_agent': 'DependencyPruningAgent',
    'duplicate_code_detector_agent': 'DuplicateCodeDetectorAgent',
    'git_hygiene_agent': 'GitHygieneAgent',
    'gravity_enforcer_agent': 'GravityEnforcerAgent',
    'policy_neural_auto_immune_agent': 'PolicyNeuralAutoImmuneAgent',
    'test_coverage_guardian_agent': 'TestCoverageGuardianAgent',
    'unused_cleanup_agent': 'UnusedCleanupAgent',
    'governance_agent': 'GovernanceAgent',
    'hierarchy_enforcer_agent': 'HierarchyEnforcerAgent',
    'dead_code_detector_agent': 'DeadCodeDetectorAgent',
    'drift_detection_drift_detector_agent': 'DriftDetectionDriftDetectorAgent',
    'drift_detector_agent': 'DriftDetectorAgent',
    'global_compliance_aggregator_agent': 'GlobalComplianceAggregatorAgent',
    'naming_law_healer_agent': 'NamingLawHealerAgent',
}

def update_imports_in_file(file_path: Path) -> int:
    """Update imports in a single file. Returns number of changes."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        original = content
        changes = 0
        
        for old_name, new_name in RENAMES.items():
            # Pattern 1: from ... import old_name
            pattern1 = rf'\bfrom\s+([a-zA-Z0-9_.]+)\s+import\s+{old_name}\b'
            if re.search(pattern1, content):
                content = re.sub(pattern1, rf'from \1 import {new_name}', content)
                changes += 1
            
            # Pattern 2: from ... import old_name as ...
            pattern2 = rf'\bfrom\s+([a-zA-Z0-9_.]+)\s+import\s+{old_name}\s+as\s+'
            if re.search(pattern2, content):
                content = re.sub(pattern2, rf'from \1 import {new_name} as ', content)
                changes += 1
            
            # Pattern 3: import path.to.old_name
            pattern3 = rf'\bimport\s+([a-zA-Z0-9_.]+\.){old_name}\b'
            if re.search(pattern3, content):
                content = re.sub(pattern3, lambda m: m.group(0).replace(old_name, new_name), content)
                changes += 1
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return changes
        
        return 0
    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return 0

# Find all Python files
project_root = Path('.')
python_files = list(project_root.rglob('*.py'))

# Exclude certain directories
excluded = {'.venv', '__pycache__', '.git', 'node_modules', '.pytest_cache'}
python_files = [
    f for f in python_files 
    if not any(ex in f.parts for ex in excluded)
]

print(f"Scanning {len(python_files)} Python files for import updates...")

total_changes = 0
files_updated = 0

for py_file in python_files:
    changes = update_imports_in_file(py_file)
    if changes > 0:
        total_changes += changes
        files_updated += 1
        print(f"  ✓ {py_file.relative_to(project_root)}: {changes} import(s) updated")

print(f"\n✓ Updated {total_changes} imports across {files_updated} files")
