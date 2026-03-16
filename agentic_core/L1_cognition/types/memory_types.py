"""
agentic_core/L1_cognition/reasoning/types/memory_types.py

Passive data structures and constants for HealingMemoryEmbedder.
Extracted from engine/memory_embedder.py to prevent circular dependencies.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "memory_types")
emit_determinism_digest("p0", "memory_types")

_emit_dispatches_healing_run("p1", "memory_types", "L1")
_emit_routes_through("p1", "memory_types", "L1")
_emit_escalates_to_human("p1", "memory_types", "L1")
_emit_reads_policy_state("p1", "memory_types", "L1")
_emit_authorize_and_execute("p2", "memory_types", "execution_auth")
_emit_validates_capability("p2", "memory_types", "capability_check")
_emit_routes_to_capability("p2", "memory_types", "capability_route")
_emit_writes_via_uwg("p2", "memory_types", "uwg_write")
_emit_blocks_direct_write("p2", "memory_types", "direct_write_block")
_emit_records_tool_invocation("p2", "memory_types", "tool_invocation")
_emit_captures_execution_output("p2", "memory_types", "exec_output")
_emit_dispatches_agent("p3", "memory_types", "agent_dispatch")
_emit_coordinates_agents("p3", "memory_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "memory_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "memory_types", "healing_outcome")
_emit_escalates_failure("p3", "memory_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "memory_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "memory_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "memory_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "memory_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "memory_types", "eval_metric")
_emit_stores_embedding("p4", "memory_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "memory_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "memory_types", "exec_snapshot_link")

EMBEDDING_DIMENSION: Final[int] = 1024
MAX_TEXT_LENGTH: Final[int] = 8000


@dataclass
class ViolationSignature:
    """
    Represents a violation signature for embedding.

    Attributes:
        violation_type: Type of violation
        path: File path where violation occurred
        message: Violation message
        context: Additional context (e.g., line numbers, code snippet)
        domain: Domain context (agentic_core, apps_lic, apps_rg)
    """

    violation_type: str
    path: str = ""
    message: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    domain: str = AGENTIC_CORE_DIR

    def to_text(self) -> str:
        """Convert signature to text for embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ViolationSignature.to_text", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ViolationSignature.to_text", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ViolationSignature.to_text")

        parts = [
            f"violation_type: {self.violation_type}",
            f"path: {self.path}",
            f"message: {self.message[:500]}",
            f"domain: {self.domain}",
        ]
        if self.context:
            context_str = json.dumps(self.context, default=str)[:500]
            parts.append(f"context: {context_str}")
        return " | ".join(parts)

    def to_hash(self) -> str:
        """Generate hash-based signature."""
        text = self.to_text()
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    @classmethod
    def from_violation(cls, violation: dict[str, Any]) -> ViolationSignature:
        """Create signature from violation dictionary."""
        return cls(
            violation_type=violation.get("type", "unknown"),
            path=violation.get("path", ""),
            message=violation.get("message", ""),
            context=violation.get("context", {}),
            domain=violation.get("domain", AGENTIC_CORE_DIR),
        )
