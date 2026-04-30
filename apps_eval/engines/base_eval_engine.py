"""
Base Eval Engine — Foundation for all apps_eval engines.

Mirrors apps_exec BaseExecEngine pattern with eval-specific contracts.
"""
# guardian: allow-silent-degradation -- Evaluation engine requires exception handling

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from abc import ABC, abstractmethod
from typing import Any

try:
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
except ImportError:  # guardian: allow-silent-swallow -- Optional semantic cache mixin

    class SemanticCacheMixin:  # type: ignore[no-redef]
        pass


try:
    from agentic_core.mixins.embedding_mixin import EmbeddingMixin
except ImportError:  # guardian: allow-silent-swallow -- Optional embedding mixin

    class EmbeddingMixin:  # type: ignore[no-redef]
        pass


from agentic_core.L0_routing.config.model_registry import QWEN_LOCAL_MODEL_ID

try:
    from agentic_core.L3_orchestration.inference.qwen_vllm import (
        AppsQwenGateway,
        AppsQwenRequest,
        apps_qwen_telemetry,
    )
except ImportError:  # guardian: allow-silent-swallow -- Optional Qwen integration
    # Fallback for environments without Qwen integration
    AppsQwenGateway = None  # type: ignore[assignment]
    AppsQwenRequest = None  # type: ignore[assignment]
    apps_qwen_telemetry = None  # type: ignore[assignment]


_log = logging.getLogger(__name__)


class BaseEvalEngine(SemanticCacheMixin, EmbeddingMixin, ABC):
    """Abstract base for all Evaluation Lab engines.

    Provides:
    - Standard logging interface
    - Specs and toggle loading
    - Provenance metadata injection
    - Dry-run protocol
    """

    AGENT_ID: str = ""

    def __init__(self, config: Any = None, **kwargs: Any) -> None:
        self.config = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True
        self._semantic_namespace = "apps_eval"

        # Initialize Qwen gateway if available
        self._qwen_gateway = None
        self._qwen_session_id = None
        if AppsQwenGateway is not None:
            self._qwen_gateway = AppsQwenGateway()
            if apps_qwen_telemetry is not None:
                self._qwen_session_id = apps_qwen_telemetry.start_session("apps_eval")

        try:
            from apps_eval.config.agent_spec_config import load_eval_specs

            self.specs = load_eval_specs()
        except ImportError:  # guardian: allow-silent-swallow -- Optional eval specs
            self.specs = None
            self.logger.warning("[%s] eval specs not available", self.name)

        try:
            from apps_eval.config.reasoning_toggles_config import DEFAULT_TOGGLES

            self.toggles = DEFAULT_TOGGLES
        except ImportError:  # guardian: allow-silent-swallow -- Optional reasoning toggles
            self.toggles = None

    @abstractmethod
    @traces_execute(layer="L3_ORCHESTRATION")
    def execute(self, input_data: Any) -> Any:
        """Main execution method — must be implemented by subclasses."""

    async def evaluate_with_qwen(self, prompt: str, template: str = "code_review") -> dict[str, Any]:
        """Evaluate using Qwen v2.5 vLLM inference.

        Args:
            prompt: Evaluation prompt text
            template: Prompt template to use

        Returns:
            Evaluation result dictionary
        """
        if self._qwen_gateway is None:
            return {
                "success": False,
                "error": "Qwen gateway not available",
                "response": None,
            }

        if apps_qwen_telemetry is None or self._qwen_session_id is None:
            return {
                "success": False,
                "error": "Qwen session not initialized",
                "response": None,
            }

        try:
            request = AppsQwenRequest(
                app_name="apps_eval",
                prompt=prompt,
                confidence_threshold=0.7,
                max_tokens=1536,
                temperature=0.05,
            )

            apps_qwen_telemetry.record_request_start(
                session_id=self._qwen_session_id,
                app_name="apps_eval",
                model_id=QWEN_LOCAL_MODEL_ID,
            )

            response = await self._qwen_gateway.infer(request)

            token_estimate = len(prompt.split()) + (
                len(response.response.split()) if response.response else 0
            )
            if response.success:
                apps_qwen_telemetry.record_request_success(
                    session_id=self._qwen_session_id,
                    app_name="apps_eval",
                    model_id=response.model_used,
                    latency_ms=response.latency_ms,
                    confidence=response.confidence,
                    tokens_used=token_estimate,
                )
            else:
                apps_qwen_telemetry.record_request_error(
                    session_id=self._qwen_session_id,
                    app_name="apps_eval",
                    model_id=response.model_used,
                    error_message=response.error_message or "unknown_error",
                )

            return {
                "success": response.success,
                "response": response.response,
                "confidence": response.confidence,
                "model_used": response.model_used,
                "latency_ms": response.latency_ms,
                "error_message": response.error_message,
            }

        except (RuntimeError, ValueError, TypeError, AttributeError, ConnectionError, TimeoutError) as e:
            self.logger.error(f"Qwen evaluation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
            }

    def record_fail(self, message: str, *, signal: str = "", data: dict | None = None) -> None:
        self.logger.warning("FAIL [%s]: %s", self.name, message)

    def record_pass(self, message: str, *, data: dict | None = None) -> None:
        self.logger.info("PASS [%s]: %s", self.name, message)

    def get_status(self) -> dict[str, Any]:
        return {
            "engine": self.name,
            "initialized": self._initialized,
            "specs_available": self.specs is not None,
        }


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_eval.engines.base_eval_engine', "module_loaded")
