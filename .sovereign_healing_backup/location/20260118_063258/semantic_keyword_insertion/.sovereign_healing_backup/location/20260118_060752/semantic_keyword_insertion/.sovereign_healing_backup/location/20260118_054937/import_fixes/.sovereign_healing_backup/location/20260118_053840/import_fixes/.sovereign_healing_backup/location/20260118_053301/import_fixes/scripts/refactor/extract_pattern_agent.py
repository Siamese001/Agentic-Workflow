"""
Extract PatternEnforcerAgent from canon_agents_pattern.py.
Also removes SubAtomicAgent stub and adds proper import.
"""
import ast
from pathlib import Path
from typing import Tuple

SOURCE_FILE = Path("agentic_core/L1_cognition/thought_engine/canon_agents_pattern.py")
TARGET_DIR = Path("agentic_core/L1_cognition/thought_engine")

def extract_class_with_context(content: str, class_name: str) -> Tuple[str, int, int]:
    """Extract class source with preceding comments."""
    lines = content.split('\n')
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include comments before class
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith('#') or not prev_line:
                    start_line -= 1
                else:
                    break
            
            class_source = '\n'.join(lines[start_line:end_line])
            return class_source, start_line + 1, end_line
    
    raise ValueError(f"Class {class_name} not found")

def create_pattern_enforcer_file(class_source: str):
    """Create sovereign file for PatternEnforcerAgent."""
    target_file = TARGET_DIR / "PatternEnforcerAgent.py"
    
    content = f'''"""
PatternEnforcerAgent - Extracted from canon_agents_pattern.py
Enforces coding patterns and best practices across Python files.
"""
from __future__ import annotations
import ast
import logging
import re
from typing import Any, Dict, List, Optional, Protocol, Tuple
from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

Logger: Any = logging.getLogger(__name__)

{class_source}
'''
    
    print(f"Creating {target_file}")
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return target_file

def update_source_file(source_file: Path):
    """Remove PatternEnforcerAgent and SubAtomicAgent stub, add proper import."""
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find classes to remove
    classes_to_remove = ['PatternEnforcerAgent', 'SubAtomicAgent']
    ranges_to_remove = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in classes_to_remove:
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include comments before class
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith('#') or not prev_line:
                    start_line -= 1
                else:
                    break
            
            ranges_to_remove.append((start_line, end_line, node.name))
    
    # Sort in reverse to remove from bottom up
    ranges_to_remove.sort(reverse=True)
    
    # Backup original
    backup_file = source_file.with_suffix('.py.bak')
    print(f"  Creating backup: {backup_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        with open(backup_file, 'w', encoding='utf-8') as b:
            b.write(f.read())
    
    # Remove classes
    for start, end, name in ranges_to_remove:
        del lines[start:end]
        if name == 'PatternEnforcerAgent':
            lines.insert(start, f"# {name} extracted to {name}.py (Phase B Task 4)")
            lines.insert(start + 1, "")
    
    # Add import for SubAtomicAgent at the top after imports
    import_line = "from agentic_core.L3_orchestration.fission_logic.SubAtomicAgent import SubAtomicAgent"
    
    # Find where to insert (after other imports)
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('from apps_shared.base_agents'):
            insert_idx = i + 1
            break
    
    lines.insert(insert_idx, import_line)
    lines.insert(insert_idx + 1, "")
    
    # Write updated file
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    print("=" * 60)
    print("PATTERN AGENT EXTRACTION - PHASE B TASK 4")
    print("=" * 60)
    
    # Read source file
    print(f"\nReading {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract PatternEnforcerAgent
    print(f"\n📦 Extracting PatternEnforcerAgent...")
    try:
        class_source, start, end = extract_class_with_context(content, 'PatternEnforcerAgent')
        target_file = create_pattern_enforcer_file(class_source)
        print(f"  ✅ Created {target_file} (lines {start}-{end})")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False
    
    # Update source file
    print(f"\nUpdating {SOURCE_FILE}...")
    print(f"  - Removing PatternEnforcerAgent")
    print(f"  - Removing SubAtomicAgent stub")
    print(f"  - Adding SubAtomicAgent import")
    update_source_file(SOURCE_FILE)
    print(f"  ✅ Updated {SOURCE_FILE}")
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"\n✅ PatternEnforcerAgent.py created")
    print(f"✅ canon_agents_pattern.py updated with proper import")
    
    print(f"\n⚠️  Next steps:")
    print(f"  1. Rename _GenerativeGuard_Deprecated in CanonHealerAgent.py")
    print(f"  2. Update imports for PatternEnforcerAgent")
    print(f"  3. Run discovery to verify 281 agents")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
