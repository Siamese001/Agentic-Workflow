"""
tests/test_rg_swarm_compliance.py - RG Swarm Compliance Test Suite

MANDATORY: 100% PASS REQUIREMENT.
Dynamically validates that EVERY agent in apps_rg/engines is V2.5 Compliant.

This test suite ensures:
1. All agents inherit from RGAgentBase
2. All agents are dataclasses
3. All agents have proper MRO with SovereignBaseAgent at root
4. No mutable defaults (list=[], dict={}, set=())
5. All agents can be instantiated successfully
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import sys
from dataclasses import is_dataclass
from pathlib import Path

import pytest

# Ensure path visibility
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent as RGAgentBase


class TestRGSwarmCompliance:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Dynamically validates that EVERY agent in apps_rg/engines is V2.5 Compliant.
    """

    @pytest.fixture
    def engine_agents(self) -> list[tuple[str, type]]:
        """
        Discover all agent classes in apps_rg/engines.

        Returns:
            List of (class_name, class_type) tuples for all agents
        """
        import apps_rg.engines as engine_pkg

        agents = []
        package_path = Path(engine_pkg.__file__).parent

        for _, name, _ in pkgutil.iter_modules([str(package_path)]):
            # Skip __init__ and non-agent modules
            if name.startswith("_"):
                continue

            try:
                module = importlib.import_module(f"apps_rg.engines.{name}")

                # Inspect all classes in the module
                for cls_name, cls in inspect.getmembers(module, inspect.isclass):
                    # Filter: Must be defined in this module (not imported)
                    if cls.__module__ != module.__name__:
                        continue

                    # Filter: Must be an "Agent" (by naming convention)
                    if "Agent" in cls_name and cls_name != "RGAgentBase":
                        agents.append((cls_name, cls))

            except (ImportError, NameError, AttributeError, TypeError) as e:
                pytest.fail(f"Failed to import module {name}: {e}")

        return agents

    def test_all_engines_are_sovereign(self, engine_agents: list[tuple[str, type]]) -> None:
        """
        The 'No Legacy Left Behind' Test.
        Validates that EVERY agent inherits from RGAgentBase.
        """
        failures = []

        for cls_name, cls in engine_agents:
            # CHECK 1: Inheritance from RGAgentBase
            if not issubclass(cls, RGAgentBase):
                failures.append(
                    f"❌ {cls_name} does not inherit from RGAgentBase! "
                    f"MRO: {[c.__name__ for c in cls.__mro__]}"
                )

        if failures:
            pytest.fail("\n".join(failures))

    def test_all_engines_are_dataclasses(self, engine_agents: list[tuple[str, type]]) -> None:
        """
        Validates that all agents are dataclasses.
        """
        failures = []

        for cls_name, cls in engine_agents:
            if not is_dataclass(cls):
                failures.append(f"❌ {cls_name} is not a dataclass!")

        if failures:
            pytest.fail("\n".join(failures))

    def test_mro_hardening(self, engine_agents: list[tuple[str, type]]) -> None:
        """
        Validates MRO hardening - SovereignBaseAgent must be in the chain.
        """
        failures = []

        for cls_name, cls in engine_agents:
            mro_names = [c.__name__ for c in cls.__mro__]

            # CHECK: SovereignBaseAgent must be in MRO
            if "SovereignBaseAgent" not in mro_names:
                failures.append(f"❌ {cls_name} MRO does not include SovereignBaseAgent! MRO: {mro_names}")

        if failures:
            pytest.fail("\n".join(failures))

    def test_mutable_defaults_purge(self) -> None:
        """
        Scans source code for dangerous mutable defaults.
        Looks for patterns like: list=[], dict={}, set=()
        """
        engine_path = Path("apps_rg/engines")
        unsafe_patterns = [
            (r":\s*list\s*=\s*\[\]", "list=[]"),
            (r":\s*dict\s*=\s*\{\}", "dict={}"),
            (r":\s*set\s*=\s*set\(\)", "set=()"),
            (r":\s*List\s*=\s*\[\]", "List=[]"),
            (r":\s*Dict\s*=\s*\{\}", "Dict={}"),
            (r":\s*Set\s*=\s*set\(\)", "Set=()"),
        ]

        violations = []

        for f in engine_path.glob("*.py"):
            if f.name == "__init__.py":
                continue

            content = f.read_text(encoding="utf-8")

            # Check for unsafe patterns
            for pattern, description in unsafe_patterns:
                import re

                matches = re.finditer(pattern, content)
                for match in matches:
                    # Ensure it's not using field(default_factory=...)
                    line_start = content.rfind("\n", 0, match.start()) + 1
                    line_end = content.find("\n", match.end())
                    line = content[line_start:line_end]

                    if "field(default_factory" not in line:
                        violations.append(
                            f"❌ {f.name}: Mutable default detected: {description}\n   Line: {line.strip()}"
                        )

        if violations:
            pytest.fail("\n".join(violations))

    def test_swarm_boot(self, engine_agents: list[tuple[str, type]]) -> None:
        """
        Attempt to initialize every agent found.
        Ensures __post_init__ logic is sound and security boot completes.
        """
        failures = []
        skipped = []

        for cls_name, cls in engine_agents:
            try:
                # Attempt default init
                agent = cls()

                # Verify security initialization
                if hasattr(agent, "_initialized"):
                    if not agent._initialized:
                        failures.append(
                            f"❌ {cls_name} failed security boot! _initialized={agent._initialized}"
                        )
                else:
                    # RGAgentBase inherits from SovereignBaseAgent which should have _initialized
                    pass  # Some agents may not expose this directly

            except TypeError as e:
                # Skip if requires mandatory args
                if "required positional argument" in str(e) or "missing" in str(e):
                    skipped.append(f"⚠️ Skipped boot test for {cls_name} (mandatory args)")
                else:
                    failures.append(f"❌ {cls_name} boot failed: {e}")
            except Exception as e:
                failures.append(f"❌ {cls_name} boot failed with exception: {e}")

        # Print skipped for visibility
        if skipped:
            print("\n".join(skipped))

        if failures:
            pytest.fail("\n".join(failures))

    def test_type_hints_present(self, engine_agents: list[tuple[str, type]]) -> None:
        """
        Validates that agents have type hints on their methods.
        Checks for __post_init__ and execute methods.
        """
        failures = []

        for cls_name, cls in engine_agents:
            # Check __post_init__ if present
            if hasattr(cls, "__post_init__"):
                method = cls.__post_init__
                sig = inspect.signature(method)

                # Should have return type hint
                if sig.return_annotation == inspect.Signature.empty:
                    failures.append(f"⚠️ {cls_name}.__post_init__ missing return type hint")

            # Check execute if present
            if hasattr(cls, "execute"):
                method = cls.execute
                sig = inspect.signature(method)

                # Should have return type hint
                if sig.return_annotation == inspect.Signature.empty:
                    failures.append(f"⚠️ {cls_name}.execute missing return type hint")

        # This is a warning test, not a hard failure
        if failures:
            print("\n".join(failures))

    def test_heal_repository_signature(self, engine_agents: list[tuple[str, type]]) -> None:
        """
        Validates that heal_repository methods have standard signature.
        """
        failures = []

        for cls_name, cls in engine_agents:
            if hasattr(cls, "heal_repository"):
                method = cls.heal_repository
                sig = inspect.signature(method)

                # Check for standard parameters
                params = list(sig.parameters.keys())

                # Should have at least: self, dry_run, execute
                if "dry_run" not in params:
                    failures.append(f"⚠️ {cls_name}.heal_repository missing 'dry_run' parameter")

                if "execute" not in params:
                    failures.append(f"⚠️ {cls_name}.heal_repository missing 'execute' parameter")

        # This is a warning test
        if failures:
            print("\n".join(failures))

    def test_no_legacy_imports(self) -> None:
        """
        Validates that engine files don't import legacy base classes directly.
        """
        engine_path = Path("apps_rg/engines")
        legacy_imports = [
            "from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin",
            "from agentic_core.base_agents.healer_mixin import HealerMixin",
            "from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin",
        ]

        violations = []

        for f in engine_path.glob("*.py"):
            if f.name == "__init__.py":
                continue

            content = f.read_text(encoding="utf-8")

            for legacy_import in legacy_imports:
                if legacy_import in content:
                    violations.append(f"❌ {f.name}: Legacy import detected:\n   {legacy_import}")

        if violations:
            pytest.fail("\n".join(violations))

    def test_agent_count(self, engine_agents: list[tuple[str, type]]) -> None:
        """
        Validates that we found a reasonable number of agents.
        This is a sanity check to ensure the discovery mechanism works.
        """
        agent_count = len(engine_agents)

        # We should have at least 10 agents after migration
        assert agent_count >= 10, (
            f"Expected at least 10 agents, found {agent_count}. Discovery mechanism may be broken."
        )

        print(f"\n✅ Discovered {agent_count} agents in apps_rg/engines")
        for cls_name, _ in engine_agents:
            print(f"   - {cls_name}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
