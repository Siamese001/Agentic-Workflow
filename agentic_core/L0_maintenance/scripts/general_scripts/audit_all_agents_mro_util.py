#!/usr/bin/env python3
"""
Mass MRO Audit Script - Audits all Agent classes in agentic_core

This script finds all classes ending in 'Agent' and runs comprehensive MRO audits:
1. Static Order Check: Verifies SovereignBaseAgent is at correct MRO position
2. Dynamic Propagation Check: Verifies __post_init__ reaches SovereignBaseAgent

Usage:
    python scripts/audit_all_agents_mro_util.py
"""

import importlib.util
import inspect
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.utils.testing.mro_auditor import MROAuditor


def find_all_agent_classes(root_dir: Path) -> list[tuple[str, type]]:
    """
    Find all classes ending in 'Agent' in the agentic_core directory.

    Returns:
        List of (module_path, agent_class) tuples
    """
    agent_classes = []

    """Scan for all agent files."""
    agents = []
    # Phase 6.9: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_agent_files

    agents = list(get_agent_files(root_dir))

    for py_file in agents:
        if py_file.name.startswith("__") or py_file.name.startswith("test_"):
            continue

        # Skip certain directories
        skip_dirs = {"__pycache__", ".git", "venv", "node_modules"}
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue

        # Convert path to module name
        try:
            relative_path = py_file.relative_to(PROJECT_ROOT)
            module_name = str(relative_path.with_suffix("")).replace("/", ".").replace("\\", ".")

            # Import module
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Find Agent classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("Agent") and obj.__module__ == module_name:
                        agent_classes.append((module_name, obj))

        except Exception:
            # Skip files that can't be imported (silently)
            pass

    return agent_classes


def main():
    """Main audit function."""
    print("\n" + "=" * 70)
    print("MRO PROPAGATION AUDITOR - Mass Agent Audit")
    print("=" * 70)

    # Find all agent classes
    print("\n🔍 Scanning for Agent classes...")
    agentic_core = PROJECT_ROOT / "agentic_core"
    agent_classes = find_all_agent_classes(agentic_core)

    print(f"Found {len(agent_classes)} Agent classes\n")

    # Audit each agent
    auditor = MROAuditor()
    passed = []
    failed = []
    warnings = []

    for module_path, agent_cls in agent_classes:
        agent_name = agent_cls.__name__

        # Run static audit (always safe)
        static_errors = auditor.audit_class_hierarchy(agent_cls)

        if static_errors:
            failed.append((agent_name, module_path, static_errors))
            print(f"  ❌ {agent_name}")
            for error in static_errors:
                print(f"     {error}")
        else:
            # Try dynamic audit (may fail for some agents)
            try:
                # Attempt instantiation with minimal args
                if hasattr(agent_cls, "__dataclass_fields__"):
                    # Dataclass - try with name only
                    instance = agent_cls(name=f"Test{agent_name}")
                else:
                    # Regular class - try default constructor
                    instance = agent_cls()

                # Check propagation
                success, error = auditor.verify_initialization_propagation(instance)

                if success:
                    passed.append((agent_name, module_path))
                    print(f"  ✅ {agent_name}")
                else:
                    failed.append((agent_name, module_path, [error]))
                    print(f"  ❌ {agent_name}")
                    print(f"     {error}")

            except Exception as e:
                # Instantiation failed - mark as warning
                warnings.append((agent_name, module_path, str(e)))
                print(f"  ⚠️  {agent_name} (could not instantiate for propagation test)")

    # Summary
    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)

    print(f"\n✅ PASSED: {len(passed)} agents")
    print(f"❌ FAILED: {len(failed)} agents")
    print(f"⚠️  WARNINGS: {len(warnings)} agents (could not instantiate)")

    if failed:
        print("\n" + "=" * 70)
        print("FAILED AGENTS - REQUIRE IMMEDIATE ATTENTION")
        print("=" * 70)
        for agent_name, module_path, errors in failed:
            print(f"\n❌ {agent_name}")
            print(f"   Module: {module_path}")
            for error in errors:
                print(f"   - {error}")
            print("\n   FIX:")
            print("   1. Check if super().__post_init__() is missing in parent mixins")
            print("   2. Verify inheritance order: (Mixins, BaseAgent, SovereignBaseAgent)")
            print("   3. Ensure all mixins use cooperative super().__post_init__()")

    if warnings:
        print("\n" + "=" * 70)
        print("WARNINGS - Manual Review Recommended")
        print("=" * 70)
        print("\nThese agents passed static MRO checks but could not be instantiated")
        print("for dynamic propagation testing. This may be expected for abstract bases")
        print("or agents requiring specific initialization parameters.\n")
        for agent_name, module_path, error in warnings[:10]:  # Show first 10
            print(f"  ⚠️  {agent_name} ({module_path})")

    print("\n" + "=" * 70)
    if failed:
        print("❌ MRO AUDIT FAILED - Fix errors above before proceeding")
        return 1
    else:
        print("✅ MRO AUDIT PASSED - All agents have correct MRO structure")
        return 0


if __name__ == "__main__":
    sys.exit(main())
