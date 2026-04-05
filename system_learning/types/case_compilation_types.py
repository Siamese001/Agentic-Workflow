"""Case compilation types — pipeline stages for System Learning Step 4.

Defines the canonical types for compiling L2 sealed outputs into CaseRecord bundles:
  - CompilationInput      — Ingests L2 sealed outputs and context logs
  - CompilationStage      — Individual pipeline stage artifacts (capture/freeze/seal)
  - CompilationPayload    — Final master archive payload
  - CaseCompilationResult — Deterministic result with CaseRecord bundles

All types are frozen dataclasses with deterministic to_dict()/to_json()/stable_hash()
methods. No wall-clock reads; timestamps are caller-supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json
from system_learning.types.case_memory_types import ADGNodeRef, CaseRecord, PolicyHashRef

# ADG wiring for case compilation types
_emit_records_execution_trace("case_compilation_types", "p0", "case_compilation_trace")
_emit_applies_guardrail("p0", "case_compilation_types", "p0_governance")
emit_replay_key("p0", "case_compilation_types")
emit_determinism_digest("p0", "case_compilation_types")
_emit_writes_via_uwg("p2", "case_compilation_types", "uwg_write")
_emit_blocks_direct_write("p2", "case_compilation_types", "direct_write_block")
_emit_records_tool_invocation("p2", "case_compilation_types", "tool_invocation")
_emit_captures_execution_output("p2", "case_compilation_types", "exec_output")
_emit_dispatches_agent("p3", "case_compilation_types", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "case_compilation_types", "exec_plan")
_emit_routes_to_agent("p3", "case_compilation_types", "target_agent")
_emit_checks_agent_registry("p3", "case_compilation_types", "agent_registry")
_emit_validates_agent_capability("p3", "case_compilation_types", "capability")
_emit_verifies_policy("p3", "case_compilation_types", "policy_check")
_emit_verifies_boundary("p3", "case_compilation_types", "boundary_check")


# =============================================================================
# Shared leaf types
# =============================================================================


@dataclass(frozen=True)
class SealedOutputRef:
    """Reference to an L2 sealed output artifact.

    Attributes
    ----------
    trace_id:
        Source execution trace identifier.
    output_hash:
        SHA-256 of the ExecTrace & StateDiff sealed output.
    timestamp_utc:
        Unix timestamp when the output was sealed.
    adg_node:
        ADG node reference for the sealed output.
    """

    trace_id: str
    output_hash: str
    timestamp_utc: int
    adg_node: ADGNodeRef

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not self.output_hash:
            raise ValueError("output_hash must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "adg_node": self.adg_node.to_dict(),
            "output_hash": self.output_hash,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


@dataclass(frozen=True)
class ContextLogAttachment:
    """Attached context logs for a case compilation.

    Attributes
    ----------
    log_hash:
        SHA-256 of the context log content.
    log_type:
        Type of log (e.g., "execution", "telemetry", "audit").
    content_preview:
        Preview of log content (first 200 chars).
    timestamp_utc:
        Unix timestamp when the log was captured.
    """

    log_hash: str
    log_type: Literal["execution", "telemetry", "audit", "guardrail", "replay"]
    content_preview: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.log_hash:
            raise ValueError("log_hash must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "content_preview": self.content_preview,
            "log_hash": self.log_hash,
            "log_type": self.log_type,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# CompilationInput — Ingests sealed L2 outputs
# =============================================================================


@dataclass(frozen=True)
class CompilationInput:
    """Input for case compilation — Step 4 ingestion stage.

    Ingests sealed L2 outputs, attaches context logs, and prepares
    for the freeze/seal pipeline stages.

    Attributes
    ----------
    artifact_type:
        Always ``COMPILATION_INPUT``.
    input_id:
        Deterministic SHA-256 ID for this input.
    sealed_outputs:
        Tuple of sealed L2 output references to compile.
    context_logs:
        Tuple of attached context logs.
    policy_hash_ref:
        Policy snapshot at compilation time.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["COMPILATION_INPUT"]
    input_id: str
    sealed_outputs: tuple[SealedOutputRef, ...]
    context_logs: tuple[ContextLogAttachment, ...]
    policy_hash_ref: PolicyHashRef
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "COMPILATION_INPUT":
            raise ValueError(f"artifact_type must be 'COMPILATION_INPUT', got {self.artifact_type!r}")
        if not self.input_id:
            raise ValueError("input_id must not be empty")
        if not self.sealed_outputs:
            raise ValueError("sealed_outputs must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "context_logs": [log.to_dict() for log in self.context_logs],
            "input_id": self.input_id,
            "policy_hash_ref": self.policy_hash_ref.to_dict(),
            "sealed_outputs": [out.to_dict() for out in self.sealed_outputs],
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# CompilationStage — Individual pipeline stage artifacts
# =============================================================================


@dataclass(frozen=True)
class CompilationStage:
    """Individual stage in the compilation pipeline.

    Represents capture, freeze, or seal stages per the documentation.

    Attributes
    ----------
    stage_type:
        One of CAPTURE, FREEZE, SEAL.
    stage_id:
        Deterministic SHA-256 ID for this stage.
    input_ref:
        Reference to the input being processed.
    output_artifact_hash:
        SHA-256 of the stage output artifact.
    rules_applied:
        Tuple of rule identifiers applied in this stage.
    limits_enforced:
        Tuple of limit identifiers enforced.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    stage_type: Literal["CAPTURE", "FREEZE", "SEAL"]
    stage_id: str
    input_ref: str  # input_id reference
    output_artifact_hash: str
    rules_applied: tuple[str, ...]
    limits_enforced: tuple[str, ...]
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.stage_type not in ("CAPTURE", "FREEZE", "SEAL"):
            raise ValueError(f"stage_type must be CAPTURE/FREEZE/SEAL, got {self.stage_type!r}")
        if not self.stage_id:
            raise ValueError("stage_id must not be empty")
        if not self.input_ref:
            raise ValueError("input_ref must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "input_ref": self.input_ref,
            "limits_enforced": list(self.limits_enforced),
            "output_artifact_hash": self.output_artifact_hash,
            "rules_applied": list(self.rules_applied),
            "stage_id": self.stage_id,
            "stage_type": self.stage_type,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# CompilationPayload — Final master archive payload
# =============================================================================


@dataclass(frozen=True)
class CompilationPayload:
    """Final master archive payload — Step 4 output.

    Sealed payload containing CaseRecord bundles ready for L4 archive.

    Attributes
    ----------
    artifact_type:
        Always ``COMPILATION_PAYLOAD``.
    payload_id:
        Deterministic SHA-256 ID for this payload.
    input_id:
        Reference to the compilation input.
    stages:
        Tuple of compilation stages executed.
    case_records:
        Tuple of compiled CaseRecord bundles.
    policy_hash_ref:
        Policy snapshot at compilation time.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["COMPILATION_PAYLOAD"]
    payload_id: str
    input_id: str
    stages: tuple[CompilationStage, ...]
    case_records: tuple[CaseRecord, ...]
    policy_hash_ref: PolicyHashRef
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "COMPILATION_PAYLOAD":
            raise ValueError(f"artifact_type must be 'COMPILATION_PAYLOAD', got {self.artifact_type!r}")
        if not self.payload_id:
            raise ValueError("payload_id must not be empty")
        if not self.case_records:
            raise ValueError("case_records must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "case_records": [record.to_dict() for record in self.case_records],
            "input_id": self.input_id,
            "payload_id": self.payload_id,
            "policy_hash_ref": self.policy_hash_ref.to_dict(),
            "stages": [stage.to_dict() for stage in self.stages],
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# CaseCompilationResult — Deterministic compilation result
# =============================================================================


@dataclass(frozen=True)
class CaseCompilationResult:
    """Deterministic result of case compilation.

    Contains the final payload and compilation metadata.

    Attributes
    ----------
    artifact_type:
        Always ``CASE_COMPILATION_RESULT``.
    result_id:
        Deterministic SHA-256 ID for this result.
    payload:
        The compiled payload with CaseRecord bundles.
    success:
        True if compilation succeeded.
    error_reason:
        Error description if compilation failed.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["CASE_COMPILATION_RESULT"]
    result_id: str
    payload: CompilationPayload | None
    success: bool
    error_reason: str | None
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "CASE_COMPILATION_RESULT":
            raise ValueError(f"artifact_type must be 'CASE_COMPILATION_RESULT', got {self.artifact_type!r}")
        if not self.result_id:
            raise ValueError("result_id must not be empty")
        if self.success and self.payload is None:
            raise ValueError("payload required when success=True")
        if not self.success and self.error_reason is None:
            raise ValueError("error_reason required when success=False")

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "error_reason": self.error_reason,
            "payload": self.payload.to_dict() if self.payload else None,
            "result_id": self.result_id,
            "success": self.success,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


__all__ = [
    "CaseCompilationResult",
    "CompilationInput",
    "CompilationPayload",
    "CompilationStage",
    "ContextLogAttachment",
    "SealedOutputRef",
]
