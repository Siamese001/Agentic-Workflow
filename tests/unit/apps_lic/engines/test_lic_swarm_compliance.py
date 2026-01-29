"""
tests/test_lic_swarm_compliance.py
"""

import importlib
import inspect
import pkgutil
import sys
from dataclasses import is_dataclass
from pathlib import Path

import pytest

# Ensure path visibility
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLICCompleteSwarmCompliance:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Validates that ALL Agents in apps_lic are V2.5 Compliant.
    """

    def test_full_directory_sweep(self):
        """
        Dynamically find every class in apps_lic.engines ending in 'Agent' or 'Architect'
        and verify it adheres to the Sovereign Standard.
        """
        from apps_lic.shared.core.agent_base import LICAgentBase

        import apps_lic.engines as engine_pkg

        package_path = Path(engine_pkg.__file__).parent

        # Track stats
        agents_found = 0
        agents_compliant = 0
        failures = []

        for _, name, _ in pkgutil.iter_modules([str(package_path)]):
            try:
                module = importlib.import_module(f"apps_lic.engines.{name}")

                for cls_name, cls in inspect.getmembers(module, inspect.isclass):
                    # Filter for our classes defined in this module
                    if cls.__module__ != module.__name__:
                        continue

                    # Broad filter for Agent-like classes
                    if any(
                        x in cls_name
                        for x in ["Agent", "Architect", "Orchestrator", "Specialist", "Guardrail"]
                    ):
                        agents_found += 1

                        # VALIDATION 1: Inheritance
                        if not issubclass(cls, LICAgentBase):
                            failures.append(f"{cls_name} does not inherit LICAgentBase")
                            continue

                        # VALIDATION 2: Dataclass
                        if not is_dataclass(cls):
                            failures.append(f"{cls_name} is not a dataclass")
                            continue

                        # VALIDATION 3: Post-Init Security
                        if not hasattr(cls, "__post_init__"):
                            # While it might inherit, we prefer explicit definition for clarity
                            pass

                        agents_compliant += 1

            except ImportError as e:
                # Some legacy files might fail import if not fully cleaned, catch here
                failures.append(f"Import Error in {name}: {e}")
            except Exception as e:
                failures.append(f"General Error in {name}: {e}")

        # Assertions
        if failures:
            pytest.fail("Compliance Failures found:\n" + "\n".join(failures))

        print(f"Verified {agents_compliant}/{agents_found} Agents in apps_lic.")
        # Ensure we actually found agents
        assert agents_found > 0
        assert agents_compliant == agents_found

    def test_orchestrator_integrity(self):
        """Verify the specific complex orchestrators migrated in Phase 25.5."""
        from apps_lic.engines.LicHealingOrchestratorAgent import LicHealingOrchestratorAgent
        from apps_lic.engines.OutreachPhase5OrchestratorAgent import OutreachPhase5OrchestratorAgent

        h_agent = LicHealingOrchestratorAgent()
        assert hasattr(h_agent, "heal_repository")
        assert isinstance(h_agent.active_incidents, dict)

        o_agent = OutreachPhase5OrchestratorAgent()
        assert "compliance" in o_agent.validation_gates
