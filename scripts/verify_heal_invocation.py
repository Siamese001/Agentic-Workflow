#!/usr/bin/env python3
"""Verify heal invocation coverage after fixes."""
import json

data = json.load(open('agent_discovery_full.json'))

total = len(data)
has_invocation = sum(1 for a in data if a.get('invocation') == 'Yes')
percentage = has_invocation / total * 100

print("=" * 80)
print("HEAL INVOCATION VERIFICATION")
print("=" * 80)
print(f"Total agents: {total}")
print(f"Agents with heal invocation: {has_invocation}")
print(f"Coverage: {percentage:.1f}%")
print()

if percentage >= 100.0:
    print("✅ TARGET ACHIEVED: 100% heal invocation coverage!")
elif percentage >= 99.0:
    print(f"⚠️  NEARLY COMPLETE: {100 - percentage:.1f}% gap remaining")
    missing = [a for a in data if a.get('invocation') != 'Yes']
    for agent in missing:
        print(f"  - {agent['class_name']}: {agent.get('path')}")
else:
    print(f"❌ GAP: {100 - percentage:.1f}% ({total - has_invocation} agents)")

print("=" * 80)
