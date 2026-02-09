"""
V15 P6 Typed Artifacts — Meta-Invariants & Typed Boundaries.

Typed artifacts required by Prompt v5.0 Enhanced for P6 (Explicit
Boundaries / Zero Trust Between Layers) invariants. All report and
violation artifacts are frozen dataclasses with strict field validation.

Artifact version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# =============================================================================
# §1.5 — SSOT Binding (node_id resolves to structure_blueprint)
# =============================================================================


@dataclass(frozen=True)
class SSOTBinding:
    """§1.5 — Proves a node_id resolves to a valid SSOT definition.

    The binding links the manifest's node_id to the blueprint entry
    that authorizes it.
    """

    node_id: str
    blueprint_entry: str
    resolved: bool

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("SSOTBinding: node_id must be non-empty")
        if not self.blueprint_entry:
            raise ValueError("SSOTBinding: blueprint_entry must be non-empty")


# =============================================================================
# §3.8 — Context Retrieval Request Artifact (L0→L4)
# =============================================================================


@dataclass(frozen=True)
class ContextRetrievalRequest:
    """§3.8 — Typed request from L0 to L4 (advisory-only, read-only).

    Required fields: trace_id, query_hash, semantic_clock_tick.
    Constraint: No direct writes from L0.
    """

    trace_id: str
    query_hash: str
    semantic_clock_tick: int
    source_layer: str = "L0"
    target_layer: str = "L4"
    read_only: bool = True

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError(
                "ContextRetrievalRequest: trace_id must be non-empty",
            )
        if not self.query_hash:
            raise ValueError(
                "ContextRetrievalRequest: query_hash must be non-empty",
            )
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"ContextRetrievalRequest: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not self.read_only:
            raise ValueError(
                "ContextRetrievalRequest: read_only must be True (L0→L4 is advisory-only)",
            )


# =============================================================================
# §12.1 / §2.4 — Boundary Schema Descriptor
# =============================================================================


class SchemaValidationStatus(Enum):
    """Status of a boundary schema validation."""

    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"


@dataclass(frozen=True)
class BoundarySchemaDescriptor:
    """§12.1 / §2.4 — Typed and versioned boundary between layers.

    Every cross-layer call must declare its schema version and the
    source/target layers. Validation status is captured.
    """

    schema_id: str
    schema_version: str
    source_layer: str
    target_layer: str
    validation_status: SchemaValidationStatus

    def __post_init__(self) -> None:
        if not self.schema_id:
            raise ValueError(
                "BoundarySchemaDescriptor: schema_id must be non-empty",
            )
        if not self.schema_version:
            raise ValueError(
                "BoundarySchemaDescriptor: schema_version must be non-empty",
            )
        if not self.source_layer:
            raise ValueError(
                "BoundarySchemaDescriptor: source_layer must be non-empty",
            )
        if not self.target_layer:
            raise ValueError(
                "BoundarySchemaDescriptor: target_layer must be non-empty",
            )
        if not isinstance(self.validation_status, SchemaValidationStatus):
            raise TypeError(
                f"BoundarySchemaDescriptor: validation_status must be "
                f"SchemaValidationStatus, got {type(self.validation_status).__name__}",
            )


# =============================================================================
# Meta-Invariant Report Types
# =============================================================================


class InvariantSeverity(Enum):
    """Severity of an invariant violation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    INFO = "info"


@dataclass(frozen=True)
class InvariantViolation:
    """A single meta-invariant violation with evidence."""

    invariant_id: str
    severity: InvariantSeverity
    evidence_paths: tuple[str, ...]
    details: str

    def __post_init__(self) -> None:
        if not self.invariant_id:
            raise ValueError(
                "InvariantViolation: invariant_id must be non-empty",
            )
        if not isinstance(self.severity, InvariantSeverity):
            raise TypeError(
                f"InvariantViolation: severity must be InvariantSeverity, got {type(self.severity).__name__}",
            )
        if not isinstance(self.evidence_paths, tuple):
            raise TypeError(
                "InvariantViolation: evidence_paths must be a tuple",
            )
        if not self.details:
            raise ValueError("InvariantViolation: details must be non-empty")


@dataclass(frozen=True)
class InvariantCheck:
    """A single invariant check result."""

    check_id: str
    description: str
    passed: bool
    evidence: str

    def __post_init__(self) -> None:
        if not self.check_id:
            raise ValueError("InvariantCheck: check_id must be non-empty")
        if not self.description:
            raise ValueError("InvariantCheck: description must be non-empty")
        if not self.evidence:
            raise ValueError("InvariantCheck: evidence must be non-empty")


@dataclass(frozen=True)
class MetaInvariantReport:
    """Meta-governor report for end-of-wave / end-of-run invariant checks.

    Fields: trace_id, run_id, semantic_clock_tick, checks, pass_fail, violations.
    """

    trace_id: str
    run_id: str
    semantic_clock_tick: int
    checks: tuple[InvariantCheck, ...]
    pass_fail: bool
    violations: tuple[InvariantViolation, ...]

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError(
                "MetaInvariantReport: trace_id must be non-empty",
            )
        if not self.run_id:
            raise ValueError(
                "MetaInvariantReport: run_id must be non-empty",
            )
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"MetaInvariantReport: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not isinstance(self.checks, tuple):
            raise TypeError("MetaInvariantReport: checks must be a tuple")
        if not isinstance(self.violations, tuple):
            raise TypeError("MetaInvariantReport: violations must be a tuple")
        # pass_fail must be consistent with violations
        if self.violations and self.pass_fail:
            raise ValueError(
                "MetaInvariantReport: pass_fail cannot be True when violations are present",
            )


__all__ = [
    "BoundarySchemaDescriptor",
    "ContextRetrievalRequest",
    "InvariantCheck",
    "InvariantSeverity",
    "InvariantViolation",
    "MetaInvariantReport",
    "SSOTBinding",
    "SchemaValidationStatus",
]
