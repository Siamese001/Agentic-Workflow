"""
Extract final agent to reach 283 - SystemArchitectDeprecatedAgent.
Renames _SystemArchitect_Deprecated to SystemArchitectDeprecatedAgent.
"""
import ast
from pathlib import Path

def extract_system_architect_deprecated():
    """Extract and rename _SystemArchitect_Deprecated from CanonHealerAgent.py."""
    source_file = Path("agentic_core/L1_cognition/thought_engine/CanonHealerAgent.py")
    target_file = Path("agentic_core/L1_cognition/thought_engine/SystemArchitectDeprecatedAgent.py")
    
    print(f"\n📦 Extracting _SystemArchitect_Deprecated from {source_file.name}...")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find _SystemArchitect_Deprecated class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == '_SystemArchitect_Deprecated':
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
            
            # Rename class in source
            class_source = class_source.replace('class _SystemArchitect_Deprecated', 'class SystemArchitectDeprecatedAgent')
            
            # Create new file
            new_content = f'''"""
SystemArchitectDeprecatedAgent - Extracted from CanonHealerAgent.py
Legacy system architect logic preserved for backward compatibility.
Renamed from _SystemArchitect_Deprecated to comply with strict discovery rules.
"""
from __future__ import annotations
import ast
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

{class_source}
'''
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ Created {target_file}")
            print(f"  ✅ Renamed class to SystemArchitectDeprecatedAgent")
            
            # Backup and update source file
            backup_file = source_file.with_suffix('.py.bak4')
            with open(source_file, 'r', encoding='utf-8') as f:
                with open(backup_file, 'w', encoding='utf-8') as b:
                    b.write(f.read())
            
            # Remove class from source
            del lines[start_line:end_line]
            lines.insert(start_line, f"# SystemArchitectDeprecatedAgent extracted to SystemArchitectDeprecatedAgent.py (Phase B Task 5)")
            lines.insert(start_line + 1, "")
            
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"  ✅ Updated {source_file}")
            return True
    
    print(f"  ❌ _SystemArchitect_Deprecated not found")
    return False

def main():
    print("=" * 60)
    print("FINAL AGENT EXTRACTION - REACH 283")
    print("=" * 60)
    
    success = extract_system_architect_deprecated()
    
    print("\n" + "=" * 60)
    if success:
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print("\n✅ SystemArchitectDeprecatedAgent.py created")
        print("✅ Class renamed for strict compliance")
        
        print(f"\n⚠️  Next step:")
        print(f"  Run discovery to verify 283 agents")
    else:
        print("EXTRACTION FAILED")
        print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
