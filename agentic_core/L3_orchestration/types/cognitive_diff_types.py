"""
§Wave4.2 — L3CognitiveDiffBundle: deterministic cognitive state diff at L3 boundary.

Emitted when L3 produces a RouteDecisionArtifact, capturing the before/after
cognitive state and a structured, sorted diff representation.

Deterministic contract:
  - SemanticClockSnapshot required (Phase 3.2)
  - DiffOp list sorted by path
  - Deterministic trace_id (SHA-256 of canonical payload)
  - No uuid4, no wall-clock, no elapsed_ms
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "cognitive_diff_types")
emit_determinism_digest("p0", "cognitive_diff_types")

_emit_dispatches_healing_run("p1", "cognitive_diff_types", "L3")
_emit_routes_through("p1", "cognitive_diff_types", "L3")
_emit_escalates_to_human("p1", "cognitive_diff_types", "L3")
_emit_reads_policy_state("p1", "cognitive_diff_types", "L3")

_emit_snapshots_state("p0", "cognitive_diff_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "cognitive_diff_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "cognitive_diff_types")

# =============================================================================
# §Wave4.2 — CognitiveStateSnapshot
# =============================================================================


@dataclass(frozen=True)
class CognitiveStateSnapshot:
    """Minimal, stable snapshot of cognitive state at a decision boundary.

    All fields are JSON-primitive compatible. No repr(), no Enum objects.
    """

    route_context: str
    candidate_paths: tuple[str, ...]
    selected_path: str
    rationale_enum: str
    risk_score: float
    budget_est: float

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_paths, tuple):
            raise TypeError(
                "CognitiveStateSnapshot: candidate_paths must be a tuple",
            )
        if list(self.candidate_paths) != sorted(self.candidate_paths):
            raise ValueError(
                "CognitiveStateSnapshot: candidate_paths must be sorted",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "budget_est": self.budget_est,
            "candidate_paths": list(self.candidate_paths),
            "rationale_enum": self.rationale_enum,
            "risk_score": self.risk_score,
            "route_context": self.route_context,
            "selected_path": self.selected_path,
        }


# =============================================================================
# §Wave4.2 — DiffOp
# =============================================================================


@dataclass(frozen=True)
class DiffOp:
    """A single field-level diff operation between before and after states.

    path: dotted field name (e.g., "selected_path", "risk_score")
    before: JSON-primitive value from the before state
    after: JSON-primitive value from the after state
    """

    path: str
    before: Any
    after: Any

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("DiffOp: path must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "after": self.after,
            "before": self.before,
            "path": self.path,
        }


# =============================================================================
# §Wave4.2 — L3CognitiveDiffBundle
# =============================================================================


@dataclass(frozen=True)
class L3CognitiveDiffBundle:
    """§Wave4.2 — Deterministic cognitive diff emitted at L3 orchestration boundary.

    Required fields:
      artifact_type     — fixed "COGNITIVE_DIFF_BUNDLE"
      semantic_clock    — required SemanticClockSnapshot (Phase 3.2)
      trace_id          — deterministic (SHA-256 of canonical payload)
      before            — CognitiveStateSnapshot
      after             — CognitiveStateSnapshot
      diff              — sorted tuple of DiffOp
      policy_config_hash — optional
    """

    artifact_type: str
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    before: CognitiveStateSnapshot
    after: CognitiveStateSnapshot
    diff: tuple[DiffOp, ...]
    policy_config_hash: str = ""

    def __post_init__(self) -> None:
        if self.artifact_type != "COGNITIVE_DIFF_BUNDLE":
            raise ValueError(
                f"L3CognitiveDiffBundle: artifact_type must be 'COGNITIVE_DIFF_BUNDLE', "
                f"got '{self.artifact_type}'",
            )
        validate_semantic_clock(self.semantic_clock)
        if not self.trace_id:
            raise ValueError(
                "L3CognitiveDiffBundle: trace_id must be non-empty",
            )
        if not isinstance(self.before, CognitiveStateSnapshot):
            raise TypeError(
                "L3CognitiveDiffBundle: before must be CognitiveStateSnapshot",
            )
        if not isinstance(self.after, CognitiveStateSnapshot):
            raise TypeError(
                "L3CognitiveDiffBundle: after must be CognitiveStateSnapshot",
            )
        if not isinstance(self.diff, tuple):
            raise TypeError("L3CognitiveDiffBundle: diff must be a tuple")
        paths = [op.path for op in self.diff]
        if paths != sorted(paths):
            raise ValueError(
                "L3CognitiveDiffBundle: diff ops must be sorted by path",
            )

    def to_dict(self) -> dict[str, Any]:
        """Deterministic serialization with sorted keys."""
        return {
            "after": self.after.to_dict(),
            "artifact_type": self.artifact_type,
            "before": self.before.to_dict(),
            "diff": [op.to_dict() for op in self.diff],
            "policy_config_hash": self.policy_config_hash,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }


# =============================================================================
# §Wave4.2 — Deterministic diff computation + bundle factory
# =============================================================================

_DIFF_FIELDS = (
    "budget_est",
    "candidate_paths",
    "rationale_enum",
    "risk_score",
    "route_context",
    "selected_path",
)


def compute_cognitive_diff(
    before: CognitiveStateSnapshot,
    after: CognitiveStateSnapshot,
) -> tuple[DiffOp, ...]:
    """Compute sorted diff ops between two CognitiveStateSnapshot instances.

    Compares all tracked fields. Only changed fields produce a DiffOp.
    Ops are sorted by path (alphabetical).
    """
    ops: list[DiffOp] = []
    before_d = before.to_dict()
    after_d = after.to_dict()

    for field_name in _DIFF_FIELDS:
        bv = before_d[field_name]
        av = after_d[field_name]
        if bv != av:
            ops.append(DiffOp(path=field_name, before=bv, after=av))

    return tuple(sorted(ops, key=lambda op: op.path))


def _compute_bundle_trace_id(
    before: CognitiveStateSnapshot,
    after: CognitiveStateSnapshot,
    tick: int,
) -> str:
    """Deterministic trace_id from canonical payload hash."""
    canonical = json.dumps(
        {"after": after.to_dict(), "before": before.to_dict(), "tick": tick},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def emit_cognitive_diff_bundle(
    before: CognitiveStateSnapshot,
    after: CognitiveStateSnapshot,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str = "",
) -> L3CognitiveDiffBundle:
    """§Wave4.2 — Build an L3CognitiveDiffBundle deterministically.

    1. Compute sorted diff ops
    2. Generate deterministic trace_id
    3. Return frozen bundle
    """
    validate_semantic_clock(semantic_clock)
    diff = compute_cognitive_diff(before, after)
    trace_id = _compute_bundle_trace_id(before, after, semantic_clock.tick)

    return L3CognitiveDiffBundle(
        artifact_type="COGNITIVE_DIFF_BUNDLE",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        before=before,
        after=after,
        diff=diff,
        policy_config_hash=policy_config_hash,
    )


__all__ = [
    "CognitiveStateSnapshot",
    "DiffOp",
    "L3CognitiveDiffBundle",
    "compute_cognitive_diff",
    "emit_cognitive_diff_bundle",
]
