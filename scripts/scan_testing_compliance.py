"""
Testing Compliance Scanner - Phase 1 & 2 Verification

Scans all agents to verify:
- L2-L4 agents have self-testing (_run_self_tests or inherit from testing mixins)
- L0 agents have delegation (_delegate_tests or inherit from L0DelegationTestingMixin)

Detects both direct methods and inherited capabilities from base classes.
"""
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / 'agentic_core'

# Base classes that provide testing capabilities
SELF_TESTING_BASES = {
    'SubAtomicAgent',  # L2
    'SubatomicTestingMixin',  # L2
    'OrchestrationBaseAgent',  # L3
    'L3SubatomicTestingMixin',  # L3
    'StateBaseAgent',  # L4
    'L4SubatomicTestingMixin',  # L4
    'CanonBaseAgent',  # Has testing
}

DELEGATION_BASES = {
    'MaintenanceBaseAgent',  # L0
    'L0DelegationTestingMixin',  # L0
    'L0DelegationMixin',  # L0
}

HEALING_BASES = {
    'HealerMixin',
    'SubAtomicAgent',  # Now has HealerMixin
    'OrchestrationBaseAgent',  # Now has HealerMixin
    'StateBaseAgent',  # Now has HealerMixin
}


def infer_layer(file_path: Path) -> str:
    """Infer canonical layer from file path."""
    path_str = str(file_path)
    if 'L0_maintenance' in path_str: return 'L0'
    if 'L1_cognition' in path_str: return 'L1'
    if 'L2_execution' in path_str: return 'L2'
    if 'L3_orchestration' in path_str: return 'L3'
    if 'L4_state' in path_str: return 'L4'
    if 'L5_safety' in path_str: return 'L5'
    return 'other'


def extract_bases(class_node: ast.ClassDef) -> Set[str]:
    """Extract base class names from class definition."""
    bases = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.add(base.id)
        elif isinstance(base, ast.Attribute):
            bases.add(base.attr)
    return bases


def has_method(class_node: ast.ClassDef, method_name: str) -> bool:
    """Check if class has a specific method."""
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if item.name == method_name:
                return True
    return False


def analyze_agent(class_node: ast.ClassDef, file_path: Path) -> Dict:
    """Analyze a single agent class for testing compliance."""
    bases = extract_bases(class_node)
    layer = infer_layer(file_path)
    
    # Check for self-testing
    has_self_test_method = has_method(class_node, '_run_self_tests')
    inherits_self_testing = bool(bases & SELF_TESTING_BASES)
    has_self_testing = has_self_test_method or inherits_self_testing
    
    # Check for delegation
    has_delegate_method = has_method(class_node, '_delegate_tests')
    inherits_delegation = bool(bases & DELEGATION_BASES)
    has_delegation = has_delegate_method or inherits_delegation
    
    # Check for healing
    has_heal_method = has_method(class_node, 'heal') or has_method(class_node, 'apply_fix')
    inherits_healing = bool(bases & HEALING_BASES)
    has_healing = has_heal_method or inherits_healing
    
    # Determine testing type
    testing_type = 'None'
    if has_self_testing:
        testing_type = 'Self'
    elif has_delegation:
        testing_type = 'Delegated'
    
    return {
        'name': class_node.name,
        'file': str(file_path.relative_to(PROJECT_ROOT)),
        'layer': layer,
        'bases': list(bases),
        'has_self_testing': has_self_testing,
        'has_delegation': has_delegation,
        'has_healing': has_healing,
        'testing_type': testing_type,
        'self_test_method': has_self_test_method,
        'delegate_method': has_delegate_method,
        'inherits_self_testing': inherits_self_testing,
        'inherits_delegation': inherits_delegation,
    }


def main():
    print("=" * 80)
    print("TESTING COMPLIANCE SCANNER - Phase 1 & 2 Verification")
    print("=" * 80)
    print()
    
    agents = []
    errors = []
    
    # Scan all Python files in agentic_core
    for py_file in AGENTIC_CORE.rglob('*.py'):
        if '__pycache__' in str(py_file) or '.sovereign_healing_backup' in str(py_file):
            continue
        
        try:
            source = py_file.read_text(encoding='utf-8', errors='replace')
            tree = ast.parse(source)
        except Exception as e:
            errors.append(f"Parse error in {py_file.name}: {e}")
            continue
        
        # Find all classes ending with 'Agent'
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Only include actual agents, not base classes or mixins
                if node.name.endswith('Agent'):
                    # Skip lowercase or snake_case
                    if node.name.islower() or ('_' in node.name and not node.name[0].isupper()):
                        continue
                    
                    # Skip base classes marked as NOT_AN_AGENT
                    if 'NOT_AN_AGENT' in py_file.read_text(encoding='utf-8', errors='replace'):
                        if node.name in ['SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent', 
                                        'OrchestrationBaseAgent', 'StateBaseAgent']:
                            continue
                    
                    agent_data = analyze_agent(node, py_file)
                    agents.append(agent_data)
    
    # Statistics by layer
    by_layer = defaultdict(list)
    for agent in agents:
        by_layer[agent['layer']].append(agent)
    
    # Compliance analysis
    l2_l4_agents = [a for a in agents if a['layer'] in ['L2', 'L3', 'L4']]
    l2_l4_non_compliant = [a for a in l2_l4_agents if not a['has_self_testing']]
    
    l0_agents = [a for a in agents if a['layer'] == 'L0']
    l0_non_compliant = [a for a in l0_agents if not a['has_delegation']]
    
    healing_agents = [a for a in agents if a['has_healing']]
    
    # Print summary
    print(f"Total agents scanned: {len(agents)}")
    print()
    print("Layer Distribution:")
    for layer in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'other']:
        count = len(by_layer[layer])
        if count > 0:
            print(f"  {layer}: {count} agents")
    print()
    
    print("=" * 80)
    print("PHASE 1: L2-L4 SELF-TESTING COMPLIANCE")
    print("=" * 80)
    print(f"Total L2-L4 agents: {len(l2_l4_agents)}")
    print(f"With self-testing: {len(l2_l4_agents) - len(l2_l4_non_compliant)}")
    print(f"Non-compliant: {len(l2_l4_non_compliant)}")
    print()
    
    if l2_l4_non_compliant:
        print("Non-Compliant L2-L4 Agents:")
        for agent in l2_l4_non_compliant[:20]:  # Show first 20
            print(f"  - {agent['name']} ({agent['layer']}) - {agent['file']}")
            print(f"    Bases: {', '.join(agent['bases']) if agent['bases'] else 'None'}")
        if len(l2_l4_non_compliant) > 20:
            print(f"  ... and {len(l2_l4_non_compliant) - 20} more")
    else:
        print("✅ ALL L2-L4 AGENTS COMPLIANT!")
    
    print()
    print("=" * 80)
    print("PHASE 2: L0 DELEGATION COMPLIANCE")
    print("=" * 80)
    print(f"Total L0 agents: {len(l0_agents)}")
    print(f"With delegation: {len(l0_agents) - len(l0_non_compliant)}")
    print(f"Non-compliant: {len(l0_non_compliant)}")
    print()
    
    if l0_non_compliant:
        print("Non-Compliant L0 Agents:")
        for agent in l0_non_compliant:
            print(f"  - {agent['name']} - {agent['file']}")
            print(f"    Bases: {', '.join(agent['bases']) if agent['bases'] else 'None'}")
    else:
        print("✅ ALL L0 AGENTS COMPLIANT!")
    
    print()
    print("=" * 80)
    print("PHASE 3: HEALING CAPABILITY")
    print("=" * 80)
    print(f"Total agents with healing: {len(healing_agents)}")
    print(f"Coverage: {100 * len(healing_agents) // len(agents)}%")
    print()
    
    # Save detailed report
    report = {
        'summary': {
            'total_agents': len(agents),
            'l2_l4_total': len(l2_l4_agents),
            'l2_l4_compliant': len(l2_l4_agents) - len(l2_l4_non_compliant),
            'l2_l4_non_compliant': len(l2_l4_non_compliant),
            'l0_total': len(l0_agents),
            'l0_compliant': len(l0_agents) - len(l0_non_compliant),
            'l0_non_compliant': len(l0_non_compliant),
            'healing_total': len(healing_agents),
            'healing_coverage_pct': 100 * len(healing_agents) // len(agents) if agents else 0,
        },
        'l2_l4_non_compliant': l2_l4_non_compliant,
        'l0_non_compliant': l0_non_compliant,
        'all_agents': agents,
    }
    
    report_path = PROJECT_ROOT / 'testing_compliance_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"Detailed report saved to: {report_path}")
    print()
    
    # Final verdict
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    if len(l2_l4_non_compliant) == 0 and len(l0_non_compliant) == 0:
        print("✅ ✅ ✅ EXACT 0 VIOLATIONS - PHASES 1 & 2 COMPLETE! ✅ ✅ ✅")
    else:
        print(f"❌ {len(l2_l4_non_compliant)} L2-L4 violations, {len(l0_non_compliant)} L0 violations")
        print("   Additional fixes needed.")
    print()
    
    if errors:
        print("Errors encountered:")
        for error in errors[:10]:
            print(f"  - {error}")


if __name__ == '__main__':
    main()
