#!/usr/bin/env python3
"""
Bulk Healer Addition Script - Add HealerMixin to all unhealed core agents

Reads agent_discovery_full.json and adds HealerMixin to all agents
that have has_healing=False.
"""
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_PATH = PROJECT_ROOT / 'agent_discovery_full.json'

HEALER_IMPORT = "from agentic_core.utils.core_extensions.healer_mixin import HealerMixin"

# Skip these - they are base classes, enums, or data classes
SKIP_CLASSES = {
    'AgentCapability', 'AgentRegistry', 'AgentRole', 'AgentSpec',
    'AgenticWorkflowError', 'AgentIdentity', 'AgentStatus',
    'L0DelegationMixin', 'L0DelegationTestingMixin',
    'Protocol', 'ABC', 'Enum',
}

def load_discovery():
    """Load agent discovery data."""
    with open(DISCOVERY_PATH) as f:
        return json.load(f)

def get_unhealed_core_agents(data):
    """Get list of core agents that aren't healed."""
    core_layers = {'L0', 'L1', 'L2', 'L3', 'L4', 'L5'}
    return [
        a for a in data 
        if not a.get('has_healing')
        and a.get('layer') in core_layers
        and a.get('class_name') not in SKIP_CLASSES
    ]

def add_healer_mixin_to_file(file_path: Path, class_name: str) -> bool:
    """Add HealerMixin to a class in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Skip if already has HealerMixin
        if 'HealerMixin' in content and class_name in content:
            # Check if this specific class has it
            pattern = rf'class\s+{re.escape(class_name)}\s*\([^)]*HealerMixin[^)]*\)'
            if re.search(pattern, content):
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
                # Add (HealerMixin) before the colon
                new_content = content[:match2.start(2)] + '(HealerMixin)' + content[match2.start(2):]
                # Add import
                new_content = add_import(new_content)
                file_path.write_text(new_content, encoding='utf-8')
                return True
            return False
        
        # Check if already has HealerMixin in bases
        bases = match.group(2).strip()
        if 'HealerMixin' in bases:
            return False
        
        # Add HealerMixin to the inheritance list
        if bases:
            new_bases = f"HealerMixin, {bases}"
        else:
            new_bases = "HealerMixin"
        
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
    """Add HealerMixin import to content."""
    if HEALER_IMPORT in content:
        return content
    
    # Find the last import line
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i
    
    # Insert after last import
    lines.insert(last_import_idx + 1, HEALER_IMPORT)
    return '\n'.join(lines)

def main():
    print("=" * 60)
    print("BULK HEALER ADDITION - Adding HealerMixin to unhealed agents")
    print("=" * 60)
    
    data = load_discovery()
    agents = get_unhealed_core_agents(data)
    
    print(f"\nFound {len(agents)} unhealed core agents (excluding skipped)")
    print()
    
    healed = 0
    skipped = 0
    errors = 0
    
    for agent in agents:
        class_name = agent['class_name']
        rel_path = agent['path']
        layer = agent['layer']
        file_path = PROJECT_ROOT / rel_path
        
        if class_name in SKIP_CLASSES:
            skipped += 1
            continue
        
        if not file_path.exists():
            print(f"  [SKIP] {class_name}: File not found")
            skipped += 1
            continue
        
        if add_healer_mixin_to_file(file_path, class_name):
            print(f"  [OK] {layer} | {class_name}")
            healed += 1
        else:
            skipped += 1
    
    print()
    print("=" * 60)
    print(f"HEALED: {healed}")
    print(f"SKIPPED: {skipped}")
    print(f"ERRORS: {errors}")
    print("=" * 60)
    
    return healed

if __name__ == '__main__':
    main()
