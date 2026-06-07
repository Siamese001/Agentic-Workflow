"""Runtime Gate Definitions — Core contracts for the fused gate pipeline.

Implements GateDefinition, GateVerdict, and JudgeVerdict dataclasses for the
RuntimeGateEngine. Reuses Result/Severity/Disposition from L5 safety gates
for consistency across the agentic_core runtime gate mesh.

Spec reference: docs/archive/windsurf/legacy-tree/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W0.P1)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agentic_core.L5_safety.runtime_gates.contracts import (
    Result,
    Severity,
    GraderType,
)


# ----------------------------------------------------------------------------
# Gate placement vocabulary
# ----------------------------------------------------------------------------

class GatePlacement(str, Enum):
    """Lifecycle placement of a runtime gate."""

    PRE_LLM = "PRE_LLM"      # Runs before generation; validates inputs / prompt assembly
    PER_CAND = "PER_CAND"    # Runs per ensemble candidate
    POST_ENS = "POST_ENS"    # Runs once after ensemble selection
    POST_NARR = "POST_NARR"  # Runs after all narrative hops complete
    PRE_EXPORT = "PRE_EXPORT"  # Runs before DOCX export


# ----------------------------------------------------------------------------
# Gate severity / enforcement level
# ----------------------------------------------------------------------------

class GateEnforcement(str, Enum):
    """Enforcement level for a gate."""

    FAIL_CLOSED = "FAIL_CLOSED"  # Non-bypassable; blocks write on FAIL/UNKNOWN
    WARN = "WARN"                # Advisory; logs but allows write
    CONFIGURABLE = "CONFIGURABLE"  # Determined by threshold profile


# ----------------------------------------------------------------------------
# Core dataclasses
# ----------------------------------------------------------------------------

@dataclass(frozen=True)
class GateDefinition:
    """Static definition of a runtime gate.

    Fields:
        gate_id: Canonical identifier (e.g., "candidate_acceptance_guard")
        placement: Lifecycle placement (PRE_LLM, PER_CAND, etc.)
        enforcement: FAIL_CLOSED, WARN, or CONFIGURABLE
        bypassable: Whether this gate can be bypassed in any mode
        dependencies: List of gate_ids that must run before this gate
        description: Human-readable description
        default_tolerance: Default tolerance for numeric gates (0.0-1.0)
    """

    gate_id: str
    placement: GatePlacement
    enforcement: GateEnforcement
    bypassable: bool = False
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""
    default_tolerance: float = 0.0

    def __post_init__(self) -> None:
        if not self.gate_id:
            raise ValueError("gate_id is required")
        if not isinstance(self.placement, GatePlacement):
            object.__setattr__(
                self, "placement", GatePlacement(self.placement)
            )
        if not isinstance(self.enforcement, GateEnforcement):
            object.__setattr__(
                self, "enforcement", GateEnforcement(self.enforcement)
            )


@dataclass(frozen=True)
class GateVerdict:
    """Verdict from a single **00C / runtime GateMesh** gate evaluation.

    This is the canonical **live** gate verdict type for fused runtime gates.
    Do **not** confuse with ``apps_rg.runtime.bindings.exit_binding.ExitGateVerdict``,
    which is an **apps_rg-local** Exit helper enum — orthogonal namespace.

    Fields:
        gate_id: The gate that produced this verdict
        result: PASS, FAIL, WARN, UNKNOWN, or NOT_APPLICABLE
        reason: Human-readable explanation
        reason_codes: Machine-readable failure reasons
        evidence_refs: References to source bullets, spans, traces
        timestamp_utc: ISO8601 timestamp of evaluation
        latency_ms: Wall-clock time spent evaluating
        deterministic_digest: Hash of inputs for reproducibility
    """

    gate_id: str
    result: Result
    reason: str = ""
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    timestamp_utc: str = ""
    latency_ms: float = 0.0
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        if not self.gate_id:
            raise ValueError("gate_id is required")
        if isinstance(self.result, str):
            object.__setattr__(self, "result", Result(self.result))

    def is_blocking(self, enforcement: GateEnforcement) -> bool:
        """Returns True if this verdict should block write."""
        if enforcement == GateEnforcement.FAIL_CLOSED:
            return self.result in (Result.FAIL, Result.UNKNOWN)
        return False


@dataclass(frozen=True)
class JudgeVerdict:
    """Verdict from an online judge (narrative_judge_scorer, etc.).

    Required fields per Online Judge Runtime Contract:
        judge_id: Canonical judge identifier
        judge_version: Semver of judge implementation
        rubric_version: Version of rubric applied
        threshold_profile_id: Active threshold profile
        gate_id: Runtime gate this judge feeds into
        placement: PER_CAND, POST_ENS, etc.
        score: Normalized score 0.0-1.0
        accepted: Whether candidate passed threshold
        result: PASS/FAIL/WARN/UNKNOWN/NOT_APPLICABLE
        reason_codes: Machine-readable explanations
        evidence_refs: References to source bullets/spans
        deterministic_digest: Hash of inputs
    """

    # Required identifiers
    judge_id: str
    judge_version: str
    rubric_version: str
    threshold_profile_id: str

    # Runtime binding
    gate_id: str
    placement: GatePlacement

    # Evaluation result
    score: float = 0.0
    accepted: bool = False
    result: Result = Result.UNKNOWN

    # Explanation and evidence
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        # Validate required fields
        if not self.judge_id:
            raise ValueError("judge_id is required")
        if not self.judge_version:
            raise ValueError("judge_version is required")
        if not self.rubric_version:
            raise ValueError("rubric_version is required")
        if not self.threshold_profile_id:
            raise ValueError("threshold_profile_id is required")
        if not self.gate_id:
            raise ValueError("gate_id is required")

        # Validate score range
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be in [0,1]; got {self.score}")

        # Normalize enums
        if isinstance(self.placement, str):
            object.__setattr__(self, "placement", GatePlacement(self.placement))
        if isinstance(self.result, str):
            object.__setattr__(self, "result", Result(self.result))

    def to_gate_verdict(self) -> GateVerdict:
        """Normalize JudgeVerdict to GateVerdict for GateBundle aggregation."""
        return GateVerdict(
            gate_id=self.gate_id,
            result=self.result,
            reason=f"Judge {self.judge_id} v{self.judge_version}: accepted={self.accepted}",
            reason_codes=self.reason_codes,
            evidence_refs=self.evidence_refs + (f"judge:{self.judge_id}",),
            deterministic_digest=self.deterministic_digest,
        )


__all__ = [
    "GatePlacement",
    "GateEnforcement",
    "GateDefinition",
    "GateVerdict",
    "JudgeVerdict",
]
