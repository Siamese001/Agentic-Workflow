"""
Agent Suffix Addition Plan

This script analyzes classes that should have 'Agent' suffix but don't,
and generates a migration plan.

Categories:
1. RENAME: Classes that are clearly agents and need suffix
2. EXCLUDE: Test classes, Mixins, Clients that are utilities
3. REVIEW: Ambiguous cases needing human review
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, prompt
# This boosts alignment detection — review and integrate appropriately

import json
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
)

# Patterns that indicate a class is NOT an agent (exclude from renaming)
EXCLUDE_PATTERNS = [
    "Test",  # Test classes
    "Mixin",  # Utility mixins
    "Context",  # Data contexts
    "Config",  # configuration
    "Protocol",  # Interfaces
    "Exception",  # Errors
    "Error",  # Errors
    "Enum",  # Enums
    "Model",  # Data models
    "schema",  # Schemas
    "Interface",  # Interfaces
    "Base",  # Base classes (already utility)
    "Abstract",  # Abstract classes
]

# Patterns that indicate a class IS an agent (should have Agent suffix)
AGENT_PATTERNS = [
    "Orchestrator",
    "Manager",
    "Handler",
    "Executor",
    "Validator",
    "Inspector",
    "Auditor",
    "Guardian",
    "Sentinel",
    "Enforcer",
    "router",
    "Planner",
    "Analyzer",
    "Coordinator",
    "Dispatcher",
    "Monitor",
    "Tracker",
    "Detector",
    "Fixer",
    "Healer",
    "Mapper",
    "Builder",
    "Generator",
    "Optimizer",
    "Classifier",
]

# Sovereign* classes that are MCP clients (utility, not agents)
SOVEREIGN_CLIENT_PATTERNS = [
    "SovereignRedisClient",
    "SovereignPineconeClient",
    "SovereignHttpClient",
    "SovereignGitClient",
    "SovereignFetchClient",
    "SovereignFigmaClient",
    "SovereignPlaywrightMcpClient",
    "SovereignFilesystemMcpClient",
    "SovereignGitKrakenMcpClient",
    "SovereignDeepWikiClient",
    "SovereignLlmRouterMcpClient",
    "SovereignRedisMcpClient",
    "SovereignPineconeMcpClient",
    "SovereignGraphClient",
    "SovereignMcpRouter",
    "SovereignSemanticCache",
]


def categorize_class(name: str, path: str) -> tuple[str, str]:
    """
    Categorize a class into RENAME, EXCLUDE, or REVIEW.

    Returns: (category, reason)
    """
    # Already has Agent suffix
    if name.endswith("Agent"):
        return ("SKIP", "Already has Agent suffix")

    # Test classes
    if name.startswith("Test") or "/tests/" in path or "test_" in path:
        return ("EXCLUDE", "Test class")

    # Sovereign MCP clients (utilities, not agents)
    if name in SOVEREIGN_CLIENT_PATTERNS or name.endswith("Client"):
        return ("EXCLUDE", "MCP Client utility")

    # Mixins
    if "Mixin" in name:
        return ("EXCLUDE", "Mixin utility class")

    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in name and not any(ap in name for ap in AGENT_PATTERNS):
            return ("EXCLUDE", f"Matches exclude pattern: {pattern}")

    # Check agent patterns - these should be renamed
    for pattern in AGENT_PATTERNS:
        if name.endswith(pattern):
            new_name = name + "Agent" if not name.endswith("Agent") else name
            return ("RENAME", f"{name} -> {new_name}")

    # Sovereign* that aren't clients might be agents
    if name.startswith("Sovereign") and not name.endswith("Client"):
        return ("RENAME", f"{name} -> {name}Agent")

    # Default: needs review
    return ("REVIEW", "Ambiguous - needs human review")


def main():
    root = Path("C:/Git/Agentic-Workflow")
    data = json.load(open(root / AGENT_DISCOVERY_JSON))

    categories = {"RENAME": [], "EXCLUDE": [], "REVIEW": [], "SKIP": []}

    for agent in data:
        name = agent.get("class_name", "")
        path = agent.get("path", "")
        layer = agent.get("layer", "?")

        category, reason = categorize_class(name, path)
        categories[category].append({"name": name, "layer": layer, "path": path, "reason": reason})

    # Print summary
    print("=" * 60)
    print("AGENT SUFFIX MIGRATION PLAN")
    print("=" * 60)

    print(f"\n### RENAME ({len(categories['RENAME'])} classes)")
    print("These classes should have 'Agent' suffix added:\n")
    for item in sorted(categories["RENAME"], key=lambda x: x["name"]):
        print(f"  [{item['layer']}] {item['reason']}")

    print(f"\n### EXCLUDE ({len(categories['EXCLUDE'])} classes)")
    print("These are utilities/tests, NOT agents:\n")
    for item in sorted(categories["EXCLUDE"], key=lambda x: x["name"])[:20]:
        print(f"  [{item['layer']}] {item['name']}: {item['reason']}")
    if len(categories["EXCLUDE"]) > 20:
        print(f"  ... and {len(categories['EXCLUDE']) - 20} more")

    print(f"\n### REVIEW ({len(categories['REVIEW'])} classes)")
    print("These need human review:\n")
    for item in sorted(categories["REVIEW"], key=lambda x: x["name"]):
        filename = (
            item["path"].split("\\")[-1] if "\\" in item["path"] else item["path"].split("/")[-1]
        )
        print(f"  [{item['layer']}] {item['name']} ({filename})")

    print(f"\n### SKIP ({len(categories['SKIP'])} classes)")
    print("Already have 'Agent' suffix")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  RENAME:  {len(categories['RENAME'])} classes")
    print(f"  EXCLUDE: {len(categories['EXCLUDE'])} classes (remove from registry)")
    print(f"  REVIEW:  {len(categories['REVIEW'])} classes")
    print(f"  SKIP:    {len(categories['SKIP'])} classes (already correct)")

    return categories


if __name__ == "__main__":
    main()
