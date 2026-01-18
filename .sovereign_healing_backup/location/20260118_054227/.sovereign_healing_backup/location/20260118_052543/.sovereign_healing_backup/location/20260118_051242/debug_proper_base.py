#!/usr/bin/env python3
"""Debug why proper_base_class detection is failing."""
import ast
import json
from pathlib import Path

# Read a sample agent file to test
sample_files = [
    'agentic_core/L1_cognition/budget/BudgetAgent.py',
    'agentic_core/L2_execution/context/ContextCuratorAgent.py',
    'agentic_core/L3_orchestration/workflow_engines/WorkflowEngineAgent.py',
    'agentic_core/L5_safety/guardrails/CompositeGuardrailAgent.py'
]

LAYER_BASE_MAP = {
    "L1": "L1CognitionBaseAgent",
    "L2": "L2ExecutionBaseAgent", 
    "L3": "L3OrchestrationBaseAgent",
    "L4": "L4StateBaseAgent",
    "L5": "L5SafetyBaseAgent",
}

def extract_bases(class_node):
    """Extract base class names from AST node."""
    bases = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.add(base.id)
        elif isinstance(base, ast.Attribute):
            bases.add(base.attr)
    return bases

print("=" * 80)
print("PROPER BASE CLASS DETECTION DEBUG")
print("=" * 80)

for file_path in sample_files:
    full_path = Path('C:/Git/Agentic-Workflow') / file_path
    if not full_path.exists():
        print(f"\n❌ {file_path}: FILE NOT FOUND")
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        tree = ast.parse(source, filename=str(full_path))
    except:
        print(f"\n❌ {file_path}: PARSE ERROR")
        continue
    
    # Find agent class
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith('Agent'):
            print(f"\n{node.name} ({file_path}):")
            
            # Determine layer
            if 'L1' in file_path:
                layer = 'L1'
            elif 'L2' in file_path:
                layer = 'L2'
            elif 'L3' in file_path:
                layer = 'L3'
            elif 'L4' in file_path:
                layer = 'L4'
            elif 'L5' in file_path:
                layer = 'L5'
            else:
                layer = 'Unknown'
            
            expected = LAYER_BASE_MAP.get(layer, None)
            bases = extract_bases(node)
            
            print(f"  Layer: {layer}")
            print(f"  Expected base: {expected}")
            print(f"  Actual bases: {bases}")
            print(f"  Has expected?: {expected in bases if expected else 'N/A'}")
            
            break

print("\n" + "=" * 80)
print("ISSUE IDENTIFIED:")
print("Most agents do NOT directly inherit from layer base classes!")
print("They inherit from mixins, specific bases, or SovereignBaseAgent instead.")
print("=" * 80)
