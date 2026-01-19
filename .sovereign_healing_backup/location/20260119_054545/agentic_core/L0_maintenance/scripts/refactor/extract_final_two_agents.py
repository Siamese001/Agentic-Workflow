"""
Extract final 2 agents to reach 283.
Extracts HealerAgent and _LegacySafetyInspectorAgent.
"""
import ast
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

def extract_healer_agent():
    """Extract HealerAgent from CanonHealerAgent.py."""
    source_file = Path("agentic_core/L1_cognition/thought_engine/CanonHealerAgent.py")
    target_file = Path("agentic_core/L1_cognition/thought_engine/HealerAgent.py")
    
    print(f"\n📦 Extracting HealerAgent from {source_file.name}...")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find HealerAgent class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'HealerAgent':
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
            
            # Read imports from source
            imports = []
            for i, line in enumerate(lines[:50]):
                if line.strip().startswith(('from', 'import')) and 'future' not in line:
                    imports.append(line)
            
            # Create new file
            new_content = f'''"""
HealerAgent - Extracted from CanonHealerAgent.py
Primary self-healing agent for agentic repository maintenance.
"""
from __future__ import annotations
{chr(10).join(imports[:15])}

{class_source}
'''
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ Created {target_file}")
            
            # Backup and update source file
            backup_file = source_file.with_suffix('.py.bak3')
            with open(source_file, 'r', encoding='utf-8') as f:
                with open(backup_file, 'w', encoding='utf-8') as b:
                    b.write(f.read())
            
            # Remove class from source
            del lines[start_line:end_line]
            lines.insert(start_line, f"# HealerAgent extracted to HealerAgent.py (Phase B Task 5)")
            lines.insert(start_line + 1, "")
            
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"  ✅ Updated {source_file}")
            return True
    
    print(f"  ❌ HealerAgent not found")
    return False

def extract_legacy_safety_inspector():
    """Extract _LegacySafetyInspectorAgent from canon_agents_quality.py."""
    source_file = Path("agentic_core/L1_cognition/thought_engine/canon_agents_quality.py")
    target_file = Path("agentic_core/L1_cognition/thought_engine/_LegacySafetyInspectorAgent.py")
    
    print(f"\n📦 Extracting _LegacySafetyInspectorAgent from {source_file.name}...")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    tree = ast.parse(content)
    
    # Find _LegacySafetyInspectorAgent class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == '_LegacySafetyInspectorAgent':
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
_LegacySafetyInspectorAgent - Extracted from canon_agents_quality.py
Legacy safety inspection agent preserved for backward compatibility.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

try:
    from agentic_core.L1_cognition.thought_engine.canon_validators_ast import validate_print_statements, validate_debugger, validate_empty_except, validate_bare_except, validate_eval_exec
except ImportError:
    validate_print_statements = validate_debugger = validate_empty_except = validate_bare_except = validate_eval_exec = lambda *a, **k: (True, [])

{class_source}
'''
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ Created {target_file}")
            
            # Backup and update source file
            backup_file = source_file.with_suffix('.py.bak3')
            with open(source_file, 'r', encoding='utf-8') as f:
                with open(backup_file, 'w', encoding='utf-8') as b:
                    b.write(f.read())
            
            # Remove class from source
            del lines[start_line:end_line]
            lines.insert(start_line, f"# _LegacySafetyInspectorAgent extracted to _LegacySafetyInspectorAgent.py (Phase B Task 5)")
            lines.insert(start_line + 1, "")
            
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"  ✅ Updated {source_file}")
            return True
    
    print(f"  ❌ _LegacySafetyInspectorAgent not found")
    return False

def main():
    print("=" * 60)
    print("FINAL TWO AGENTS EXTRACTION - REACH 283")
    print("=" * 60)
    
    success = True
    
    # Extract HealerAgent
    if not extract_healer_agent():
        success = False
    
    # Extract _LegacySafetyInspectorAgent
    if not extract_legacy_safety_inspector():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print("\n✅ HealerAgent.py created")
        print("✅ _LegacySafetyInspectorAgent.py created")
        
        print(f"\n⚠️  Next step:")
        print(f"  Run discovery to verify 283 agents")
    else:
        print("EXTRACTION FAILED")
        print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
