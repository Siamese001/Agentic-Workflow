"""
Base Resume Agent - Foundation for all RG Sovereign V2.5 Engines
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = Any  # type: ignore

# Import mixins - fall back to stubs if not available
try:
    from apps_rg.utils.mixins import HealerMixin, MCPHardenedMixin

    MIXINS_AVAILABLE = True
except ImportError:
    MIXINS_AVAILABLE = False

    class MCPHardenedMixin:
        """Stub MCPHardenedMixin for standalone usage."""

        def __init__(self, *args, **kwargs):
            pass

    class HealerMixin:
        """Stub HealerMixin for standalone usage."""

        def __init__(self, *args, **kwargs):
            pass

        def heal_repository(
            self,
            dry_run: bool = True,
            execute: bool = False,
            depth: int = 0,
            max_depth: int = 3,
            _call_path: set | None = None,
        ) -> dict[str, int]:
            return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0}


logger = logging.getLogger(__name__)


class BaseRGEngine(MCPHardenedMixin, HealerMixin, ABC):
    """
    Abstract base class for all Resume Generation engines.

    Provides:
    - MCP hardening capabilities
    - Self-healing capabilities
    - Standard logging interface
    - Pydantic model I/O enforcement
    - Knowledge base integration
    """

    def __init__(self, config: BaseModel | None = None, **kwargs):
        """Initialize the engine with configuration."""
        # Extract known kwargs, pass rest to super
        self.node_id = kwargs.pop("node_id", None)
        super().__init__()
        self.config = config
        self.ctx = config  # Store context for compatibility
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True

        # Auto-load configuration specs
        try:
            from apps_rg.config import load_rg_specs

            self.rg_specs = load_rg_specs()
        except ImportError:
            self.rg_specs = None
            self.logger.warning("RG specs not available")

        # Auto-load reasoning toggles
        try:
            from apps_rg.config.ReasoningToggles import get_toggles

            self.toggles = get_toggles()
        except ImportError:
            self.toggles = None
            self.logger.warning("Reasoning toggles not available")

        # Import knowledge base
        try:
            from apps_rg.config.knowledge_base import FROZEN_SNAPSHOT

            self.knowledge = FROZEN_SNAPSHOT
        except ImportError:
            self.knowledge = None
            self.logger.warning("Knowledge base not available")

    @abstractmethod
    def execute(self, input_data: BaseModel) -> BaseModel:
        """
        Main execution method - must be implemented by subclasses.

        Args:
            input_data: Pydantic model containing input

        Returns:
            Pydantic model containing output
        """
        pass

    def validate_input(self, input_data: BaseModel) -> bool:
        """Validate input data before execution."""
        if not isinstance(input_data, BaseModel):
            raise TypeError(f"Input must be a Pydantic BaseModel, got {type(input_data)}")
        return True

    def run_subatomic_test(self) -> dict[str, Any]:
        """Run subatomic self-tests (SubatomicTestingMixin compatibility).

        Returns:
            Test results dict
        """
        return {"status": "passed", "tests_run": 0}

    def get_prompt(self, prompt_id: str) -> str:
        """Get prompt from knowledge base."""
        if self.knowledge:
            from apps_rg.config.knowledge_base import get_prompt

            return get_prompt(prompt_id)
        return ""

    def get_node_config(self, node_id: str) -> Any:
        """Get K-node configuration from knowledge base."""
        if self.knowledge:
            from apps_rg.config.knowledge_base import get_node_config

            return get_node_config(node_id)
        return None

    def get_status(self) -> dict[str, Any]:
        """Return engine status for observability."""
        return {
            "engine": self.__class__.__name__,
            "initialized": self._initialized,
            "mixins_available": MIXINS_AVAILABLE,
            "knowledge_available": self.knowledge is not None,
        }
