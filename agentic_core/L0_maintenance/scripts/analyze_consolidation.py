"""Agent Consolidation Analysis for L3 Orchestration and L2 Execution layers."""
import json
from pathlib import Path
from collections import defaultdict

from agentic_core.L5_safety.validators.structure_blueprint import (
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
from archives.location_violations.file_utils import safe_read_file, safe_write_file

def main():
    data = json.load(open(AGENT_DISCOVERY_JSON))
    
    l3_agents = [a for a in data if 'L3' in a.get('path', '')]
    l2_agents = [a for a in data if 'L2' in a.get('path', '')]
    
    print("=" * 80)
    print("AGENT CONSOLIDATION ANALYSIS REPORT")
    print("=" * 80)
    
    print(f"\n## Summary")
    print(f"- L3 Orchestration Agents: {len(l3_agents)}")
    print(f"- L2 Execution Agents: {len(l2_agents)}")
    print(f"- Total: {len(l3_agents) + len(l2_agents)}")
    
    # Analyze L3 agents
    print("\n" + "=" * 80)
    print("L3 ORCHESTRATION CORE ANALYSIS")
    print("=" * 80)
    
    # Group by functional category
    l3_categories = defaultdict(list)
    for a in l3_agents:
        name = a['class_name']
        if 'RL' in name or 'PPO' in name or 'QLearning' in name or 'ActorCritic' in name or 'Reinforce' in name:
            l3_categories['RL/Learning'].append(a)
        elif 'Territory' in name or 'Semantic' in name:
            l3_categories['Territory/Semantic'].append(a)
        elif 'DAG' in name or 'Dag' in name:
            l3_categories['DAG/Workflow'].append(a)
        elif 'MCP' in name or 'Mcp' in name:
            l3_categories['MCP/Tool'].append(a)
        elif 'Monitor' in name or 'Detector' in name:
            l3_categories['Monitoring'].append(a)
        elif 'Orchestrat' in name or 'Workflow' in name:
            l3_categories['Core Orchestration'].append(a)
        elif 'Fission' in name:
            l3_categories['Fission'].append(a)
        elif 'Permission' in name or 'Registry' in name or 'Governor' in name:
            l3_categories['Governance'].append(a)
        else:
            l3_categories['Other'].append(a)
    
    for category, agents in sorted(l3_categories.items(), key=lambda x: -len(x[1])):
        print(f"\n### {category} ({len(agents)} agents)")
        for a in agents:
            print(f"  - {a['class_name']}: LOC={a.get('loc', 0)}, CC={a.get('cyclomatic_complexity', 0)}")
    
    # Analyze L2 agents
    print("\n" + "=" * 80)
    print("L2 EXECUTION CORE ANALYSIS")
    print("=" * 80)
    
    l2_categories = defaultdict(list)
    for a in l2_agents:
        name = a['class_name']
        if 'Git' in name:
            l2_categories['Git/VCS'].append(a)
        elif 'Code' in name or 'Dedup' in name or 'Janitor' in name:
            l2_categories['Code Quality'].append(a)
        elif 'Memory' in name or 'Context' in name:
            l2_categories['Memory/Context'].append(a)
        elif 'Integrity' in name or 'Safety' in name or 'Security' in name:
            l2_categories['Safety/Security'].append(a)
        elif 'Sovereign' in name or 'MCP' in name or 'Mcp' in name:
            l2_categories['MCP/Sovereign'].append(a)
        elif 'Enforcer' in name or 'Sentinel' in name or 'Guardian' in name:
            l2_categories['Enforcement'].append(a)
        elif 'Architect' in name or 'Engineer' in name or 'Planner' in name:
            l2_categories['Architecture/Planning'].append(a)
        elif 'Dependency' in name or 'Fallback' in name or 'Resource' in name:
            l2_categories['Resource Management'].append(a)
        elif 'Inspector' in name or 'Auditor' in name or 'Detector' in name:
            l2_categories['Inspection/Audit'].append(a)
        elif 'Tool' in name or 'Healer' in name:
            l2_categories['Tooling'].append(a)
        else:
            l2_categories['Other'].append(a)
    
    for category, agents in sorted(l2_categories.items(), key=lambda x: -len(x[1])):
        print(f"\n### {category} ({len(agents)} agents)")
        for a in agents:
            print(f"  - {a['class_name']}: LOC={a.get('loc', 0)}, CC={a.get('cyclomatic_complexity', 0)}")
    
    # Identify duplicates
    print("\n" + "=" * 80)
    print("DUPLICATE/SIMILAR AGENTS DETECTED")
    print("=" * 80)
    
    all_agents = l3_agents + l2_agents
    name_counts = defaultdict(list)
    for a in all_agents:
        name_counts[a['class_name']].append(a['path'])
    
    print("\n### Exact Name Duplicates:")
    for name, paths in sorted(name_counts.items()):
        if len(paths) > 1:
            print(f"  - {name}: {len(paths)} instances")
            for p in paths:
                print(f"      {p}")
    
    # Similar names
    print("\n### Similar Name Patterns (potential consolidation):")
    similar_groups = [
        ('DAG', [a for a in all_agents if 'DAG' in a['class_name'] or 'Dag' in a['class_name']]),
        ('Territory', [a for a in all_agents if 'Territory' in a['class_name']]),
        ('Semantic', [a for a in all_agents if 'Semantic' in a['class_name']]),
        ('Fission', [a for a in all_agents if 'Fission' in a['class_name']]),
        ('Orchestrator', [a for a in all_agents if 'Orchestrator' in a['class_name'] or 'Orchestrat' in a['class_name']]),
        ('Monitor/Detector', [a for a in all_agents if 'Monitor' in a['class_name'] or 'Detector' in a['class_name']]),
        ('Architect', [a for a in all_agents if 'Architect' in a['class_name']]),
        ('Engineer', [a for a in all_agents if 'Engineer' in a['class_name']]),
        ('Enforcer', [a for a in all_agents if 'Enforcer' in a['class_name']]),
        ('Inspector', [a for a in all_agents if 'Inspector' in a['class_name']]),
    ]
    
    for pattern, agents in similar_groups:
        if len(agents) > 1:
            print(f"\n  {pattern} pattern ({len(agents)} agents):")
            for a in agents:
                path = a.get('path', '').replace('\\', '/').split('/')[-1]
                print(f"    - {a['class_name']} ({path})")

if __name__ == '__main__':
    main()
