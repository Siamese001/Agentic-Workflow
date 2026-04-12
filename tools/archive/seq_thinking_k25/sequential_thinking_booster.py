#!/usr/bin/env python3
"""
Sequential Thinking Booster for Kimi K2.5 - HARDENED
Aggressive tool prioritization that enforces sequential thinking dominance over cascade chat.
"""

import json
import sys
from pathlib import Path
from typing import Any

# HARDENED: Tool categories with strict priority enforcement
CRITICAL_TOOLS = ["sequential_thinking", "mcp7_sequentialthinking"]
CORE_TOOLS = ["filesystem", "adg_redis", "memory", "adg_status", "adg_meta"]
SUPPRESSED_TOOLS = ["chat", "cascade_chat", "simple_chat", "fallback_chat"]
REASONING_TOOLS = ["analysis", "reasoning", "planning", "dependency", "graph", "architecture", "debug"]


def boost_sequential_thinking(tools_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Boost sequential thinking with AGGRESSIVE priority - suppresses cascade chat."""
    critical_tools = []
    reasoning_tools = []
    core_tools = []
    suppressed_tools = []
    other_tools = []

    for tool in tools_list:
        tool_name = tool.get("name", "").lower()
        tool_desc = tool.get("description", "").lower()

        # HARDENED: Check for critical sequential thinking tools
        if any(ct in tool_name for ct in CRITICAL_TOOLS):
            critical_tools.append(tool)
        # HARDENED: Suppress cascade chat tools
        elif any(st in tool_name or st in tool_desc for st in SUPPRESSED_TOOLS):
            suppressed_tools.append(tool)
        # Core infrastructure tools
        elif tool_name in CORE_TOOLS:
            core_tools.append(tool)
        # Reasoning/analysis tools
        elif any(rt in tool_name or rt in tool_desc for rt in REASONING_TOOLS):
            reasoning_tools.append(tool)
        else:
            other_tools.append(tool)

    # HARDENED: Strict priority order - sequential thinking ALWAYS first
    # Suppressed tools (chat) go to the END (lowest priority)
    return critical_tools + reasoning_tools + core_tools + other_tools + suppressed_tools


def apply_kimi_k2_5_boosting(tools_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply HARDENED Kimi K2.5 boosting rules - suppresses chat, enforces sequential dominance."""

    # HARDENED: Kimi K2.5 prioritized tool categories (expanded)
    kimi_k2_5_categories = [
        "sequential",
        "analysis",
        "reasoning",
        "planning",
        "thinking",
        "dependency",
        "graph",
        "architecture",
        "debug",
        "validation",
        "audit",
        "compliance",
        "governance",
        "safety",
    ]

    # HARDENED: Chat/cascade suppression patterns
    chat_suppression_patterns = [
        "chat",
        "cascade",
        "fallback",
        "simple",
        "basic",
        "quick",
        "immediate",
        "instant",
        "direct",
    ]

    critical_tools = []
    kimi_k2_5_tools = []
    core_tools = []
    other_tools = []
    suppressed_tools = []  # Chat/cascade tools get pushed to end

    for tool in tools_list:
        tool_name = tool.get("name", "").lower()
        tool_desc = tool.get("description", "").lower()

        # HARDENED: Check if tool is sequential thinking (absolute priority)
        is_sequential = "sequential" in tool_name or "sequential_thinking" in tool_name

        # HARDENED: Check if tool matches Kimi K2.5 categories
        is_kimi_k2_5 = any(cat in tool_name or cat in tool_desc for cat in kimi_k2_5_categories)

        # HARDENED: Check if tool should be suppressed (chat/cascade)
        is_suppressed = any(pat in tool_name or pat in tool_desc for pat in chat_suppression_patterns)

        if is_sequential:
            critical_tools.append(tool)
        elif is_suppressed:
            suppressed_tools.append(tool)
        elif is_kimi_k2_5:
            kimi_k2_5_tools.append(tool)
        elif tool_name in CORE_TOOLS:
            core_tools.append(tool)
        else:
            other_tools.append(tool)

    # HARDENED: Sort Kimi K2.5 tools with sequential thinking first
    kimi_k2_5_tools.sort(key=lambda t: 0 if "sequential" in t.get("name", "").lower() else 1)

    # HARDENED: Return with suppressed tools at END (lowest priority)
    return critical_tools + kimi_k2_5_tools + core_tools + other_tools + suppressed_tools


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

    tools_list = tools_data.get("tools", [])
    if not tools_list:
        print("Warning: No tools found in the input file")
        # Create empty boosted file
        boosted_tools = []
    else:
        # Apply HARDENED boosting strategies
        print(f"Processing {len(tools_list)} tools with HARDENED Kimi K2.5 boosting...")

        # First boost: aggressive sequential thinking priority
        boosted_tools = boost_sequential_thinking(tools_list)

        # Second boost: HARDENED Kimi K2.5 suppression of cascade chat
        boosted_tools = apply_kimi_k2_5_boosting(boosted_tools)

        # Count sequential thinking tools
        seq_count = len([t for t in boosted_tools if "sequential" in t.get("name", "").lower()])
        suppressed_count = len(
            [
                t
                for t in boosted_tools
                if any(pat in t.get("name", "").lower() for pat in ["chat", "cascade", "fallback"])
            ]
        )
        print(f"Boosted {seq_count} sequential thinking tools to ABSOLUTE priority")
        print(f"Suppressed {suppressed_count} chat/cascade tools to LOWEST priority")

    # Write boosted configuration
    try:
        with open(output_file, "w") as f:
            json.dump({"tools": boosted_tools}, f, indent=2)
        print(f"Output written to: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

    # Print HARDENED summary
    print("\n" + "=" * 60)
    print("HARDENED Kimi K2.5 Boosting Summary:")
    print("=" * 60)
    print(f"  Total tools: {len(boosted_tools)}")
    print(
        f"  Sequential thinking (ABSOLUTE PRIORITY): {len([t for t in boosted_tools if 'sequential' in t.get('name', '').lower()])}"
    )
    print(
        f"  Kimi K2.5 relevant tools: {len([t for t in boosted_tools if any(cat in t.get('name', '').lower() or cat in t.get('description', '').lower() for cat in ['sequential', 'analysis', 'reasoning', 'planning', 'dependency', 'graph', 'architecture', 'debug', 'thinking', 'validation', 'audit', 'compliance', 'governance', 'safety'])])}"
    )
    print(
        f"  Cascade/Chat tools (SUPPRESSED): {len([t for t in boosted_tools if any(pat in t.get('name', '').lower() for pat in ['chat', 'cascade', 'fallback'])])}"
    )
    print("  DOMINANCE MODE: ENABLED - Sequential thinking prioritized ABOVE cascade chat")
    print("=" * 60)


if __name__ == "__main__":
    main()
