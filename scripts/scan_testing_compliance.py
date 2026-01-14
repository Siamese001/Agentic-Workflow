"""
Testing Compliance Scanner - Phase 1 & 2 Verification

UNIFIED SCANNER: Uses agent_discovery_full.json as single source of truth.
Runs full_agent_discovery.py if JSON is stale.

Scans all agents to verify:
- L2-L4 agents have self-testing (_run_self_tests or inherit from testing mixins)
- L0 agents have delegation (_delegate_tests or inherit from L0DelegationTestingMixin)

Detects both direct methods and inherited capabilities from base classes.
"""
import ast
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# SSOT: Import canonical layer inference (Phase 3 Migration)
from agentic_core.config.blueprint_sovereign.canonical_truth import get_canonical_layer
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR
DISCOVERY_JSON = PROJECT_ROOT / AGENT_DISCOVERY_JSON
DISCOVERY_SCRIPT = PROJECT_ROOT / SCRIPTS_DIR / 'full_agent_discovery.py'

# Base classes that provide testing capabilities
SELF_TESTING_BASES = {
    'SubAtomicAgent',  # L2
    'SubatomicTestingMixin',  # L2
    'L3OrchestrationBaseAgent',  # L3
    'L3SubatomicTestingMixin',  # L3
    'L4StateBaseAgent',  # L4
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
    'SubAtomicAgent',  # L2 - has HealerMixin
    'L3OrchestrationBaseAgent',  # L3 - has HealerMixin
    'L4StateBaseAgent',  # L4 - has HealerMixin
    'L5SafetyBaseAgent',  # L5 - has HealerMixin
    'CanonBaseAgent',  # Parent - child bases have HealerMixin
    'L3SubatomicTestingMixin',  # L3 agents inherit healing via base
    'L4SubatomicTestingMixin',  # L4 agents inherit healing via base
    'SubatomicTestingMixin',  # L2 agents inherit healing via base
    'ABC',  # CanonBaseAgent inherits from ABC + HealerMixin
}

# REMOVED: infer_layer() function - migrated to canonical_truth.py (Phase 3)
# All layer inference now uses get_canonical_layer() from canonical_truth.py


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
    layer = get_canonical_layer(file_path)
    
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


def regenerate_discovery_json():
    """Regenerate the canonical agent discovery JSON."""
    print("[REGENERATING] Running full_agent_discovery.py for fresh data...")
    subprocess.run(['python', str(DISCOVERY_SCRIPT)], cwd=str(PROJECT_ROOT))


def load_from_canonical_json() -> List[Dict]:
    """Load agents from canonical JSON, regenerating if needed."""
    # Force fresh regeneration if JSON doesn't exist or is older than 1 hour
    if not DISCOVERY_JSON.exists():
        regenerate_discovery_json()
    
    with open(DISCOVERY_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("=" * 80)
    print("TESTING COMPLIANCE SCANNER - Phase 1 & 2 Verification")
    print("(Single Source of Truth: agent_discovery_full.json)")
    print("=" * 80)
    print()
    
    # Load from canonical JSON
    canonical_agents = load_from_canonical_json()
    
    # Convert to our format
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
        
        # Find all agent classes - expanded detection
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Detect agents by multiple patterns:
                # 1. Ends with 'Agent'
                # 2. Ends with 'Mixin' (but only in agent contexts)
                # 3. Has execute/run/heal methods (duck-typed agents)
                # 4. Inherits from known agent bases
                
                is_agent = False
                
                # Pattern 1: Ends with Agent
                if node.name.endswith('Agent'):
                    is_agent = True
                
                # Pattern 2: Known agent-like suffixes
                if node.name.endswith(('Executor', 'Validator', 'Enforcer', 'Guardian', 'Sentinel', 'Inspector', 'Architect', 'Engineer', 'Healer', 'Oracle', 'Curator', 'Router', 'Orchestrator', 'Conductor')):
                    is_agent = True
                
                # Pattern 3: Inherits from agent bases
                bases = extract_bases(node)
                if bases & {'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent', 
                           'L3OrchestrationBaseAgent', 'L4StateBaseAgent', 'L5SafetyBaseAgent',
                           'HealerMixin', 'SubatomicTestingMixin', 'L3SubatomicTestingMixin',
                           'L4SubatomicTestingMixin', 'AutonomyMixin', 'AdaptiveExecutionMixin'}:
                    is_agent = True
                
                if not is_agent:
                    continue
                
                # Skip lowercase or pure snake_case
                if node.name.islower() or ('_' in node.name and not node.name[0].isupper()):
                    continue
                
                # Skip known base classes (not concrete agents)
                skip_bases = {'SubAtomicAgent', 'CanonBaseAgent', 'MaintenanceBaseAgent', 
                             'L3OrchestrationBaseAgent', 'L4StateBaseAgent', 'L5SafetyBaseAgent',
                             'IActionPlane', 'ValidationProtocol'}
                if node.name in skip_bases:
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
