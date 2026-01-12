#!/usr/bin/env python3
"""Verify Phase 1 fixes: L2-L5 base agents and L5 security compliance."""
import json

with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

print("=" * 80)
print("PHASE 1 VERIFICATION")
print("=" * 80)

# Check L2-L5 base agents
print("\n1. BASE AGENT TERRITORY VERIFICATION")
base_agents = [a for a in agents if a['class_name'] in ['L2Agent', 'L3Agent', 'L4Agent', 'L5Agent']]
for agent in base_agents:
    territory = agent.get('territory', 'NO TERRITORY')
    expected = 'Base Class' in territory
    status = '✅' if expected else '❌'
    print(f"   {status} {agent['class_name']}: {territory}")

# Check L5 security compliance
print("\n2. L5 SECURITY COMPLIANCE CHECK")
l5_agents = [a for a in agents if a['class_name'] in ['CompositeGuardrailAgent', 'L5SafetyExerciserAgent']]
for agent in l5_agents:
    hardened = agent.get('mcp_hardened', False)
    status = '✅' if hardened else '❌'
    print(f"   {status} {agent['class_name']}: mcp_hardened={hardened}")

# Check SovereignBaseAgent count
print("\n3. SOVEREIGNBASEAGENT DUPLICATE CHECK")
sovereign_agents = [a for a in agents if a['class_name'] == 'SovereignBaseAgent']
count = len(sovereign_agents)
status = '✅' if count == 1 else '❌'
print(f"   {status} SovereignBaseAgent count: {count} (expected: 1)")
if sovereign_agents:
    print(f"   Location: {sovereign_agents[0].get('path', 'Unknown')}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
all_base_correct = all('Base Class' in a.get('territory', '') for a in base_agents)
all_l5_hardened = all(a.get('mcp_hardened', False) for a in l5_agents)
sovereign_correct = len(sovereign_agents) == 1

if all_base_correct and all_l5_hardened and sovereign_correct:
    print("✅ ALL PHASE 1 FIXES VERIFIED")
else:
    print("❌ SOME PHASE 1 FIXES FAILED")
    if not all_base_correct:
        print("   - L2-L5 base agents not in Base Class territories")
    if not all_l5_hardened:
        print("   - L5 agents not MCP hardened")
    if not sovereign_correct:
        print("   - SovereignBaseAgent duplicate not resolved")

print("=" * 80)
