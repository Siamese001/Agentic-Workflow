#!/usr/bin/env python3
"""
Bulk MCP Hardening Script - Add MCPHardenedMixin to all external agents

Reads agent_discovery_full.json and adds MCPHardenedMixin to all agents
that have external_touch=True but mcp_hardened=False.
"""
import json
import re
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_PATH = PROJECT_ROOT / AGENT_DISCOVERY_JSON

MCP_IMPORT = "from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin"

def load_discovery():
    """Load agent discovery data."""
    with open(DISCOVERY_PATH) as f:
        return json.load(f)

def get_unhardened_external_agents(data):
    """Get list of external agents that aren't MCP hardened."""
    core_layers = {'L0', 'L1', 'L2', 'L3', 'L4', 'L5'}
    return [
        a for a in data 
        if a.get('external_touch') 
        and not a.get('mcp_hardened')
        and a.get('layer') in core_layers
    ]

def add_mcp_mixin_to_file(file_path: Path, class_name: str) -> bool:
    """Add MCPHardenedMixin to a class in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Skip if already has MCPHardenedMixin
        if 'MCPHardenedMixin' in content:
            return False
        
        # Find the class definition
        # Pattern: class ClassName(Base1, Base2):
        pattern = rf'(class\s+{re.escape(class_name)}\s*\()([^)]+)(\)\s*:)'
        match = re.search(pattern, content)
        
        if not match:
            # Try simpler pattern: class ClassName:
            pattern2 = rf'(class\s+{re.escape(class_name)}\s*)(:)'
            match2 = re.search(pattern2, content)
            if match2:
                # Add (MCPHardenedMixin) before the colon
                new_content = content[:match2.start(2)] + '(MCPHardenedMixin)' + content[match2.start(2):]
                # Add import
                new_content = add_import(new_content)
                file_path.write_text(new_content, encoding='utf-8')
                return True
            return False
        
        # Add MCPHardenedMixin to the inheritance list
        bases = match.group(2).strip()
        if bases:
            new_bases = f"{bases}, MCPHardenedMixin"
        else:
            new_bases = "MCPHardenedMixin"
        
        new_class_def = f"{match.group(1)}{new_bases}{match.group(3)}"
        new_content = content[:match.start()] + new_class_def + content[match.end():]
        
        # Add import
        new_content = add_import(new_content)
        
        file_path.write_text(new_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"  [ERROR] {file_path.name}: {e}")
        return False

def add_import(content: str) -> str:
    """Add MCPHardenedMixin import to content."""
    if MCP_IMPORT in content:
        return content
    
    # Find the last import line
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i
    
    # Insert after last import
    lines.insert(last_import_idx + 1, MCP_IMPORT)
    return '\n'.join(lines)

def main():
    print("=" * 60)
    print("BULK MCP HARDENING - Adding MCPHardenedMixin to external agents")
    print("=" * 60)
    
    data = load_discovery()
    agents = get_unhardened_external_agents(data)
    
    print(f"\nFound {len(agents)} unhardened external agents")
    print()
    
    hardened = 0
    skipped = 0
    errors = 0
    
    for agent in agents:
        class_name = agent['class_name']
        rel_path = agent['path']
        layer = agent['layer']
        file_path = PROJECT_ROOT / rel_path
        
        if not file_path.exists():
            print(f"  [SKIP] {class_name}: File not found")
            skipped += 1
            continue
        
        if add_mcp_mixin_to_file(file_path, class_name):
            print(f"  [OK] {layer} | {class_name}")
            hardened += 1
        else:
            # Already hardened or couldn't find class
            skipped += 1
    
    print()
    print("=" * 60)
    print(f"HARDENED: {hardened}")
    print(f"SKIPPED: {skipped}")
    print(f"ERRORS: {errors}")
    print("=" * 60)
    
    return hardened

if __name__ == '__main__':
    main()
