#!/usr/bin/env python3
"""
compare_agent_lists.py - Compare agent lists between commits to trace reductions
"""
import subprocess
import json
import sys
from pathlib import Path
from collections import defaultdict

def get_agents_at_commit(commit_hash):
    """Get agent list from agent_discovery_full.json at a specific commit."""
    result = subprocess.run(
        ["git", "show", f"{commit_hash}:agent_discovery_full.json"],
        capture_output=True,
        text=True,
        cwd="C:/Git/Agentic-Workflow"
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        agents = {}
        for a in data:
            agents[a['class_name']] = {
                'path': a.get('path', ''),
                'layer': a.get('layer', 'Unknown'),
            }
        return agents
    return {}

def get_current_agents():
    """Get current agent list."""
    with open("C:/Git/Agentic-Workflow/agent_discovery_full.json") as f:
        data = json.load(f)
    agents = {}
    for a in data:
        agents[a['class_name']] = {
            'path': a.get('path', ''),
            'layer': a.get('layer', 'Unknown'),
        }
    return agents

def find_agent_in_archives(agent_name):
    """Search for agent in archives directory."""
    archives = Path("C:/Git/Agentic-Workflow/archives")
    results = []
    for f in archives.rglob(f"*{agent_name}*"):
        if f.is_file():
            rel = f.relative_to(archives)
            results.append(str(rel))
    return results

def main():
    # Commit with 209 agents (from waterfall analysis)
    commit_209 = "3277e45c6"  # 2026-01-04: 209 agents

    print("=" * 80)
    print("AGENT LIST COMPARISON: 209 agents -> 120 agents")
    print("=" * 80)

    print(f"\nFetching agents from commit {commit_209}...")
    old_agents = get_agents_at_commit(commit_209)
    print(f"  Found {len(old_agents)} agents")

    print("\nFetching current agents...")
    current_agents = get_current_agents()
    print(f"  Found {len(current_agents)} agents")

    # Find missing agents
    missing = set(old_agents.keys()) - set(current_agents.keys())
    added = set(current_agents.keys()) - set(old_agents.keys())

    print(f"\n{'=' * 80}")
    print(f"MISSING AGENTS: {len(missing)}")
    print(f"ADDED AGENTS: {len(added)}")
    print(f"{'=' * 80}")

    # Categorize missing agents by their archive location
    categories = defaultdict(list)
    not_found = []

    print("\nSearching archives for missing agents...")
    for agent in sorted(missing):
        archive_locs = find_agent_in_archives(agent)
        if archive_locs:
            # Get the top-level archive folder
            for loc in archive_locs:
                folder = loc.split("\\")[0].split("/")[0]
                categories[folder].append((agent, loc))
                break
        else:
            not_found.append(agent)

    print(f"\n{'=' * 80}")
    print("MISSING AGENTS BY ARCHIVE CATEGORY")
    print(f"{'=' * 80}")

    for category in sorted(categories.keys(), key=lambda x: -len(categories[x])):
        agents = categories[category]
        print(f"\n## {category}/ ({len(agents)} agents)")
        for agent, loc in sorted(agents)[:10]:
            print(f"   - {agent}")
        if len(agents) > 10:
            print(f"   ... and {len(agents) - 10} more")

    if not_found:
        print(f"\n## NOT IN ARCHIVES ({len(not_found)} agents)")
        print("   (Likely consolidated, renamed, or excluded from discovery)")
        for agent in sorted(not_found)[:20]:
            print(f"   - {agent}")
        if len(not_found) > 20:
            print(f"   ... and {len(not_found) - 20} more")

    print(f"\n{'=' * 80}")
    print("NEWLY ADDED AGENTS (in current but not in 209 snapshot)")
    print(f"{'=' * 80}")
    for agent in sorted(added):
        info = current_agents[agent]
        print(f"   + {agent} ({info['layer']})")

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Old count:     {len(old_agents)}")
    print(f"Current count: {len(current_agents)}")
    print(f"Missing:       {len(missing)}")
    print(f"Added:         {len(added)}")
    print(f"Net change:    {len(current_agents) - len(old_agents)}")

    print(f"\nBreakdown of {len(missing)} missing agents:")
    for category in sorted(categories.keys(), key=lambda x: -len(categories[x])):
        print(f"  {category}: {len(categories[category])}")
    print(f"  Not in archives: {len(not_found)}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
