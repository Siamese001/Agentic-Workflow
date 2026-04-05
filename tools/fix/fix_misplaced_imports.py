#!/usr/bin/env python3
"""
Fix misplaced imports from constants migration.

The migration tool incorrectly inserted imports inside class definitions.
This script moves them to the top of the file.
"""

import re
from pathlib import Path


def fix_file(filepath: Path, dry_run: bool = True) -> dict:
    """Fix misplaced imports in a file."""
    content = filepath.read_text(encoding='utf-8')
    original_content = content
    
    # Pattern to find imports inside class definitions (indented)
    # These are lines like:     from agentic_core.config.constants_config import ...
    indented_import_pattern = r'^(\s+)from agentic_core\.config\.core\.constants_config import .+$'
    
    lines = content.split('\n')
    imports_to_move = []
    other_lines = []
    
    for line in lines:
        match = re.match(indented_import_pattern, line)
        if match:
            # Extract the import without indentation
            import_line = line.strip()
            imports_to_move.append(import_line)
        else:
            other_lines.append(line)
    
    if not imports_to_move:
        return {'file': str(filepath), 'changed': False, 'imports_moved': 0}
    
    # Find where to insert imports (after other imports, before code)
    insert_idx = 0
    for i, line in enumerate(other_lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_idx = i + 1
    
    # Insert the imports
    for import_line in reversed(imports_to_move):
        other_lines.insert(insert_idx, import_line)
    
    content = '\n'.join(other_lines)
    
    result = {
        'file': str(filepath),
        'changed': content != original_content,
        'imports_moved': len(imports_to_move),
    }
    
    if not dry_run and result['changed']:
        filepath.write_text(content, encoding='utf-8')
    
    return result


def main():
    # Files that need fixing (from ADG error output)
    files_to_fix = [
        'agentic_core/config/core/agent_defaults_config.py',
        'agentic_core/config/core/base_entity_config.py',
        'agentic_core/config/core/colors_config.py',
        'agentic_core/config/core/complexity_metrics_config.py',
        'agentic_core/config/core/gateway_config.py',
        'agentic_core/config/core/legacy_artifacts_config.py',
        'agentic_core/config/core/rag_config.py',
        'agentic_core/config/core/reflection_config.py',
        'agentic_core/config/core/registry_config.py',
        'agentic_core/config/core/sovereign_config.py',
        'agentic_core/adg/client/mcp_client.py',
        'agentic_core/adg/runtime/cache_loader.py',
        'agentic_core/adg/runtime/query_engine.py',
        'agentic_core/cache/config_file_cache.py',
        'agentic_core/knowledge/document_loaders/csv_document_loader_config.py',
        'agentic_core/L0_routing/scripts/agent_analysis_config.py',
        'agentic_core/L2_execution/config/transform_config.py',
        'agentic_core/L2_execution/config/unified_workflow_config.py',
        'agentic_core/L2_execution/healers/architecture_governor_healer.py',
        'agentic_core/L2_execution/healers/healing_tier_config.py',
        'agentic_core/L4_state/workflow_engines/config_file_cache.py',
        'agentic_core/L5_safety/enforcement/test_rigor_enforcer.py',
        'agentic_core/mixins/mcp_operation_mixin.py',
        'agentic_core/runtime/config/anomaly_report_config.py',
        'agentic_core/runtime/config/feature_flags_config.py',
        'agentic_core/runtime/config/injection_type_config.py',
        'agentic_core/runtime/config/model_provider_config.py',
        'agentic_core/runtime/config/model_tier_config.py',
        'agentic_core/runtime/config/prompt_injection_loader_config.py',
        'agentic_core/runtime/config/shared_infrastructure_config.py',
        'agentic_core/runtime/config/signal_quality_config.py',
        'agentic_core/runtime/config/validation_severity_config.py',
    ]
    
    total_fixed = 0
    for file_path in files_to_fix:
        filepath = Path(file_path)
        if filepath.exists():
            result = fix_file(filepath, dry_run=False)
            if result['changed']:
                print(f"Fixed {result['imports_moved']} imports in {filepath}")
                total_fixed += 1
        else:
            print(f"File not found: {filepath}")
    
    print(f"\nFixed {total_fixed} files")


if __name__ == '__main__':
    main()
