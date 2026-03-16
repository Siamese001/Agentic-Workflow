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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "memory_types")
emit_determinism_digest("p0", "memory_types")

_emit_dispatches_healing_run("p1", "memory_types", "L1")
_emit_routes_through("p1", "memory_types", "L1")
_emit_escalates_to_human("p1", "memory_types", "L1")
_emit_reads_policy_state("p1", "memory_types", "L1")

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
