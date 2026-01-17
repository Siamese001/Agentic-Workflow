#!/usr/bin/env python3
"""
Audit code quality metrics (typed %, documented %, schema strictness %) across all agents.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"

def main():
    """Audit code quality metrics."""
    print("=" * 70)
    print("CODE QUALITY METRICS AUDIT")
    print("=" * 70)
    
    # Load agent discovery
    with open(DISCOVERY_FILE, 'r', encoding='utf-8') as f:
        agents = json.load(f)
    
    total = len(agents)
    
    # Analyze typed %
    typed_100 = sum(1 for a in agents if a.get('typed_pct', 0) == 100.0)
    typed_below_100 = [a for a in agents if a.get('typed_pct', 0) < 100.0]
    avg_typed = sum(a.get('typed_pct', 0) for a in agents) / total if total > 0 else 0
    
    # Analyze documented %
    doc_100 = sum(1 for a in agents if a.get('documented_pct', 0) == 100.0)
    doc_below_100 = [a for a in agents if a.get('documented_pct', 0) < 100.0]
    avg_doc = sum(a.get('documented_pct', 0) for a in agents) / total if total > 0 else 0
    
    # Analyze schema strictness %
    schema_100 = sum(1 for a in agents if a.get('schema_strictness', 0) == 100.0)
    schema_below_100 = [a for a in agents if a.get('schema_strictness', 0) < 100.0]
    avg_schema = sum(a.get('schema_strictness', 0) for a in agents) / total if total > 0 else 0
    
    print(f"\nTotal agents: {total}")
    print("\n" + "=" * 70)
    print("TYPED % METRICS")
    print("=" * 70)
    print(f"  Agents at 100%: {typed_100}/{total} ({typed_100/total*100:.1f}%)")
    print(f"  Agents below 100%: {len(typed_below_100)} ({len(typed_below_100)/total*100:.1f}%)")
    print(f"  Average: {avg_typed:.1f}%")
    
    print("\n" + "=" * 70)
    print("DOCUMENTED % METRICS")
    print("=" * 70)
    print(f"  Agents at 100%: {doc_100}/{total} ({doc_100/total*100:.1f}%)")
    print(f"  Agents below 100%: {len(doc_below_100)} ({len(doc_below_100)/total*100:.1f}%)")
    print(f"  Average: {avg_doc:.1f}%")
    
    print("\n" + "=" * 70)
    print("SCHEMA STRICTNESS % METRICS")
    print("=" * 70)
    print(f"  Agents at 100%: {schema_100}/{total} ({schema_100/total*100:.1f}%)")
    print(f"  Agents below 100%: {len(schema_below_100)} ({len(schema_below_100)/total*100:.1f}%)")
    print(f"  Average: {avg_schema:.1f}%")
    
    # Find agents below 100% in ANY metric
    all_below_100 = set()
    for a in agents:
        if (a.get('typed_pct', 0) < 100.0 or 
            a.get('documented_pct', 0) < 100.0 or 
            a.get('schema_strictness', 0) < 100.0):
            all_below_100.add(a['class_name'])
    
    print("\n" + "=" * 70)
    print(f"AGENTS NEEDING IMPROVEMENT: {len(all_below_100)}")
    print("=" * 70)
    
    # Show top 20 agents needing most work
    agents_with_issues = []
    for a in agents:
        typed = a.get('typed_pct', 0)
        doc = a.get('documented_pct', 0)
        schema = a.get('schema_strictness', 0)
        
        if typed < 100.0 or doc < 100.0 or schema < 100.0:
            total_deficit = (100 - typed) + (100 - doc) + (100 - schema)
            agents_with_issues.append({
                'name': a['class_name'],
                'path': a['path'],
                'typed': typed,
                'doc': doc,
                'schema': schema,
                'deficit': total_deficit
            })
    
    agents_with_issues.sort(key=lambda x: x['deficit'], reverse=True)
    
    print(f"\nTop 20 agents needing most improvement:")
    print("-" * 70)
    for i, agent in enumerate(agents_with_issues[:20], 1):
        print(f"\n{i}. {agent['name']}")
        print(f"   Path: {agent['path']}")
        print(f"   Typed: {agent['typed']:.1f}% | Documented: {agent['doc']:.1f}% | Schema: {agent['schema']:.1f}%")
        print(f"   Total deficit: {agent['deficit']:.1f} points")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if len(all_below_100) == 0:
        print("\n✅ ALL AGENTS AT 100% FOR ALL METRICS!")
    else:
        print(f"\n⚠️  {len(all_below_100)} agents need improvement")
        print(f"\nTo achieve 100%:")
        print(f"  - {len(typed_below_100)} agents need type hints")
        print(f"  - {len(doc_below_100)} agents need documentation")
        print(f"  - {len(schema_below_100)} agents need schema strictness")

if __name__ == "__main__":
    main()
