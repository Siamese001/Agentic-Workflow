"""
Test Suite for InfrastructureMixin

Verifies the Method Resolution Order (MRO) and state aggregation
of the consolidated InfrastructureMixin (Opportunity #4).
"""

from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.infrastructure_mixin import InfrastructureMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin


class ConcreteInfrastructureAgent(InfrastructureMixin):
    """
    Concrete implementation of InfrastructureMixin for testing purposes.
    """

    def __init__(self):
        super().__init__()
        self.name = "TestInfrastructureAgent"


class TestInfrastructureMixin:
    """
    Verifies the Method Resolution Order (MRO) and state aggregation
    of the consolidated InfrastructureMixin.
    """

    def test_mro_resolution(self):
        """
        Crucial: Verifies that InfrastructureMixin correctly inherits from
        HealerMixin, MCPHardenedMixin, and SubatomicTestingMixin in the correct order.
        """
        mro = ConcreteInfrastructureAgent.__mro__

        # Verify presence
        assert InfrastructureMixin in mro
        assert HealerMixin in mro
        assert MCPHardenedMixin in mro
        assert SubatomicTestingMixin in mro

        # Verify order (InfrastructureMixin should be before its parents)
        infra_idx = mro.index(InfrastructureMixin)
        assert mro.index(HealerMixin) > infra_idx
        assert mro.index(MCPHardenedMixin) > infra_idx
        assert mro.index(SubatomicTestingMixin) > infra_idx

    def test_verify_state_aggregation(self):
        """
        Verifies that verify_state() returns a value (dict or bool).
        """
        agent = ConcreteInfrastructureAgent()

        state = agent.verify_state()

        # verify_state may return dict or bool depending on implementation
        assert state is not None

    def test_initialization_chain(self):
        """
        Ensure initializing the class doesn't crash and sets up basic attributes.
        """
        agent = ConcreteInfrastructureAgent()
        assert agent.name == "TestInfrastructureAgent"

    def test_healer_mixin_methods_available(self):
        """
        Verify methods from HealerMixin are exposed.
        """
        agent = ConcreteInfrastructureAgent()
        # HealerMixin provides heal_repository
        assert hasattr(agent, "heal_repository")

    def test_mcp_hardened_methods_available(self):
        """
        Verify MCPHardenedMixin is in the MRO.
        """
        agent = ConcreteInfrastructureAgent()
        # MCPHardenedMixin should be in MRO
        assert MCPHardenedMixin in type(agent).__mro__

    def test_subatomic_testing_methods_available(self):
        """
        Verify SubatomicTestingMixin is in the MRO.
        """
        agent = ConcreteInfrastructureAgent()
        # SubatomicTestingMixin should be in MRO
        assert SubatomicTestingMixin in type(agent).__mro__

    def test_mro_ends_with_object(self):
        """
        Verify MRO terminates correctly with object.
        """
        mro = ConcreteInfrastructureAgent.__mro__
        assert mro[-1] is object
