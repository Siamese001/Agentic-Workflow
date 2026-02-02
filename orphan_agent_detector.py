#!/usr/bin/env python3
"""
Orphan Agent Detection Script
Identifies agents that are not referenced or imported elsewhere in the codebase.
Uses SSOT discovery system for accurate agent enumeration.
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import SSOT discovery system
try:
    from agentic_core.L0_maintenance.scripts.full_agent_discovery import (
        discover_all_agents,
    )

    SSOT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SSOT discovery not available ({e}), falling back to JSON file")
    SSOT_AVAILABLE = False


def load_agent_discovery():
    """Load agent discovery data using SSOT or fallback to JSON"""
    if SSOT_AVAILABLE:
        try:
            return discover_all_agents()
        except Exception as e:
            print(f"SSOT discovery failed: {e}, falling back to JSON")

    # Fallback to direct JSON loading
    try:
        with open("agent_discovery_full.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: agent_discovery_full.json not found")
        print("Please run agent discovery first:")
        print("  python -m agentic_core.L0_maintenance.scripts.full_agent_discovery")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing agent_discovery_full.json: {e}")
        sys.exit(1)


def scan_agent_usage(agents):
    """Scan codebase for agent imports and references"""
    agent_classes = set(agent["class_name"] for agent in agents)
    agent_files = {agent["class_name"]: agent["path"] for agent in agents}

    all_imports = defaultdict(set)
    all_references = defaultdict(set)

    # Directories to skip for performance and to avoid hanging
    SKIP_DIRS = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "node_modules",
        ".vscode",
        ".idea",
        "dist",
        "build",
        ".backup",
        "archive",
        "logs",
        "reports",
        "data/external",
    }

    # File patterns to skip
    SKIP_PATTERNS = {"test_", "_test.py", "conftest.py", "mock_", "fixture", "temp_"}

    files_scanned = 0
    files_skipped = 0

    # Pre-compile regex patterns for efficiency
    agent_patterns = {agent: re.compile(rf"\b{re.escape(agent)}\b") for agent in agent_classes}

    # Scan all Python files
    for root, dirs, files in os.walk("."):
        # Skip problematic directories early
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        # Skip if current path contains skip patterns
        if any(skip in root for skip in SKIP_DIRS):
            files_skipped += len(files)
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            # Skip test files and other patterns
            if any(pattern in file for pattern in SKIP_PATTERNS):
                files_skipped += 1
                continue

            file_path = os.path.join(root, file).replace("\\", "/")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                files_scanned += 1

                # Find imports of agents (more efficient)
                import_matches = re.findall(
                    r"(?:from\s+\S+\s+)?import\s+([A-Z][a-zA-Z0-9]*Agent)", content
                )
                for match in import_matches:
                    if match in agent_classes:
                        all_imports[match].add(file_path)

                # Find direct references using pre-compiled patterns (much faster)
                for agent_class, pattern in agent_patterns.items():
                    if pattern.search(content):
                        all_references[agent_class].add(file_path)

            except Exception:
                files_skipped += 1
                continue  # Skip problematic files silently

    print(f"Scanned {files_scanned} files, skipped {files_skipped} files")
    return all_imports, all_references, agent_files


def identify_orphans(agents, all_imports, all_references, agent_files):
    """Identify potential orphan agents"""
    agent_classes = set(agent["class_name"] for agent in agents)
    orphan_agents = []

    for agent_class in agent_classes:
        # Get agent's own file path
        own_file = agent_files.get(agent_class, "")

        # Filter out own file and test files from references
        non_self_refs = [ref for ref in all_references[agent_class] if ref != own_file]
        non_test_refs = [ref for ref in non_self_refs if "/tests/" not in ref]

        # Consider orphan if:
        # 1. No references outside of its own file
        # 2. No references outside of tests
        # 3. Very few total references (suggesting minimal usage)

        is_orphan = (
            len(non_test_refs) == 0  # No production usage
            or len(all_references[agent_class]) <= 2  # Only referenced in own file + maybe one test
        )

        if is_orphan:
            orphan_agents.append(
                {
                    "class_name": agent_class,
                    "path": agent_files[agent_class],
                    "total_references": len(all_references[agent_class]),
                    "non_test_references": len(non_test_refs),
                    "all_references": list(all_references[agent_class]),
                    "imports": list(all_imports[agent_class]),
                }
            )

    return orphan_agents


def main():
    print("=== Orphan Agent Detection ===")

    # Load agent data
    agents = load_agent_discovery()
    print(f"Total agents discovered: {len(agents)}")

    # Scan for usage
    all_imports, all_references, agent_files = scan_agent_usage(agents)

    # Identify orphans
    orphan_agents = identify_orphans(agents, all_imports, all_references, agent_files)

    print(f"\nFound {len(orphan_agents)} potential orphan agents:")
    print("=" * 80)

    for i, orphan in enumerate(sorted(orphan_agents, key=lambda x: x["class_name"])):
        print(f"\n{i + 1}. {orphan['class_name']}")
        print(f"   Path: {orphan['path']}")
        print(f"   Total References: {orphan['total_references']}")
        print(f"   Non-Test References: {orphan['non_test_references']}")
        if orphan["all_references"]:
            print(f"   Referenced in: {', '.join(orphan['all_references'][:3])}")
        if orphan["imports"]:
            print(f"   Imported by: {', '.join(orphan['imports'][:3])}")

    # Save results
    with open("orphan_agents_report.json", "w") as f:
        json.dump(orphan_agents, f, indent=2)

    print("\n=== Summary ===")
    print(f"Total agents: {len(agents)}")
    print(f"Potential orphans: {len(orphan_agents)}")
    print(f"Orphan percentage: {len(orphan_agents) / len(agents) * 100:.1f}%")
    print("Results saved to: orphan_agents_report.json")


if __name__ == "__main__":
    main()
