#!/usr/bin/env python3
"""
Debug Template Content
See what's actually in the rendered templates
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

from tools.utils.planning.sequential_thinking_workflow import SequentialThinkingEnhancedWorkflow


def debug_template_content():
    """Debug what's actually in the rendered templates."""

    print("🔍 DEBUGGING TEMPLATE CONTENT")
    print("=" * 60)
    print("Checking what's actually in rendered templates")

    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)

    # Test one template in detail
    step_config = {
        'name': 'ADG Graph Analysis',
        'type': 'adg_analysis',
        'complexity': 'high',
        'files': ['adg.sqlite']
    }

    template_content = workflow._get_seq_thinking_template('adg_analysis', step_config)

    print("📋 ADG Graph Analysis Template Content:")
    print("-" * 50)

    # Show first 30 lines
    lines = template_content.split('\n')
    for i, line in enumerate(lines[:30]):
        print(f"{i+1:2d}: {line}")

    if len(lines) > 30:
        print(f"... ({len(lines)-30} more lines)")

    # Check for expected values
    print("\n🔍 Checking for expected values:")
    expected_values = [
        '10,432',  # node_count
        '681,161',  # edge_count
        '5,301',   # violation_count
        'L0: 7,220',  # layer_info
        'node_count',  # variable name
        'edge_count',  # variable name
        'violation_count',  # variable name
        'layer_info'  # variable name
    ]

    for value in expected_values:
        present = value in template_content
        print(f"   {'✅' if present else '❌'} {value}: {'Found' if present else 'Not Found'}")

    # Check for ADG context section
    print("\n📊 ADG Statistics Section:")
    if "## ADG Graph Statistics" in template_content:
        print("   ✅ ADG Graph Statistics section found")

        # Extract the statistics section
        stats_start = template_content.find("## ADG Graph Statistics")
        stats_end = template_content.find("##", stats_start + 1)
        if stats_end == -1:
            stats_end = len(template_content)

        stats_section = template_content[stats_start:stats_end]
        print("   Content:")
        for line in stats_section.split('\n')[:10]:
            if line.strip():
                print(f"      {line}")
    else:
        print("   ❌ ADG Graph Statistics section not found")

    return template_content

if __name__ == "__main__":
    debug_template_content()
