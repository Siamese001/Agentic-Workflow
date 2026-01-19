#!/usr/bin/env python3
"""
Phase 3.3: Comprehensive Inheritance Map Generator
Creates visual documentation of agent inheritance hierarchy
"""
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

def load_discovery():
    """Load agent discovery data."""
    with open('agent_discovery_full.json', 'r') as f:
        return json.load(f)

def build_inheritance_tree(agents: List[Dict]) -> Dict:
    """Build a hierarchical inheritance tree."""
    tree = {
        'SovereignBaseAgent': {
            'count': 0,
            'children': defaultdict(lambda: {'count': 0, 'agents': []})
        }
    }
    
    # Layer base agents
    layer_bases = {
        'L0MaintenanceBaseAgent': 'L0',
        'L1CognitionBaseAgent': 'L1',
        'L2ExecutionBaseAgent': 'L2',
        'L3OrchestrationBaseAgent': 'L3',
        'L4StateBaseAgent': 'L4',
        'L5SafetyBaseAgent': 'L5',
        'L6ObservabilityBaseAgent': 'L6'
    }
    
    # Categorize agents by their inheritance
    for agent in agents:
        class_name = agent.get('class_name', '')
        bases = agent.get('bases', [])
        layer = agent.get('layer', 'Unknown')
        
        # Check if it's a base agent
        if class_name in layer_bases:
            tree['SovereignBaseAgent']['count'] += 1
            tree['SovereignBaseAgent']['children'][class_name]['count'] += 1
            tree['SovereignBaseAgent']['children'][class_name]['agents'].append({
                'name': class_name,
                'layer': layer,
                'path': agent.get('path', '')
            })
        else:
            # Find which base it inherits from
            base_found = False
            for base in bases:
                if base in layer_bases:
                    tree['SovereignBaseAgent']['count'] += 1
                    tree['SovereignBaseAgent']['children'][base]['count'] += 1
                    tree['SovereignBaseAgent']['children'][base]['agents'].append({
                        'name': class_name,
                        'layer': layer,
                        'path': agent.get('path', ''),
                        'bases': bases
                    })
                    base_found = True
                    break
            
            if not base_found and 'SovereignBaseAgent' in bases:
                # Direct child of SovereignBaseAgent
                tree['SovereignBaseAgent']['count'] += 1
                tree['SovereignBaseAgent']['children']['Direct']['count'] += 1
                tree['SovereignBaseAgent']['children']['Direct']['agents'].append({
                    'name': class_name,
                    'layer': layer,
                    'path': agent.get('path', ''),
                    'bases': bases
                })
    
    return tree

def analyze_mixin_usage(agents: List[Dict]) -> Dict:
    """Analyze mixin usage patterns."""
    mixin_stats = defaultdict(lambda: {'count': 0, 'layers': set(), 'agents': []})
    
    common_mixins = [
        'HealerMixin',
        'MCPHardenedMixin',
        'SubatomicTestingMixin',
        'L2SelfTestingMixin',
        'L3SubatomicTestingMixin',
        'RedisCacheMixin',
        'PineconeVectorMixin'
    ]
    
    for agent in agents:
        bases = agent.get('bases', [])
        layer = agent.get('layer', 'Unknown')
        
        for mixin in common_mixins:
            if mixin in bases:
                mixin_stats[mixin]['count'] += 1
                mixin_stats[mixin]['layers'].add(layer)
                mixin_stats[mixin]['agents'].append(agent.get('class_name', ''))
    
    return mixin_stats

def generate_report(agents: List[Dict]):
    """Generate comprehensive inheritance report."""
    print("=" * 70)
    print("PHASE 3.3: COMPREHENSIVE INHERITANCE MAP")
    print("=" * 70)
    print()
    
    # Build inheritance tree
    tree = build_inheritance_tree(agents)
    
    print("📊 INHERITANCE HIERARCHY:")
    print()
    print(f"SovereignBaseAgent (Root)")
    print(f"├─ Total Descendants: {tree['SovereignBaseAgent']['count']}")
    print()
    
    for base_name, base_data in sorted(tree['SovereignBaseAgent']['children'].items()):
        if base_data['count'] > 0:
            print(f"├─ {base_name}")
            print(f"│  └─ Agents: {base_data['count']}")
            
            # Show layer distribution
            layer_dist = defaultdict(int)
            for agent in base_data['agents']:
                layer_dist[agent['layer']] += 1
            
            for layer, count in sorted(layer_dist.items()):
                print(f"│     └─ {layer}: {count} agents")
            print()
    
    # Analyze mixin usage
    print("🔧 MIXIN USAGE ANALYSIS:")
    print()
    mixin_stats = analyze_mixin_usage(agents)
    
    for mixin, stats in sorted(mixin_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"   {mixin}")
        print(f"      Used by: {stats['count']} agents")
        print(f"      Layers: {', '.join(sorted(stats['layers']))}")
        print()
    
    # Identify orphans (agents not inheriting from proper base)
    print("🔍 ARCHITECTURAL ANALYSIS:")
    print()
    
    proper_bases = {
        'SovereignBaseAgent',
        'L0MaintenanceBaseAgent',
        'L1CognitionBaseAgent', 
        'L2ExecutionBaseAgent',
        'L3OrchestrationBaseAgent',
        'L4StateBaseAgent',
        'L5SafetyBaseAgent',
        'L6ObservabilityBaseAgent'
    }
    
    orphans = []
    mixin_only = []
    
    for agent in agents:
        bases = agent.get('bases', [])
        has_proper_base = any(b in proper_bases for b in bases)
        has_mixin = any('Mixin' in b for b in bases)
        
        if not has_proper_base:
            if has_mixin:
                mixin_only.append({
                    'name': agent.get('class_name', ''),
                    'layer': agent.get('layer', ''),
                    'bases': bases
                })
            else:
                orphans.append({
                    'name': agent.get('class_name', ''),
                    'layer': agent.get('layer', ''),
                    'bases': bases
                })
    
    print(f"   ✓ Properly Inherited: {len(agents) - len(orphans) - len(mixin_only)} agents")
    print(f"   ⚠️  Mixin-Only (No Base): {len(mixin_only)} agents")
    print(f"   ❌ Orphans (No Inheritance): {len(orphans)} agents")
    print()
    
    if mixin_only:
        print("   MIXIN-ONLY AGENTS (Top 10):")
        for agent in mixin_only[:10]:
            print(f"      {agent['name']} ({agent['layer']})")
            print(f"         Bases: {', '.join(agent['bases'])}")
        if len(mixin_only) > 10:
            print(f"      ... and {len(mixin_only) - 10} more")
        print()
    
    # Layer compliance
    print("📋 LAYER COMPLIANCE:")
    print()
    layer_stats = defaultdict(lambda: {'total': 0, 'compliant': 0, 'mixin_only': 0})
    
    for agent in agents:
        layer = agent.get('layer', 'Unknown')
        bases = agent.get('bases', [])
        has_proper_base = any(b in proper_bases for b in bases)
        has_mixin = any('Mixin' in b for b in bases)
        
        layer_stats[layer]['total'] += 1
        if has_proper_base:
            layer_stats[layer]['compliant'] += 1
        elif has_mixin:
            layer_stats[layer]['mixin_only'] += 1
    
    for layer in sorted(layer_stats.keys()):
        stats = layer_stats[layer]
        compliance_pct = (stats['compliant'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"   {layer:20} {stats['compliant']:3}/{stats['total']:3} ({compliance_pct:5.1f}%) compliant")
        if stats['mixin_only'] > 0:
            print(f"                        {stats['mixin_only']:3} mixin-only")
    
    print()
    print("=" * 70)
    
    # Save detailed report
    report_data = {
        'total_agents': len(agents),
        'properly_inherited': len(agents) - len(orphans) - len(mixin_only),
        'mixin_only': len(mixin_only),
        'orphans': len(orphans),
        'mixin_only_agents': mixin_only,
        'orphan_agents': orphans,
        'layer_stats': dict(layer_stats),
        'mixin_usage': {k: {'count': v['count'], 'layers': list(v['layers'])} 
                        for k, v in mixin_stats.items()}
    }
    
    with open('PHASE3_3_INHERITANCE_MAP.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"✓ Detailed report saved to PHASE3_3_INHERITANCE_MAP.json")
    
    return len(mixin_only) + len(orphans)

def main():
    agents = load_discovery()
    issues = generate_report(agents)
    
    if issues == 0:
        print("\n✅ INHERITANCE MAP: All agents properly inherit from base classes")
        return 0
    else:
        print(f"\n⚠️  INHERITANCE MAP: {issues} agents need architectural review")
        return issues

if __name__ == '__main__':
    import sys
    issues = main()
    sys.exit(0)  # Don't fail, just report
