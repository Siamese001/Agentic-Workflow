#!/usr/bin/env python3
"""
Comprehensive import fix script for engine → agentic_core restructuring.
Updates all import paths to reflect the new Windsurf Rules.md compliant structure.
"""

import re
from pathlib import Path

# Mapping of old import paths to new paths after restructuring
IMPORT_MAPPINGS = {
    # Base engine → agentic_core rename
    'from agentic_core.': 'from agentic_core.',
    'import agentic_core.': 'import agentic_core.',
    'from agentic_core import': 'from agentic_core import',
    
    # L2 execution restructuring (draft_execution → engines/resume or engines/outreach)
    'from agentic_core.l2_execution.engines.resume.rg_': 'from agentic_core.l2_execution.engines.resume.rg_',
    'from agentic_core.l2_execution.engines.outreach.lic_': 'from agentic_core.l2_execution.engines.outreach.lic_',
    'import agentic_core.l2_execution.engines.resume.rg_': 'import agentic_core.l2_execution.engines.resume.rg_',
    'import agentic_core.l2_execution.engines.outreach.lic_': 'import agentic_core.l2_execution.engines.outreach.lic_',
    
    # L2 execution tools consolidation
    'from agentic_core.l2_execution.tools.': 'from agentic_core.l2_execution.tools.',
    'import agentic_core.l2_execution.tools.': 'import agentic_core.l2_execution.tools.',
    
    # Outreach specific files moved from draft_execution/outreach/
    'from agentic_core.l2_execution.engines.outreach.': 'from agentic_core.l2_execution.engines.outreach.',
    'import agentic_core.l2_execution.engines.outreach.': 'import agentic_core.l2_execution.engines.outreach.',
    
    # Remaining draft_execution files (catch-all for non-rg_/lic_ files)
    'from agentic_core.l2_execution.engines.outreach.': 'from agentic_core.l2_execution.engines.outreach.',
    'import agentic_core.l2_execution.engines.outreach.': 'import agentic_core.l2_execution.engines.outreach.',
    
    # L1 planning (draft_planning stays as-is for now)
    'from agentic_core.l1_planning.planners.': 'from agentic_core.l1_planning.planners.',
    
    # L3 orchestration (will need engines/ vs framework/ split later)
    'from agentic_core.l3_orchestration.engines.resume.': 'from agentic_core.l3_orchestration.engines.resume.',
    
    # L4 state (memory_state rename and internal restructuring)
    'from agentic_core.l4_memory_state.': 'from agentic_core.l4_memory_state.',
    'import agentic_core.l4_memory_state.': 'import agentic_core.l4_memory_state.',
    'from agentic_core.l4_memory_state.temporal.': 'from agentic_core.l4_memory_state.temporal.',
    'from agentic_core.l4_memory_state.providers.': 'from agentic_core.l4_memory_state.providers.',
    'from agentic_core.l4_memory_state.providers.': 'from agentic_core.l4_memory_state.providers.',
    'from agentic_core.l4_memory_state.providers.': 'from agentic_core.l4_memory_state.providers.',
    'import agentic_core.l4_memory_state.temporal.': 'import agentic_core.l4_memory_state.temporal.',
    'import agentic_core.l4_memory_state.providers.': 'import agentic_core.l4_memory_state.providers.',
    'import agentic_core.l4_memory_state.providers.': 'import agentic_core.l4_memory_state.providers.',
    'import agentic_core.l4_memory_state.providers.': 'import agentic_core.l4_memory_state.providers.',
}

def fix_imports_in_file(file_path):
    """Fix imports in a single file using the mapping."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_config_files():
    """Fix configuration files that reference engine paths."""
    config_files = ['pytest.ini', 'mypy.ini']
    
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace engine/ paths with agentic_core/ in config files
                content = re.sub(r'engine/', 'agentic_core/', content)
                content = re.sub(r'engine\.', 'agentic_core.', content)
                
                if content != original_content:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Fixed config: {config_file}")
                    
            except Exception as e:
                print(f"Error processing config {config_file}: {e}")

def main():
    """Process all Python files in the repository."""
    repo_root = Path('.')
    files_processed = 0
    files_updated = 0
    
    print("Starting comprehensive agentic_core import fix...")
    
    # Fix configuration files first
    fix_config_files()
    
    # Process all Python files
    for py_file in repo_root.rglob('*.py'):
        # Skip .venv and __pycache__
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        files_processed += 1
        if fix_imports_in_file(py_file):
            files_updated += 1
            print(f"Fixed: {py_file}")
    
    print(f"\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Files updated: {files_updated}")

if __name__ == "__main__":
    main()
