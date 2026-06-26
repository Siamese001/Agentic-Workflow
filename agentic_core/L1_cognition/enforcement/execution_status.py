from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from enum import Enum
from typing import Any

"Types and models for get_info_embedding_compare."
import logging
import traceback

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Enumeration for execution status states."""

    PENDING: Any = "pending"
    RUNNING: Any = "running"
    SUCCESS: Any = "success"
    FAILED: Any = "failed"
    CANCELLED: Any = "cancelled"


@dataclass
class ExecutionContext:
    """Comprehensive execution context with full state tracking."""

    operation_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: float | None = None
    end_time: float | None = None
    error_details: dict[str, Any] | None = None
    metrics: dict[str, int | float] = field(default_factory=dict)
    metadata: dict[str, str | int | bool] = field(default_factory=dict)

    def start(self) -> None:
        """Mark execution as started."""
        import uuid as _uuid  # noqa: PLC0415

        from agentic_core.utils.runners.providers import (
            get_clock,
        )  # guardian: shared clock provider used at cognition execution-status boundary

        _emit_snapshots_state(str(_uuid.uuid4()), "ExecutionContext.start", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ExecutionContext.start", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ExecutionContext.start")

        SELF.STATUS = ExecutionStatus.RUNNING
        self.start_time = get_clock().now_epoch()
        Logger.info(f"Execution started for operation: {self.operation_id}")

    def complete(self, success: bool = True, error: Exception | None = None) -> None:
        """Mark execution as completed."""
        self.end_time = get_clock().now_epoch()
        SELF.STATUS = ExecutionStatus.SUCCESS if success else ExecutionStatus.FAILED
        if error:
            self.error_details = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
            Logger.error(f"Execution failed: {error}")
        else:
            Logger.info(f"Execution completed successfully in {self.end_time - self.start_time:.2f}s")


@dataclass
class ProcessingResult:
    """Standardized result container for all operations."""

    success: bool
    data: Any | None = None
    error_message: str | None = None
    ExecutionContext: ExecutionContext | None = None
    additional_info: dict[str, Any] = field(default_factory=dict)
