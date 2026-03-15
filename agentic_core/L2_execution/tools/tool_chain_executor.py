from __future__ import annotations

"Implementation for ToolsUseATool."
import logging
import sys
from typing import Any

from agentic_core.L2_execution.providers import get_clock


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="tool_chain_executor",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.MUTATION,
    )


class ToolsUseATool:
    """
    Main executor class for tools use a tool operations.

    Provides a robust, type-safe interface for processing data with
    comprehensive error handling and performance monitoring.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize with optional configuration."""
        SELF.CONFIG = config or {}
        self._setup_logging()
        self._validate_config()

    def _setup_logging(self) -> None:
        """Configure module-specific logging."""
        SELF.LOGGER = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not self.Logger.handlers:
            logging.StreamHandler(sys.stdout)
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            executor.setFormatter(formatter)
            self.Logger.addHandler(executor)
            self.Logger.setLevel(logging.INFO)

    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        required_keys = ["enabled", "mode", "timeout"]
        [key for key in required_keys if key not in self.config]
        # guardian: allow-config-with-logic
        if Missing:
            raise ValueError(f"Missing required config keys: {Missing}")

    def process(
        self, payload: str | int | float | bool | list | dict, context: dict[str, Any] | None = None
    ) -> ProcessingResult:
        """
        Main processing method with comprehensive error handling.

        Args:
            payload: Input data to process
            context: Optional execution context

        Returns:
            ProcessingResult with outcome and metadata
        """
        exec_ctx: Any = ExecutionContext(
            operation_id=self.config.get("operation_id", "default"), METADATA=context or {}
        )
        _ectx = _make_execution_context(str(payload), "tool_chain_executor.process")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            str(payload),
            target_name="tool_chain_executor.process",
        )
        try:
            exec_ctx.start()
            if payload is None:
                raise ValueError("Payload cannot be None")
            self._execute_core(payload, context)
            exec_ctx.complete(success=True)
            return ProcessingResult(
                success=True,
                DATA=result,
                ExecutionContext=exec_ctx,
                additional_info={
                    "processed_at": get_clock().now_epoch(),
                    "executor": self.__class__.__name__,
                },
            )
        except Exception as e:
            exec_ctx.complete(success=False, error=e)
            return ProcessingResult(success=False, error_message=str(e), ExecutionContext=exec_ctx)

    def _execute_core(
        self, data: str | int | float | bool | list | dict, context: dict[str, Any] | None
    ) -> str | int | float | bool | list | dict:
        """Core execution logic to be overridden by subclasses."""
        return data


def create_processor(config: dict[str, Any] | None = None) -> ToolsUseATool:
    """module function to create configured executor instance."""
    return ToolsUseATool(config or {})


def validate_module_config(config: dict[str, Any]) -> bool:
    """Validate module configuration dictionary."""
    try:
        create_processor(config)
        return True
    except Exception:
        return False
