#!/usr/bin/env python3
"""Analyze zombie agents - agents that are discovered but never called."""

import json
from pathlib import Path

# Load all discovered agents
with open('agent_discovery_full.json', encoding='utf-8') as f:
    all_agents = json.load(f)

# Agents that are actually called in canon_validator_agentic_v2_thin.py
# Based on code analysis of the validator
CALLED_AGENTS = {
    'NamingAgent',           # Line 562, 627 - called in heal mode
    'AutonomyGuardianAgent', # Line 563, 628 - called in heal mode
}

# Additional agents that can be invoked via --agent flag (but not in main flow)
INVOKABLE_AGENTS = set()  # All agents are invokable via --agent flag

print("=" * 80)
print("ZOMBIE AGENT ANALYSIS REPORT")
print("Canon Validator Dry Run Analysis")
print("=" * 80)

print(f"\nTotal Discovered Agents: {len(all_agents)}")
print(f"Agents Called in Main Flow: {len(CALLED_AGENTS)}")

# Categorize agents
zombie_agents = []
called_agents = []

for agent in all_agents:
    agent_name = agent['class_name']
    if agent_name in CALLED_AGENTS:
        called_agents.append(agent)
    else:
        zombie_agents.append(agent)

print(f"Zombie Agents (Never Called): {len(zombie_agents)}")

# Report actively called agents
print("\n" + "=" * 80)
print("ACTIVELY CALLED AGENTS (Main Heal Flow)")
print("=" * 80)
for agent in called_agents:
    print(f"  ✓ {agent['class_name']:<45} [{agent['layer']}] {agent['territory']}")

# Report zombie agents by layer
print("\n" + "=" * 80)
print("ZOMBIE AGENTS (Discovered but Never Called)")
print("=" * 80)

layers = {}
for agent in zombie_agents:
    layer = agent.get('layer', 'Unknown')
    if layer not in layers:
        layers[layer] = []
    layers[layer].append(agent)

for layer in sorted(layers.keys()):
    agents_in_layer = layers[layer]
    print(f"\n{layer} ({len(agents_in_layer)} agents):")
    for agent in sorted(agents_in_layer, key=lambda x: x['class_name']):
        name = agent['class_name']
        territory = agent.get('territory', 'Unknown')
        has_healing = agent.get('has_healing', False)
        healing_mark = "🔧" if has_healing else "  "
        print(f"  {healing_mark} {name:<45} [{territory}]")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

zombie_with_healing = [a for a in zombie_agents if a.get('has_healing', False)]
zombie_without_healing = [a for a in zombie_agents if not a.get('has_healing', False)]

print(f"\nZombie Agents with heal_repository(): {len(zombie_with_healing)}")
print(f"Zombie Agents without heal_repository(): {len(zombie_without_healing)}")

# Breakdown by category
categories = {}
for agent in zombie_agents:
    cat = agent.get('category', 'Unknown')
    categories[cat] = categories.get(cat, 0) + 1

print("\nZombie Agents by Category:")
for cat in sorted(categories.keys(), key=lambda x: categories[x], reverse=True):
    print(f"  {cat:<20} {categories[cat]:>3} agents")

# Recommendations
print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print("""
1. CRITICAL: Only 2 agents are called in the main heal flow:
   - NamingAgent
   - AutonomyGuardianAgent
   
2. All other 263 agents are "zombie agents" - discovered but never executed
   in the canonical validation/healing workflow.

3. These zombie agents can only be invoked manually via:
   python canon_validator_agentic_v2_thin.py --agent <AgentName>

4. SUGGESTED ACTIONS:
   a) Review if additional agents should be added to the heal flow
   b) Consider creating orchestration layers that call relevant agents
   c) Document which agents are intentionally manual-only
   d) Consider deprecating/archiving truly unused agents
   
5. HIGH-VALUE ZOMBIE AGENTS TO CONSIDER ACTIVATING:
   - LocationAgent (L5 Safety) - validates file territories
   - HierarchyAgent (L5 Safety) - validates depth compliance
   - ImportAgent (L5 Safety) - validates import statements
   - GovernanceAgent (L1 Cognition) - architectural governance
   - FilesystemSSOTReconcilerAgent (L0 Maintenance) - blueprint sync
""")

print("=" * 80)
