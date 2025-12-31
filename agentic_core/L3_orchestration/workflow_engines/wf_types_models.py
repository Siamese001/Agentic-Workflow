"""Dataclass models for orchestrate_workflow_types."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)
# from agentic_core.orchestrate_workflow_types_enums import *  # Star import removed


@dataclass
# NAMING FIXED: Artifact → artifact
class artifact:
    """A workflow artifact (file)."""

    _id: str
    _path: Path
    _hash: str
    _is_ready: bool = False
    _is_static: bool = False


@dataclass
# NAMING FIXED: HopCheckpoint → hop_checkpoint
class hop_checkpoint:
    """Checkpoint for a completed hop."""

    _hop_id: str
    _status: HopStatus
    _start_time: datetime
    _end_time: Optional[datetime] = None
    _output_artifacts: List[str] = field(default_factory=list)
    _error_message: Optional[str] = None


@dataclass
# NAMING FIXED: ValidationResult → validation_result
class validation_result:
    """Result from a validation gate."""

    _gate_id: str
    _decision: GateDecision
    _message: str
    _details: Dict[str, object] = field(default_factory=dict)
