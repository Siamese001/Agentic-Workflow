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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "boundary_types", "L0")
_emit_routes_through("p1", "boundary_types", "L0")
_emit_escalates_to_human("p1", "boundary_types", "L0")
_emit_reads_policy_state("p1", "boundary_types", "L0")

_emit_records_execution_trace("p0", "evidence", "boundary_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "boundary_types", "p0_governance")
_emit_snapshots_state("p0", "boundary_types", "state_snapshot")


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
            raise ValueError("ContextRetrievalRequest: trace_id must be non-empty")
        if not self.query_hash:
            raise ValueError("ContextRetrievalRequest: query_hash must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"ContextRetrievalRequest: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}"
            )
        if not self.read_only:
            raise ValueError("ContextRetrievalRequest: read_only must be True (L0→L4 is advisory-only)")


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
            raise ValueError("BoundarySchemaDescriptor: schema_id must be non-empty")
        if not self.schema_version:
            raise ValueError("BoundarySchemaDescriptor: schema_version must be non-empty")
        if not self.source_layer:
            raise ValueError("BoundarySchemaDescriptor: source_layer must be non-empty")
        if not self.target_layer:
            raise ValueError("BoundarySchemaDescriptor: target_layer must be non-empty")
        if not isinstance(self.validation_status, SchemaValidationStatus):
            raise TypeError(
                f"BoundarySchemaDescriptor: validation_status must be SchemaValidationStatus, got {type(self.validation_status).__name__}"
            )


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
            raise ValueError("InvariantViolation: invariant_id must be non-empty")
        if not isinstance(self.severity, InvariantSeverity):
            raise TypeError(
                f"InvariantViolation: severity must be InvariantSeverity, got {type(self.severity).__name__}"
            )
        if not isinstance(self.evidence_paths, tuple):
            raise TypeError("InvariantViolation: evidence_paths must be a tuple")
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
            raise ValueError("MetaInvariantReport: trace_id must be non-empty")
        if not self.run_id:
            raise ValueError("MetaInvariantReport: run_id must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"MetaInvariantReport: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}"
            )
        if not isinstance(self.checks, tuple):
            raise TypeError("MetaInvariantReport: checks must be a tuple")
        if not isinstance(self.violations, tuple):
            raise TypeError("MetaInvariantReport: violations must be a tuple")
        if self.violations and self.pass_fail:
            raise ValueError("MetaInvariantReport: pass_fail cannot be True when violations are present")


@dataclass(frozen=True)
class SideEffectRegistry:
    """§12.2 — Immutable registry of side effects produced during a heal wave.

    Tracks all resources touched (read/written) and APIs called,
    enabling deterministic replay and audit.
    """

    trace_id: str
    wave_id: str
    paths_read: tuple[str, ...]
    paths_written: tuple[str, ...]
    apis_called: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("SideEffectRegistry: trace_id must be non-empty")
        if not self.wave_id:
            raise ValueError("SideEffectRegistry: wave_id must be non-empty")
        if not isinstance(self.paths_read, tuple):
            raise TypeError("SideEffectRegistry: paths_read must be a tuple")
        if not isinstance(self.paths_written, tuple):
            raise TypeError("SideEffectRegistry: paths_written must be a tuple")
        if not isinstance(self.apis_called, tuple):
            raise TypeError("SideEffectRegistry: apis_called must be a tuple")


V15_DISCOVERY_SCHEMA_VERSION: str = "1.0.0"


@dataclass(frozen=True)
class V15DiscoverySchema:
    """§8.4 — Pinned discovery schema for the V15 Environment Under Test.

    ALL fields are required. Missing field = HARD FAIL in guardian tests.
    MRO scanners MUST consume ONLY this schema (no live reflection fallback).
    """

    identity: str
    layer: str
    status: str
    file_path: str
    class_name: str
    mro_chain: tuple[str, ...]
    mixins: tuple[str, ...]
    detected_methods: tuple[str, ...]
    integrity_hash: str
    mro_signature: str

    def __post_init__(self) -> None:
        if not self.identity:
            raise ValueError("V15DiscoverySchema: identity must be non-empty")
        if not self.layer:
            raise ValueError("V15DiscoverySchema: layer must be non-empty")
        if not self.status:
            raise ValueError("V15DiscoverySchema: status must be non-empty")
        if not self.file_path:
            raise ValueError("V15DiscoverySchema: file_path must be non-empty")
        if not self.class_name:
            raise ValueError("V15DiscoverySchema: class_name must be non-empty")
        if not isinstance(self.mro_chain, tuple):
            raise TypeError("V15DiscoverySchema: mro_chain must be a tuple")
        if not isinstance(self.mixins, tuple):
            raise TypeError("V15DiscoverySchema: mixins must be a tuple")
        if not isinstance(self.detected_methods, tuple):
            raise TypeError("V15DiscoverySchema: detected_methods must be a tuple")
        if not self.integrity_hash:
            raise ValueError("V15DiscoverySchema: integrity_hash must be non-empty")
        if not self.mro_signature:
            raise ValueError("V15DiscoverySchema: mro_signature must be non-empty")


V15_DISCOVERY_REQUIRED_FIELDS: frozenset[str] = frozenset(
    f.name for f in __import__("dataclasses").fields(V15DiscoverySchema)
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
    "SideEffectRegistry",
    "V15DiscoverySchema",
    "V15_DISCOVERY_REQUIRED_FIELDS",
    "V15_DISCOVERY_SCHEMA_VERSION",
]
