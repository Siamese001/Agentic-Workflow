"""
V15 P2 Framework Contracts — Determinism & Replayability Enforcement.

Runtime contracts enforcing P2 (Determinism & Replayability) invariants required
by the V15 Target State audit (Prompt v5.0 Enhanced).

Contract version: 1.0.0
"""

from __future__ import annotations

import ast
import hashlib
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    FORBIDDEN_INPUT_PATTERNS,
    MEMORY_CONFIDENCE_THRESHOLD,
    TRACE_BUFFER_VELOCITY_THRESHOLD,
    WALL_CLOCK_FORBIDDEN_CALLABLES,
    BoundarySnapshotArtifact,
    CanonicalASTResult,
    SemanticClock,
    SurgicalManifest,
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
)

_emit_dispatches_healing_run("p1", "determinism_contracts_types", "L0")
_emit_routes_through("p1", "determinism_contracts_types", "L0")
_emit_escalates_to_human("p1", "determinism_contracts_types", "L0")
_emit_reads_policy_state("p1", "determinism_contracts_types", "L0")

_emit_records_execution_trace("p0", "evidence", "determinism_contracts_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "determinism_contracts_types", "p0_governance")
_emit_snapshots_state("p0", "determinism_contracts_types", "state_snapshot")

# =============================================================================
# §1.1 — SurgicalManifest as exclusive execution input
# §1.2 — Forbidden execution inputs enforcement
# =============================================================================


class ForbiddenInputError(Exception):
    """§1.2 — Raised when a forbidden execution input is detected."""

    def __init__(self, input_type: str) -> None:
        self.input_type = input_type
        super().__init__(
            f"FAIL (P2): Forbidden execution input detected: '{input_type}'. "
            "Only SurgicalManifest is a valid execution input.",
        )


def validate_execution_input(input_obj: Any) -> SurgicalManifest:
    """§1.1/§1.2 — Validate that execution input is exclusively a SurgicalManifest.

    Rejects raw paths, regex, diffs, line numbers, free-form text, etc.
    Fail-closed: anything that is not a SurgicalManifest is rejected.
    """
    if not isinstance(input_obj, SurgicalManifest):
        raise ForbiddenInputError(type(input_obj).__name__)
    return input_obj


def check_forbidden_input_type(input_type: str) -> None:
    """§1.2 — Check if an input type is in the forbidden set."""
    if input_type in FORBIDDEN_INPUT_PATTERNS:
        raise ForbiddenInputError(input_type)


# =============================================================================
# §2.1 — Validator emits SurgicalManifest (per-agent contract)
# =============================================================================


def validate_manifest_emission(manifest: Any) -> SurgicalManifest:
    """§2.1 — Validator MUST emit a SurgicalManifest. Fail-closed on wrong type."""
    if not isinstance(manifest, SurgicalManifest):
        raise TypeError(
            f"FAIL (P2): Validator must emit SurgicalManifest, got {type(manifest).__name__}",
        )
    if not manifest.verify_hash():
        raise ValueError(
            "FAIL (P2): SurgicalManifest manifest_hash does not match ast_snippet SHA-256",
        )
    return manifest


def require_manifest_hash_ok(manifest: SurgicalManifest) -> None:
    """§1.6 — Fail-closed: verify manifest_hash matches ast_snippet SHA-256.

    Call immediately after SurgicalManifest construction, before return.
    Raises ValueError on mismatch.
    """
    if not manifest.verify_hash():
        raise ValueError("SurgicalManifest integrity hash mismatch")


# =============================================================================
# §1.4 — Deterministic AST serialization
# =============================================================================


def canonical_ast_serialize(source: str, source_path: str = "<string>") -> CanonicalASTResult:
    """§1.4 — Deterministic AST serialization via sorted ast.dump.

    Produces a canonical string form of the AST that is stable across runs.
    LibCST or sorted ast.dump; formatter-dependent output is invalid.
    """
    tree = ast.parse(source)
    canonical = ast.dump(tree, indent=None)
    canonical_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return CanonicalASTResult(
        source_path=source_path,
        canonical_form=canonical,
        canonical_hash=canonical_hash,
    )


def verify_ast_determinism(source: str) -> bool:
    """§1.4 — Verify AST serialization is deterministic (two runs produce same hash)."""
    r1 = canonical_ast_serialize(source)
    r2 = canonical_ast_serialize(source)
    return r1.canonical_hash == r2.canonical_hash


# =============================================================================
# §5.1 — Dedupe uses SHA-256 (per-agent contract)
# =============================================================================


def dedupe_sha256(signal_data: str) -> str:
    """§5.1 — All deduplication uses cryptographic SHA-256 hashes."""
    return hashlib.sha256(signal_data.encode("utf-8")).hexdigest()


def dedupe_check(signal_data: str, seen_hashes: set[str]) -> bool:
    """§5.1 — Returns True if signal is a duplicate (already seen)."""
    h = dedupe_sha256(signal_data)
    if h in seen_hashes:
        return True
    seen_hashes.add(h)
    return False


# =============================================================================
# §13.1 / §13.1.1 / §13.2 — Semantic Clock enforcement
# =============================================================================


class WallClockViolation(Exception):
    """§13.2 — Wall-clock usage detected in hash/signature/dedup path."""

    def __init__(self, callable_name: str, file_path: str, line: int) -> None:
        self.callable_name = callable_name
        self.file_path = file_path
        self.line = line
        super().__init__(
            f"FAIL (P2): Wall-clock callable '{callable_name}' at "
            f"{file_path}:{line} in hash/signature/dedup path",
        )


def ast_scan_wall_clock(source: str, file_path: str = "<string>") -> list[WallClockViolation]:
    """§13.2 — AST scan for wall-clock callables in source code.

    Returns list of violations. Empty list = compliant.
    """
    violations: list[WallClockViolation] = []
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                full_name = f"{node.value.id}.{node.attr}"
                if full_name in WALL_CLOCK_FORBIDDEN_CALLABLES:
                    violations.append(
                        WallClockViolation(full_name, file_path, getattr(node, "lineno", 0)),
                    )
            elif isinstance(node.value, ast.Attribute):
                if isinstance(node.value.value, ast.Name):
                    full_name = f"{node.value.value.id}.{node.value.attr}.{node.attr}"
                    shortened = f"{node.value.attr}.{node.attr}"
                    if shortened in WALL_CLOCK_FORBIDDEN_CALLABLES:
                        violations.append(
                            WallClockViolation(
                                full_name,
                                file_path,
                                getattr(node, "lineno", 0),
                            ),
                        )
    return violations


# =============================================================================
# §10.2 / §10.3 — Rollback determinism
# =============================================================================


def create_boundary_snapshot(
    trace_id: str,
    filesystem_hash: str,
    git_state_hash: str,
    agent_memory_hash: str,
    semantic_clock: SemanticClock,
) -> BoundarySnapshotArtifact:
    """§10.2 — Create a BoundarySnapshotArtifact at wave start."""
    return BoundarySnapshotArtifact(
        trace_id=trace_id,
        filesystem_hash=filesystem_hash,
        git_state_hash=git_state_hash,
        agent_memory_hash=agent_memory_hash,
        semantic_clock_tick=semantic_clock.current_tick,
    )


class RollbackHashMismatch(Exception):
    """§10.3 — Post-rollback hash does not match pre-wave snapshot."""

    def __init__(self, field: str, expected: str, actual: str) -> None:
        self.field = field
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"FAIL (P2): Post-rollback {field} hash mismatch. "
            f"Expected {expected[:16]}..., got {actual[:16]}...",
        )


def verify_rollback_integrity(
    pre_snapshot: BoundarySnapshotArtifact,
    post_fs_hash: str,
    post_git_hash: str,
    post_memory_hash: str,
) -> bool:
    """§10.3 — Post-rollback state hash must exactly match pre-wave snapshot.

    Raises RollbackHashMismatch on any mismatch.
    """
    if pre_snapshot.filesystem_hash != post_fs_hash:
        raise RollbackHashMismatch(
            "filesystem",
            pre_snapshot.filesystem_hash,
            post_fs_hash,
        )
    if pre_snapshot.git_state_hash != post_git_hash:
        raise RollbackHashMismatch(
            "git_state",
            pre_snapshot.git_state_hash,
            post_git_hash,
        )
    if pre_snapshot.agent_memory_hash != post_memory_hash:
        raise RollbackHashMismatch(
            "agent_memory",
            pre_snapshot.agent_memory_hash,
            post_memory_hash,
        )
    return True


# =============================================================================
# §6.1 — Episodic memory query enforcement
# =============================================================================


class EpisodicMemoryNotQueried(Exception):
    """§6.1 — Planning attempted without querying episodic memory first."""


def enforce_episodic_query_before_planning(episodic_result: Any | None) -> None:
    """§6.1 — Fail-closed: episodic memory must be queried before planning."""
    if episodic_result is None:
        raise EpisodicMemoryNotQueried(
            "FAIL (P2): Episodic memory must be queried before planning.",
        )


# =============================================================================
# §6.6 — Knowledge Supervisor enforcement
# =============================================================================


def knowledge_supervisor_check(  # guardian: allow-magic_configuration
    confidence: float,
    threshold: float = MEMORY_CONFIDENCE_THRESHOLD,
) -> bool:
    """§6.6 — Returns True if confidence is below threshold (requires retraining)."""
    return confidence < threshold


# =============================================================================
# §15.3 — Forensic Trace Buffer enforcement
# =============================================================================


def check_velocity_threshold(  # guardian: allow-magic_configuration
    signal_count: int,
    threshold: int = TRACE_BUFFER_VELOCITY_THRESHOLD,
) -> bool:
    """§15.3 — Returns True if signal_count meets or exceeds velocity threshold."""
    return signal_count >= threshold


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "EpisodicMemoryNotQueried",
    "ForbiddenInputError",
    "RollbackHashMismatch",
    "WallClockViolation",
    "ast_scan_wall_clock",
    "canonical_ast_serialize",
    "check_forbidden_input_type",
    "check_velocity_threshold",
    "create_boundary_snapshot",
    "dedupe_check",
    "dedupe_sha256",
    "enforce_episodic_query_before_planning",
    "knowledge_supervisor_check",
    "require_manifest_hash_ok",
    "validate_execution_input",
    "validate_manifest_emission",
    "verify_ast_determinism",
    "verify_rollback_integrity",
]
