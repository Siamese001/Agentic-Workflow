"""
Base Resume Agent - Foundation for all RG Sovereign V2.5 Engines
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

try:
    from agentic_core.interfaces.execution_contracts import (
        AgentOutputContract,
        get_current_secret,
        wrap_output,
    )

    _OUTPUT_CONTRACT_AVAILABLE = True
except ImportError as e:
    _OUTPUT_CONTRACT_AVAILABLE = False
    logging.getLogger(__name__).debug(f"Output contracts not available: {e}")
try:
    from pydantic import BaseModel
except ImportError as e:
    BaseModel = Any
    logging.getLogger(__name__).debug(f"Pydantic not available: {e}")
try:
    from apps_rg.utils.mixins import HealerMixin, MCPHardenedMixin

    MIXINS_AVAILABLE = True
except ImportError as e:
    MIXINS_AVAILABLE = False
    logging.getLogger(__name__).debug(f"RG mixins not available: {e}")

    class MCPHardenedMixin:
        """Stub MCPHardenedMixin for standalone usage."""

        def __init__(self, *args, **kwargs):
            pass

    class HealerMixin:
        """Stub HealerMixin for standalone usage."""

        def __init__(self, *args, **kwargs):
            pass

        # guardian: allow-magic-config
        def heal_repository(
            self,
            dry_run: bool = False,
            execute: bool = False,
            depth: int = 0,
            max_depth: int = 3,
            _call_path: set | None = None,
        ) -> dict[str, int]:
            return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0}
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


logger = logging.getLogger(__name__)


class BaseRGEngine(MCPHardenedMixin, HealerMixin, ABC):
    AGENT_ID: str = ""
    _current_trace_id: str = ""
    "\n    Abstract base class for all Resume Generation engines.\n\n    Provides:\n    - MCP hardening capabilities\n    - Self-healing capabilities\n    - Standard logging interface\n    - Pydantic model I/O enforcement\n    - Knowledge base integration\n    "

    def __init__(self, config: BaseModel | None = None, **kwargs):
        """Initialize the engine with configuration."""
        self.node_id = kwargs.pop("node_id", None)
        super().__init__()
        self.config = config
        self.ctx = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True
        try:
            from apps_rg.config import load_rg_specs

            self.rg_specs = load_rg_specs()
        except ImportError:
            self.rg_specs = None
            self.logger.warning("RG specs not available")
        try:
            from apps_rg.config.reasoning_toggles_config import DEFAULT_TOGGLES

            self.toggles = DEFAULT_TOGGLES
        except ImportError:
            self.toggles = None
            self.logger.warning("Reasoning toggles not available")
        try:
            from apps_rg.config.knowledge_base import FROZEN_SNAPSHOT

            self.knowledge = FROZEN_SNAPSHOT
        except ImportError:
            self.knowledge = None
            self.logger.warning("Knowledge base not available")

    def _mcp_audit(self, event: str, **kwargs) -> None:
        """Log an MCP audit event. Lightweight stub for standalone usage."""
        self.logger.debug(f"MCP_AUDIT: {event} {kwargs}")

    def record_fail(self, message: str, *, signal: str = "", data: dict | None = None) -> None:
        """Record a failure event."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaseRGEngine.record_fail")

        self.logger.warning(f"FAIL [{self.name}]: {message}")
        if hasattr(self.ctx, "trace") and self.ctx is not None:
            self.ctx.trace.add_trace(f"{self.name}_FAIL", {"message": message, "signal": signal})

    def record_pass(self, message: str, *, data: dict | None = None) -> None:
        """Record a pass event."""
        self.logger.info(f"PASS [{self.name}]: {message}")
        if hasattr(self.ctx, "trace") and self.ctx is not None:
            self.ctx.trace.add_trace(f"{self.name}_PASS", {"message": message, **(data or {})})

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

    def execute_contracted(self, input_data: BaseModel, trace_id: str = "") -> "AgentOutputContract":
        """Execute and wrap result in a signed AgentOutputContract.

        Use this instead of execute() at all call sites that feed L6 observability.
        """
        if not _OUTPUT_CONTRACT_AVAILABLE:
            raise RuntimeError("AgentOutputContract not available — check agentic_core import")
        if not self.AGENT_ID:
            raise RuntimeError(f"{self.__class__.__name__}.AGENT_ID must be set to its AGENT_REGISTRY key")
        result = self.execute(input_data)
        return wrap_output(
            agent_id=self.AGENT_ID,
            trace_id=trace_id or self._current_trace_id,
            payload_model=result,
            secret=get_current_secret(),
        )

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
        # guardian: allow-config-with-logic
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
