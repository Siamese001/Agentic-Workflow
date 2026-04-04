#!/usr/bin/env python3
"""
Debug System Restructuring Template
Fix the missing "layer violations" data
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.append(str(repo_root))

from agentic_core.planning.sequential_thinking_workflow import SequentialThinkingEnhancedWorkflow


def debug_system_restructuring():
    """Debug the System Restructuring template."""

    print("🔍 DEBUGGING SYSTEM RESTRUCTURING TEMPLATE")
    print("=" * 60)

    workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)

    step_config = {
        'name': 'System Restructuring',
        'type': 'system_restructuring',
        'complexity': 'critical',
        'files': ['legacy.py']
    }

    template_content = workflow._get_seq_thinking_template('system_restructuring', step_config)

    print("📋 System Restructuring Template Content:")
    print("-" * 50)

    # Show first 40 lines
    lines = template_content.split('\n')
    for i, line in enumerate(lines[:40]):
        print(f"{i+1:2d}: {line}")

    # Check for specific values
    print("\n🔍 Checking for specific values:")
    check_values = [
        'layer violations',
        'Layer violations',
        'layer violations,',
        'Layer violations,',
        'identified_issues',
        'system_size',
        'complexity_metrics',
        'restructuring_goals'
    ]

    for value in check_values:
        present = value in template_content
        print(f"   {'✅' if present else '❌'} '{value}': {'Found' if present else 'Not Found'}")

    # Look for any section with issues
    print("\n📊 Looking for issues/restructuring sections:")
    if "## Current Issues" in template_content:
        print("   ✅ Current Issues section found")
        issues_start = template_content.find("## Current Issues")
        issues_end = template_content.find("##", issues_start + 1)
        if issues_end == -1:
            issues_end = len(template_content)

        issues_section = template_content[issues_start:issues_end]
        print("   Content:")
        for line in issues_section.split('\n')[:10]:
            if line.strip():
                print(f"      {line}")
    else:
        print("   ❌ Current Issues section not found")

    return template_content

if __name__ == "__main__":
    debug_system_restructuring()
