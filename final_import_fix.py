#!/usr/bin/env python3
"""
Final comprehensive import fix script.
Handles both internal path issues and creates stubs for missing dependencies.
"""

import re
from pathlib import Path

# Additional explicit mappings for remaining issues
ADDITIONAL_MAPPINGS = {
    # Runtime dependencies - create relative imports
    'from runtime.infra.': 'from runtime.infra.',
    'import runtime.infra': 'import runtime.infra',
    'from runtime.telemetry': 'from runtime.telemetry',
    'from runtime.meta.': 'from runtime.meta.',
    'import runtime.meta': 'import runtime.meta',
    'from runtime.eval.': 'from runtime.eval.',
    'import runtime.eval': 'import runtime.eval',
    'from agentic_core.l3_orchestration.': 'from agentic_core.l3_orchestration.',
    
    # Specific remaining engine path issues
    'from agentic_core.l1_planning.planners.lic_': 'from agentic_core.l1_planning.planners.lic_',
    'from agentic_core.l4_memory_state.temporal.': 'from agentic_core.l4_memory_state.temporal.',
    'from agentic_core.l5_safety.safety_validator.': 'from agentic_core.l5_safety.safety_validator.',
}

def create_dependency_stubs():
    """Create stub files for missing dependencies to allow imports to work."""
    stubs_created = []
    
    # Create runtime module structure if missing
    runtime_dirs = ['runtime/infra', 'runtime/telemetry', 'runtime/meta', 'runtime/eval']
    for dir_path in runtime_dirs:
        full_path = Path(dir_path)
        full_path.mkdir(parents=True, exist_ok=True)
        
        init_file = full_path / '__init__.py'
        if not init_file.exists():
            init_file.write_text('# Runtime module stub\n')
            stubs_created.append(str(init_file))
    
    return stubs_created

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply additional explicit mappings
        for old_import, new_import in ADDITIONAL_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Additional regex patterns for edge cases
        patterns = [
            # Handle remaining engine path variations
            (r'from engine\.l1_planning\.draft_planning\.lic_(\w+)', r'from agentic_core.l1_planning.planners.lic_\1'),
            (r'from engine\.l4_state\.temporal_agents\.(\w+)', r'from agentic_core.l4_memory_state.temporal.\1'),
            (r'from engine\.l5_safety\.safety_validator\.(\w+)', r'from agentic_core.l5_safety.safety_validator.\1'),
            
            # Runtime dependency fixes
            (r'from infra\.(\w+)', r'from runtime.infra.\1'),
            (r'from meta\.(\w+)', r'from runtime.meta.\1'),
            (r'from eval\.(\w+)', r'from runtime.eval.\1'),
            (r'from orchestration\.(\w+)', r'from agentic_core.l3_orchestration.\1'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all Python files and create dependency stubs."""
    repo_root = Path('.')
    files_processed = 0
    files_updated = 0
    
    print("Creating dependency stubs...")
    stubs_created = create_dependency_stubs()
    for stub in stubs_created:
        print(f"Created stub: {stub}")
    
    print("\nStarting final import fix...")
    
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
    print(f"Stubs created: {len(stubs_created)}")

if __name__ == "__main__":
    main()
