#!/usr/bin/env python3
"""
Phase 3.3: Naming Standardization Audit
Identifies files ending in Agent.py that don't inherit from SovereignBaseAgent
"""
import ast
import json
from pathlib import Path


def load_discovery():
    """Load agent discovery data."""
    with open('agent_discovery_full.json') as f:
        return json.load(f)

def find_all_agent_files():
    """Find all Python files ending in Agent.py"""
    root = Path('.')
    # Phase 6.7: Use ssot_discovery instead of glob
    from agentic_core.utils.ssot_discovery import get_agent_files
    agent_files = get_agent_files(root)

    return agent_files

def check_inheritance(file_path: Path) -> dict:
    """Check if a file inherits from SovereignBaseAgent or any base agent."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class name ends with Agent
                if node.name.endswith('Agent'):
                    # Check bases
                    base_names = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            base_names.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            base_names.append(base.attr)

                    # Check if it inherits from any base agent
                    is_true_agent = any(
                        'BaseAgent' in b or 'Agent' in b
                        for b in base_names
                    )

                    return {
                        'class_name': node.name,
                        'bases': base_names,
                        'is_true_agent': is_true_agent,
                        'line': node.lineno
                    }

        return None
    except Exception as e:
        return {'error': str(e)}

def main():
    print("=" * 70)
    print("PHASE 3.3: NAMING STANDARDIZATION AUDIT")
    print("=" * 70)
    print()

    # Load discovery data
    agents = load_discovery()
    discovered_names = {a['class_name'] for a in agents}

    print(f"✓ Loaded {len(agents)} agents from discovery")

    # Find all Agent.py files
    agent_files = find_all_agent_files()
    print(f"✓ Found {len(agent_files)} files ending in Agent.py")
    print()

    # Categorize files
    true_agents = []
    utilities_misnamed = []
    not_in_discovery = []

    for file_path in agent_files:
        inheritance_info = check_inheritance(file_path)

        if not inheritance_info or 'error' in inheritance_info:
            continue

        class_name = inheritance_info['class_name']

        # Check if in discovery
        if class_name not in discovered_names:
            not_in_discovery.append({
                'file': str(file_path),
                'class': class_name,
                'bases': inheritance_info['bases']
            })
            continue

        # Check if it's a true agent
        if inheritance_info['is_true_agent']:
            true_agents.append(class_name)
        else:
            # This is a utility misnamed as Agent
            utilities_misnamed.append({
                'file': str(file_path),
                'class': class_name,
                'bases': inheritance_info['bases'],
                'line': inheritance_info['line']
            })

    # Report results
    print("📊 AUDIT RESULTS:")
    print(f"   True Agents: {len(true_agents)}")
    print(f"   Utilities Misnamed: {len(utilities_misnamed)}")
    print(f"   Not in Discovery: {len(not_in_discovery)}")
    print()

    if utilities_misnamed:
        print("⚠️  UTILITIES MISNAMED AS AGENTS:")
        for util in utilities_misnamed:
            print(f"   {util['class']}")
            print(f"      File: {util['file']}")
            print(f"      Bases: {util['bases']}")
            print()

    if not_in_discovery:
        print("⚠️  FILES NOT IN DISCOVERY:")
        for item in not_in_discovery:
            print(f"   {item['class']}")
            print(f"      File: {item['file']}")
            print(f"      Bases: {item['bases']}")
            print()

    # Check for mixin redundancy
    print("🔍 CHECKING FOR REDUNDANT MIXIN IMPORTS...")
    redundant_mixins = []

    for agent in agents:
        path = agent.get('path', '')
        if not path:
            continue

        try:
            file_path = Path(path)
            if not file_path.exists():
                continue

            content = file_path.read_text(encoding='utf-8')

            # Check for direct mixin imports that should come from base
            if 'from agentic_core.base.mixins' in content:
                # Check if agent has a proper base class
                bases = agent.get('bases', [])
                if any('BaseAgent' in b for b in bases):
                    redundant_mixins.append({
                        'agent': agent['class_name'],
                        'file': path,
                        'layer': agent.get('layer', 'Unknown')
                    })
        except Exception:
            continue

    if redundant_mixins:
        print(f"   Found {len(redundant_mixins)} agents with potentially redundant mixin imports")
        for item in redundant_mixins[:5]:
            print(f"      {item['agent']} ({item['layer']})")
        if len(redundant_mixins) > 5:
            print(f"      ... and {len(redundant_mixins) - 5} more")
    else:
        print("   ✓ No redundant mixin imports detected")

    print()
    print("=" * 70)

    # Summary
    issues_found = len(utilities_misnamed) + len(not_in_discovery)
    if issues_found == 0:
        print("✅ NAMING AUDIT PASSED: All files properly named")
        return 0
    else:
        print(f"⚠️  NAMING AUDIT: {issues_found} issues require attention")
        return issues_found

if __name__ == '__main__':
    import sys
    issues = main()
    sys.exit(0)  # Don't fail, just report
