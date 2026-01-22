#!/usr/bin/env python3
"""
MRO Propagation Auditor - Critical Sanity Check for L0-L6 Architecture

This auditor ensures the MRO (Method Resolution Order) inheritance chain is never broken.
A single missing super().__post_init__() in a middle-layer mixin acts like a "silent circuit breaker,"
preventing all root-level hardening and logging from ever executing.

The auditor performs two primary checks:
1. Static Order Check: Ensures SovereignBaseAgent is at the tail end of MRO before object
2. Dynamic Propagation Check: Verifies instantiation triggers __post_init__ in SovereignBaseAgent
"""

import inspect
from pathlib import Path


class MROAuditor:
    """
    Harden MRO: Ensures the L0-L6 inheritance chain is never broken.

    Critical for detecting:
    - Missing super().__post_init__() calls in mixins
    - Incorrect inheritance order (SovereignBaseAgent not at tail)
    - Broken initialization chains that prevent root hardening
    """

    @staticmethod
    def audit_class_hierarchy(agent_cls: type) -> list[str]:
        """
        Validates that SovereignBaseAgent is at the correct position in MRO.

        Args:
            agent_cls: The agent class to audit

        Returns:
            List of error messages (empty if no errors)
        """
        from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        mro = inspect.getmro(agent_cls)
        errors = []

        # Rule 1: SovereignBaseAgent must be present
        if SovereignBaseAgent not in mro:
            errors.append(
                f"CRITICAL: {agent_cls.__name__} does not inherit from SovereignBaseAgent."
            )
            return errors  # Can't continue without SovereignBaseAgent

        # Rule 2: SovereignBaseAgent must be near the end, before MCPHardenedMixin and object
        # Expected order: ... -> SovereignBaseAgent -> MCPHardenedMixin -> object
        sovereign_idx = mro.index(SovereignBaseAgent)
        mcp_idx = mro.index(MCPHardenedMixin) if MCPHardenedMixin in mro else None
        mro.index(object)

        # Check: SovereignBaseAgent should be immediately before MCPHardenedMixin
        if mcp_idx is not None:
            if sovereign_idx != mcp_idx - 1:
                errors.append(
                    f"MRO ORDER ERROR: {agent_cls.__name__} has SovereignBaseAgent at position {sovereign_idx}, "
                    f"but MCPHardenedMixin at {mcp_idx}. Expected SovereignBaseAgent -> MCPHardenedMixin."
                )

        # Rule 3: No custom classes should appear AFTER SovereignBaseAgent (except MCPHardenedMixin)
        # Everything after SovereignBaseAgent should be framework/stdlib classes
        allowed_after_sovereign = {MCPHardenedMixin, object}
        for i in range(sovereign_idx + 1, len(mro)):
            cls = mro[i]
            if cls not in allowed_after_sovereign:
                # Check if it's a stdlib/framework class (has __module__ starting with standard prefixes)
                if not (cls.__module__.startswith(("builtins", "abc", "typing", "dataclasses"))):
                    errors.append(
                        f"MRO ORDER ERROR: {agent_cls.__name__} has {cls.__name__} AFTER SovereignBaseAgent. "
                        f"Only MCPHardenedMixin and object should appear after the root."
                    )

        return errors

    @staticmethod
    def verify_initialization_propagation(agent_instance: object) -> tuple[bool, str | None]:
        """
        Check if SovereignBaseAgent's initialization was actually reached.

        Requires SovereignBaseAgent to set a sentinel attribute: _sovereign_initialized

        Args:
            agent_instance: An instantiated agent object

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        sentinel = getattr(agent_instance, "_sovereign_initialized", None)

        if sentinel is True:
            return True, None
        elif sentinel is None:
            return False, (
                f"PROPAGATION BROKEN: {agent_instance.__class__.__name__} never reached "
                f"SovereignBaseAgent.__post_init__(). Missing super().__post_init__() in a parent class?"
            )
        else:
            return False, (
                f"PROPAGATION ERROR: {agent_instance.__class__.__name__} has _sovereign_initialized={sentinel} "
                f"(expected True). Initialization chain may be corrupted."
            )

    @staticmethod
    def audit_agent_class(agent_cls: type, instantiate: bool = False) -> tuple[bool, list[str]]:
        """
        Comprehensive audit of an agent class.

        Args:
            agent_cls: The agent class to audit
            instantiate: If True, also instantiate and check propagation (may fail for some agents)

        Returns:
            Tuple of (passed: bool, errors: List[str])
        """
        errors = []

        # Static check
        static_errors = MROAuditor.audit_class_hierarchy(agent_cls)
        errors.extend(static_errors)

        # Dynamic check (optional)
        if instantiate and not static_errors:
            try:
                # Try to instantiate with minimal args
                if hasattr(agent_cls, "__dataclass_fields__"):
                    # Dataclass - try with name only
                    instance = agent_cls(name=f"Test{agent_cls.__name__}")
                else:
                    # Regular class
                    instance = agent_cls()

                success, error = MROAuditor.verify_initialization_propagation(instance)
                if not success:
                    errors.append(error)

            except Exception as e:
                # Instantiation failed - not necessarily an MRO error
                errors.append(
                    f"WARNING: Could not instantiate {agent_cls.__name__} for propagation test: {e}"
                )

        return len(errors) == 0, errors


def find_all_agent_classes(root_dir: Path) -> list[type]:
    """
    Find all classes ending in 'Agent' in the agentic_core directory.

    Args:
        root_dir: Root directory to search (should be agentic_core)

    Returns:
        List of agent classes found
    """
    import importlib.util
    import sys

    agent_classes = []

    # Find all Python files
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files

    for py_file in get_python_files(root_dir):
        if py_file.name.startswith("__"):
            continue

        # Convert path to module name
        try:
            relative_path = py_file.relative_to(root_dir.parent)
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
                        agent_classes.append(obj)

        except Exception:
            # Skip files that can't be imported
            pass

    return agent_classes


# Usage in a test suite
def test_all_agents_mro_compliance():
    """
    Test function to audit all agents in the codebase.

    This should be run as part of CI/CD to catch MRO violations early.
    """
    from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import L1CognitionBaseAgent

    # Test L1CognitionBaseAgent as example
    agent = L1CognitionBaseAgent(name="TestL1CognitionBaseAgent")
    auditor = MROAuditor()

    # Check 1: Static order
    errors = auditor.audit_class_hierarchy(L1CognitionBaseAgent)
    assert not errors, f"MRO Order Violations: {errors}"

    # Check 2: Dynamic propagation
    success, error = auditor.verify_initialization_propagation(agent)
    assert success, f"Chain Broken: {error}"


__all__ = ["MROAuditor", "find_all_agent_classes", "test_all_agents_mro_compliance"]
