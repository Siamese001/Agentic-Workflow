from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "artifact_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "artifact_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "artifact_types")

"Dataclass models for orchestrate_workflow_types."
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

_logger = logging.getLogger(__name__)


@dataclass
class Artifact:
    """A workflow Artifact (file)."""

    _id: str
    _path: Path
    _hash: str
    _is_ready: bool = False
    _is_static: bool = False


@dataclass
class HopCheckpoint:
    """Checkpoint for a completed hop."""

    _hop_id: str
    _status: HopStatus
    _start_time: datetime
    _end_time: datetime | None = None
    _output_artifacts: list[str] = field(default_factory=list)
    _error_message: str | None = None


@dataclass
class ValidationResult:
    """Result from a validation gate."""

    _gate_id: str
    _decision: GateDecision
    _message: str
    _details: dict[str, object] = field(default_factory=dict)
