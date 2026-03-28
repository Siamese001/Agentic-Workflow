#!/usr/bin/env python3
"""
Sequential Thinking Booster for SWE 1.5
Intercepts and boosts sequential thinking tool selection.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

def boost_sequential_thinking(tools_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Boost sequential thinking priority in tool selection."""
    boosted_tools = []
    seq_thinking_tools = []
    high_priority_tools = []
    other_tools = []

    # Categorize tools
    for tool in tools_list:
        tool_name = tool.get('name', '').lower()
        if 'sequential' in tool_name:
            seq_thinking_tools.append(tool)
        elif tool_name in ['filesystem', 'adg_redis', 'memory']:
            high_priority_tools.append(tool)
        else:
            other_tools.append(tool)

    # Priority order: sequential thinking -> high priority -> others
    return seq_thinking_tools + high_priority_tools + other_tools

def apply_swe15_boosting(tools_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply SWE 1.5 specific boosting rules."""

    # SWE 1.5 prioritized tool categories
    swe15_categories = [
        'sequential', 'analysis', 'reasoning', 'planning',
        'dependency', 'graph', 'architecture', 'debug'
    ]

    boosted = []
    swe15_tools = []
    core_tools = []
    other_tools = []

    for tool in tools_list:
        tool_name = tool.get('name', '').lower()
        tool_desc = tool.get('description', '').lower()

        # Check if tool matches SWE 1.5 categories
        is_swe15 = any(cat in tool_name or cat in tool_desc for cat in swe15_categories)

        if is_swe15:
            swe15_tools.append(tool)
        elif tool_name in ['filesystem', 'adg_redis', 'memory']:
            core_tools.append(tool)
        else:
            other_tools.append(tool)

    # Sort SWE 1.5 tools with sequential thinking first
    swe15_tools.sort(key=lambda t: 0 if 'sequential' in t.get('name', '').lower() else 1)

    return swe15_tools + core_tools + other_tools

def main():
    """Main booster function."""
    if len(sys.argv) < 2:
        print("Usage: python sequential_thinking_booster.py <tools_json> [output_json]")
        sys.exit(1)

    tools_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else tools_file.parent / "boosted_tools.json"

    try:
        with open(tools_file) as f:
            tools_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Tools file not found: {tools_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in tools file: {e}")
        sys.exit(1)

    tools_list = tools_data.get('tools', [])
    if not tools_list:
        print("Warning: No tools found in the input file")
        # Create empty boosted file
        boosted_tools = []
    else:
        # Apply boosting strategies
        print(f"Processing {len(tools_list)} tools...")

        # First boost: sequential thinking priority
        boosted_tools = boost_sequential_thinking(tools_list)

        # Second boost: SWE 1.5 specific prioritization
        boosted_tools = apply_swe15_boosting(boosted_tools)

        # Count sequential thinking tools
        seq_count = len([t for t in boosted_tools if 'sequential' in t.get('name', '').lower()])
        print(f"Boosted {seq_count} sequential thinking tools to top priority")

    # Write boosted configuration
    try:
        with open(output_file, 'w') as f:
            json.dump({'tools': boosted_tools}, f, indent=2)
        print(f"Output written to: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

    # Print summary
    print("\nBoosting Summary:")
    print(f"  Total tools: {len(boosted_tools)}")
    print(f"  Sequential thinking tools: {len([t for t in boosted_tools if 'sequential' in t.get('name', '').lower()])}")
    print(f"  SWE 1.5 relevant tools: {len([t for t in boosted_tools if any(cat in t.get('name', '').lower() or cat in t.get('description', '').lower() for cat in ['sequential', 'analysis', 'reasoning', 'planning', 'dependency', 'graph', 'architecture', 'debug'])])}")

if __name__ == "__main__":
    main()
