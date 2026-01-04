#!/usr/bin/env python3
"""
Check for base class violations - agents should inherit from their layer base.
"""
import json
from pathlib import Path

# Load agent discovery
agents = json.loads(Path('agent_discovery_full.json').read_text(encoding='utf-8'))

# Canonical layer bases
LAYER_BASES = {
    'L0': 'L0Agent',
    'L1': 'L1Agent', 
    'L2': 'L2Agent',
    'L3': 'L3Agent',
    'L4': 'L4Agent',
    'L5': 'L5Agent',
}

# Map directory patterns to layers
LAYER_PATTERNS = {
    'L0_maintenance': 'L0',
    'L1_cognition': 'L1',
    'L2_execution': 'L2',
    'L3_orchestration': 'L3',
    'L4_state': 'L4',
    'L5_safety': 'L5',
}

violations = []
compliant = []

for agent in agents:
    path = agent.get('path', '')
    class_name = agent.get('class_name', '')
    bases = agent.get('bases', [])
    
    # Determine expected layer from path
    expected_layer = None
    for pattern, layer in LAYER_PATTERNS.items():
        if pattern in path:
            expected_layer = layer
            break
    
    if not expected_layer:
        continue  # Not in a layer directory
    
    expected_base = LAYER_BASES[expected_layer]
    
    # Check if agent inherits from expected base
    has_correct_base = expected_base in bases
    has_any_layer_base = any(b in LAYER_BASES.values() for b in bases)
    
    if has_correct_base:
        compliant.append({'class': class_name, 'path': path, 'layer': expected_layer})
    elif has_any_layer_base:
        # Wrong layer base
        actual_base = [b for b in bases if b in LAYER_BASES.values()][0]
        violations.append({
            'class': class_name, 
            'path': path, 
            'expected': expected_base,
            'actual': actual_base,
            'type': 'wrong_layer_base'
        })
    else:
        # Missing layer base entirely
        violations.append({
            'class': class_name,
            'path': path,
            'expected': expected_base,
            'bases': bases[:3],  # Show first 3 bases
            'type': 'missing_layer_base'
        })

print(f'Compliant: {len(compliant)}')
print(f'Violations: {len(violations)}')
print()
if violations:
    print('Violations:')
    for v in violations[:20]:
        vclass = v["class"]
        vtype = v["type"]
        vexp = v["expected"]
        print(f'  {vclass} ({vtype}): expected {vexp}')
        if 'actual' in v:
            print(f'    actual: {v["actual"]}')
        elif 'bases' in v:
            print(f'    has: {v["bases"]}')
    if len(violations) > 20:
        print(f'  ... and {len(violations) - 20} more')
