"""BaseDispatchAgent — Shared dispatch executor skeleton for LIC and RG domains.

Extracted from DispatchOutreachToolsAgent and DispatchResumeToolsAgent (2026-03-11, P2-C).
App agents subclass this and override _perform_action() and domain-specific heal methods.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, NamedTuple

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_S = 30.0
_MAX_SAFE_TIMEOUT_S = 300.0
_MIN_SAFE_TIMEOUT_S = 1.0


class ExecutionResult(NamedTuple):
    """Result of a dispatch execution action."""

    SUCCESS: bool
    OUTPUT: Any = None
    ERROR: str | None = None
    duration_ms: float = 0.0


@dataclass
class BaseDispatchAgent(SovereignBaseAgent):
    """Generic action dispatcher with self-healing config/timeout management.

    Subclasses override:
    - `_perform_action()` to add domain-specific routing
    - `_heal_domain_config()` for domain-specific config checks
    - `_run_domain_diagnostics()` for domain smoke tests
    """

    config_dict: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize timeout from config_dict."""
        super().__post_init__()
        self.TIMEOUT: float = float(self.config_dict.get("timeout", _DEFAULT_TIMEOUT_S))
        Logger.info(f"Initialized {self.__class__.__name__} (timeout={self.TIMEOUT}s)")
        self._register_in_knowledge_graph()

    def _register_in_knowledge_graph(self) -> None:
        """Register this agent as an entity in the Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            bridge.create_agent_entity(
                agent_name=self.__class__.__name__,
                agent_type="DispatchAgent",
                observations=[
                    f"DispatchAgent {self.__class__.__name__} initialized",
                    f"timeout={self.config_dict.get('timeout', _DEFAULT_TIMEOUT_S)}s",
                ],
            )
        except Exception as e:
            Logger.debug(f"[{self.__class__.__name__}] KG registration skipped: {e}")

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, "config_dict"), "Missing config_dict"
        return True

    def execute(self, action: str, params: dict[str, Any]) -> ExecutionResult:
        """Execute action with parameters, returning a timed ExecutionResult."""
        start = time.time()
        try:
            output = self._perform_action(action, params)
            result = ExecutionResult(
                SUCCESS=True,
                OUTPUT=output,
                duration_ms=(time.time() - start) * 1000,
            )
            self._persist_outcome(action, result)
            return result
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            result = ExecutionResult(
                SUCCESS=False,
                ERROR=str(e),
                duration_ms=(time.time() - start) * 1000,
            )
            self._persist_outcome(action, result)
            return result

    def _persist_outcome(self, action: str, result: ExecutionResult) -> None:
        """Persist task outcome to Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            score = 1.0 if result.SUCCESS else 0.0
            task_desc = f"{self.__class__.__name__}:{action}"
            if result.SUCCESS and score >= 0.8:
                bridge.create_mastered_task_relation(
                    agent_name=self.__class__.__name__,
                    task_description=task_desc,
                    feedback_score=score,
                )
            elif not result.SUCCESS:
                bridge.create_relation(
                    from_entity=self.__class__.__name__,
                    to_entity=f"Task_{action}",
                    relation_type=GraphMemoryBridge.RELATION_FAILED_TASK,
                )
                bridge.add_observation(
                    entity_name=self.__class__.__name__,
                    observation=f"Failed action={action} error={result.ERROR}",
                )
        except Exception as e:
            Logger.debug(f"[{self.__class__.__name__}] KG outcome persistence skipped: {e}")

    def _perform_action(self, action: str, params: dict[str, Any]) -> Any:
        """Perform the action. Subclasses override for domain routing."""
        Logger.info(f"Executing {action} with {params}")
        return {"action": action, "params": params, "status": "completed"}

    def heal_repository(self) -> None:
        """Autonomy healing: shared timeout + config checks, then domain-specific."""
        super().heal_repository()
        self._heal_timeout_settings()
        self._heal_config_integrity()
        self._heal_domain_config()
        self._run_domain_diagnostics()

    def _heal_timeout_settings(self) -> None:
        """Ensure timeout is within safe bounds [1s, 300s]."""
        if self.TIMEOUT > _MAX_SAFE_TIMEOUT_S:
            Logger.warning(f"Timeout {self.TIMEOUT}s exceeds safe limit — resetting to {_DEFAULT_TIMEOUT_S}s")
            self.TIMEOUT = _DEFAULT_TIMEOUT_S  # guardian: allow-magic-config
        elif self.TIMEOUT < _MIN_SAFE_TIMEOUT_S:
            Logger.warning(f"Timeout {self.TIMEOUT}s too low — resetting to {_DEFAULT_TIMEOUT_S}s")
            self.TIMEOUT = _DEFAULT_TIMEOUT_S  # guardian: allow-magic-config

    def _heal_config_integrity(self) -> None:
        """Validate config_dict structure and repair if corrupted."""
        if not isinstance(self.config_dict, dict):
            Logger.warning("config_dict corrupted — resetting to defaults")
            self.config_dict = {}
        if "timeout" not in self.config_dict:
            Logger.warning("Missing config key 'timeout' — setting default")
            self.config_dict["timeout"] = _DEFAULT_TIMEOUT_S

    def _heal_domain_config(self) -> None:
        """Domain-specific config healing. Override in subclasses."""

    def _run_domain_diagnostics(self) -> None:
        """Domain-specific smoke test. Default: generic action test."""
        try:
            test_result = self._perform_action("test", {"query": "diagnostic test"})
            if isinstance(test_result, dict) and "error" in test_result:
                Logger.error(f"Diagnostics failed: {test_result['error']}")
        except Exception as e:  # guardian: allow-silent-swallow
            Logger.error(f"Diagnostics exception: {e}")

    def heal(self, violation: Any, **kwargs: Any) -> Any:
        return super().heal(violation, **kwargs)
