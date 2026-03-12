"""

infrastructure_mixin - Unified Gatekeeper for Agent Infrastructure



L0 DNA FLATTENING (Jan 2026):

This mixin consolidates all core agent capabilities into a single inheritance point:

- HealerMixin (autonomous repair)

- MCPHardenedMixin (MCP protocol safety)

- SubatomicTestingMixin (self-testing)

- instructional_injection_mixin (prompt injection protection - now L0 core trait)



Ensures proper initialization order and provides state verification to catch "silent failure" bugs.



USAGE:



    class MyAgent(infrastructure_mixin):

        def __init__(self, project_root: Path):

            super().__init__()  # CRITICAL: Must call super().__init__()

            self.project_root = project_root

            self.verify_state()  # Optional: Verify initialization succeeded



SSOT PRINCIPLE:

    Agents should inherit from infrastructure_mixin instead of individual mixins.

    This ensures consistent MRO and prevents initialization bugs.



HARDENING:

    The verify_state() method will raise RuntimeError if initialization failed,

    preventing silent failures that lead to hard-to-debug issues.

"""
from __future__ import annotations
import logging
from typing import Any
from agentic_core.mixins.context_management_mixin import ContextManagementMixin
from agentic_core.mixins.cost_mixin import CostGuardrailMixin
from agentic_core.mixins.healer_mixin import HealerMixin
from agentic_core.mixins.hitl_mixin import HITLMixin
from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.mixins.performance_mixin import PerformanceMixin
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.mixins.tool_reliability_mixin import ToolReliabilityMixin
from agentic_core.mixins.tracing_mixin import TracingMixin
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class InfrastructureMixin(CostGuardrailMixin, ContextManagementMixin, ToolReliabilityMixin, HITLMixin, PerformanceMixin, HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, TracingMixin):
    """

    Unified infrastructure mixin combining all standard agent capabilities.



    This mixin provides:

    1. Cost guardrails (CostGuardrailMixin) [PHASE 1 Jan 2026]

    2. Context management (ContextManagementMixin) [PHASE 1 Jan 2026]

    3. Tool reliability (ToolReliabilityMixin) [PHASE 2 Feb 2026]

    4. Human-in-the-loop (HITLMixin) [PHASE 3 Feb 2026]

    5. Performance optimization (PerformanceMixin) [PHASE 4 Feb 2026]

    7. Healing capabilities (HealerMixin)

    8. MCP hardening (MCPHardenedMixin)

    9. Subatomic testing (SubatomicTestingMixin)

    10. Distributed tracing (TracingMixin) [PHASE 2 Feb 2026]

    11. State verification to catch initialization failures



    MRO Order (L0 DNA Flattening):

        ConcreteAgent -> infrastructure_mixin -> CostGuardrailMixin ->

        ContextManagementMixin -> ToolReliabilityMixin -> HITLMixin ->

        PerformanceMixin -> HealerMixin ->

        MCPHardenedMixin -> SubatomicTestingMixin -> TracingMixin -> object



    Critical Requirements:

        - Subclasses MUST call super().__init__() in their __init__

        - Failure to do so will cause verify_state() to raise RuntimeError

    """
    _infra_initialized: bool = False

    def __init__(self) -> None:
        """

        Initialize all infrastructure components.



        This method MUST be called by subclasses via super().__init__().

        Failure to call this will leave _infra_initialized as False,

        causing verify_state() to raise RuntimeError.

        """
        super().__init__()
        self._infra_initialized = True
        Logger.debug(f'[INFRA] {self.__class__.__name__} infrastructure initialized')

    def verify_state(self) -> bool:
        """

        Verify that infrastructure was properly initialized.



        This method checks for common initialization failures:

        1. _infra_initialized flag not set (super().__init__() not called)

        2. _healer_metrics missing (HealerMixin not initialized)

        3. _mcp_initialized missing (MCPHardenedMixin not initialized)



        Returns:

            True if all checks pass



        Raises:

            RuntimeError: If any initialization check fails



        Usage:

            class MyAgent(infrastructure_mixin):

                def __init__(self):

                    super().__init__()

                    self.verify_state()  # Ensure initialization succeeded

        """
        errors = []
        if not getattr(self, '_infra_initialized', False):
            errors.append(f'{self.__class__.__name__}: _infra_initialized is False. Did you forget to call super().__init__()?')
        if not hasattr(self, '_healer_metrics'):
            errors.append(f'{self.__class__.__name__}: _healer_metrics is missing. HealerMixin was not properly initialized.')
        if errors:
            error_msg = 'Infrastructure initialization failed:\n' + '\n'.join((f'  - {e}' for e in errors))
            Logger.error(f'[INFRA] {error_msg}')
            raise RuntimeError(error_msg)
        Logger.debug(f'[INFRA] {self.__class__.__name__} state verification passed')
        return True

    def get_infrastructure_status(self) -> dict[str, Any]:
        """

        Get the current status of all infrastructure components.



        Returns:

            Dictionary with component status:

                - infra_initialized (bool): Whether infrastructure is initialized

                - healer_ready (bool): Whether HealerMixin is ready

                - mcp_ready (bool): Whether MCPHardenedMixin is ready

                - testing_ready (bool): Whether SubatomicTestingMixin is ready

        """
        return {'infra_initialized': getattr(self, '_infra_initialized', False), 'healer_ready': hasattr(self, '_healer_metrics'), 'mcp_ready': hasattr(self, '_mcp_initialized'), 'testing_ready': hasattr(self, '_subatomic_initialized'), 'class_name': self.__class__.__name__}

    def reset_infrastructure(self) -> None:
        """

        Reset infrastructure state for re-initialization.



        This is useful for testing or when an agent needs to be

        re-initialized without creating a new instance.



        Warning: This should only be used in controlled scenarios.

        """
        self._infra_initialized = False
        if hasattr(self, '_healer_metrics'):
            self._healer_metrics = {'violations_found': 0, 'violations_fixed': 0, 'errors': 0}
        Logger.debug(f'[INFRA] {self.__class__.__name__} infrastructure reset')
__all__ = ['InfrastructureMixin']
infrastructure_mixin = InfrastructureMixin
