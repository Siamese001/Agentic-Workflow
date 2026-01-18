"""
Final extraction for Phase B Task 5 - Reach 283 agents.
Extracts GenerativeGuardDeprecatedAgent and removes SubAtomicAgent stubs.
"""
import ast
from pathlib import Path
from typing import Tuple

def extract_generative_guard():
    """Extract GenerativeGuardDeprecatedAgent from CanonHealerAgent.py."""
    source_file = Path("agentic_core/L1_cognition/thought_engine/CanonHealerAgent.py")
    target_file = Path("agentic_core/L1_cognition/thought_engine/GenerativeGuardDeprecatedAgent.py")
    
    print(f"\n📦 Extracting GenerativeGuardDeprecatedAgent from {source_file.name}...")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find GenerativeGuardDeprecatedAgent class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'GenerativeGuardDeprecatedAgent':
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
            
            # Create new file
            new_content = f'''"""
GenerativeGuardDeprecatedAgent - Extracted from CanonHealerAgent.py
Deprecated guard logic preserved for backward compatibility.
"""
from __future__ import annotations
import logging
import os
from typing import Any, Dict, List
from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
from agentic_core.L3_orchestration.fission_logic.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

EXCLUDED_DIRS = {{'__pycache__', '.git', 'node_modules', 'venv', '.venv'}}

{class_source}
'''
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ Created {target_file}")
            
            # Backup and update source file
            backup_file = source_file.with_suffix('.py.bak')
            with open(source_file, 'r', encoding='utf-8') as f:
                with open(backup_file, 'w', encoding='utf-8') as b:
                    b.write(f.read())
            
            # Remove class from source
            del lines[start_line:end_line]
            lines.insert(start_line, f"# GenerativeGuardDeprecatedAgent extracted to GenerativeGuardDeprecatedAgent.py (Phase B Task 5)")
            lines.insert(start_line + 1, "")
            
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"  ✅ Updated {source_file}")
            return True
    
    print(f"  ❌ GenerativeGuardDeprecatedAgent not found")
    return False

def remove_subatomic_stubs():
    """Remove SubAtomicAgent stubs from canon_agents_quality.py."""
    source_file = Path("agentic_core/L1_cognition/thought_engine/canon_agents_quality.py")
    
    print(f"\n🧹 Removing SubAtomicAgent stubs from {source_file.name}...")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find all SubAtomicAgent classes
    ranges_to_remove = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'SubAtomicAgent':
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include comments before class
            while start_line > 0:
                prev_line = lines[start_line - 1].strip()
                if prev_line.startswith('#') or not prev_line:
                    start_line -= 1
                else:
                    break
            
            ranges_to_remove.append((start_line, end_line))
    
    if not ranges_to_remove:
        print(f"  ℹ️  No SubAtomicAgent stubs found")
        return True
    
    # Backup
    backup_file = source_file.with_suffix('.py.bak2')
    with open(source_file, 'r', encoding='utf-8') as f:
        with open(backup_file, 'w', encoding='utf-8') as b:
            b.write(f.read())
    
    # Remove in reverse order
    ranges_to_remove.sort(reverse=True)
    for start, end in ranges_to_remove:
        del lines[start:end]
    
    # Add import at appropriate location (after other imports)
    import_added = False
    for i, line in enumerate(lines):
        if line.strip().startswith('from agentic_core.utils.core_extensions.healer_mixin'):
            lines.insert(i + 1, "from agentic_core.L3_orchestration.fission_logic.SubAtomicAgent import SubAtomicAgent")
            lines.insert(i + 2, "")
            import_added = True
            break
    
    if not import_added:
        # Fallback: add after imports section
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith(('from', 'import', '#', '"""', "'''")):
                lines.insert(i, "from agentic_core.L3_orchestration.fission_logic.SubAtomicAgent import SubAtomicAgent")
                lines.insert(i + 1, "")
                break
    
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"  ✅ Removed {len(ranges_to_remove)} SubAtomicAgent stub(s)")
    print(f"  ✅ Added SubAtomicAgent import")
    return True

def main():
    print("=" * 60)
    print("FINAL 283 EXTRACTION - PHASE B TASK 5")
    print("=" * 60)
    
    success = True
    
    # Extract GenerativeGuardDeprecatedAgent
    if not extract_generative_guard():
        success = False
    
    # Remove SubAtomicAgent stubs
    if not remove_subatomic_stubs():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print("\n✅ GenerativeGuardDeprecatedAgent.py created")
        print("✅ SubAtomicAgent stubs removed")
        print("✅ SubAtomicAgent import added")
        
        print(f"\n⚠️  Next steps:")
        print(f"  1. Identify duplicate CanonBaseAgent files")
        print(f"  2. Delete redundant file and update imports")
        print(f"  3. Run discovery to verify 283 agents")
    else:
        print("EXTRACTION FAILED")
        print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
