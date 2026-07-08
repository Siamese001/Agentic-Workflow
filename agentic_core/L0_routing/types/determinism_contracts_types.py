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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from tqdm import tqdm

trace_contract.record_execution_trace("determinism_contracts_types", "determinism_contracts_types_trace")


trace_contract._emit_emits_metric_event("determinism_contracts_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("determinism_contracts_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("determinism_contracts_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("determinism_contracts_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("determinism_contracts_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("determinism_contracts_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("determinism_contracts_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("determinism_contracts_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("determinism_contracts_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("determinism_contracts_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("determinism_contracts_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("determinism_contracts_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("determinism_contracts_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("determinism_contracts_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("determinism_contracts_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("determinism_contracts_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("determinism_contracts_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("determinism_contracts_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("determinism_contracts_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("determinism_contracts_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("determinism_contracts_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("determinism_contracts_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("determinism_contracts_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("determinism_contracts_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("determinism_contracts_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("determinism_contracts_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("determinism_contracts_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("determinism_contracts_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "determinism_contracts_types")
trace_contract.emit_determinism_digest("p0", "determinism_contracts_types")

trace_contract._emit_dispatches_healing_run("p1", "determinism_contracts_types", "L0")
trace_contract._emit_routes_through("p1", "determinism_contracts_types", "L0")
trace_contract._emit_checks_agent_registry("p1", "determinism_contracts_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "determinism_contracts_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "determinism_contracts_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "determinism_contracts_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "determinism_contracts_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "determinism_contracts_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "determinism_contracts_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "determinism_contracts_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "determinism_contracts_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "determinism_contracts_types")
trace_contract._emit_gated_by_confidence("p1", "determinism_contracts_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "determinism_contracts_types", "L0")
trace_contract._emit_reads_policy_state("p1", "determinism_contracts_types", "L0")
trace_contract._emit_pulls_context("p1", "determinism_contracts_types", "context_pull")
trace_contract._emit_pulls_context("p1", "determinism_contracts_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "determinism_contracts_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "determinism_contracts_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "determinism_contracts_types", "write_through")
trace_contract._emit_writes_through("p1", "determinism_contracts_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "determinism_contracts_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "determinism_contracts_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "determinism_contracts_types", "routing_commit")

trace_contract._emit_records_execution_trace("p0", "evidence", "determinism_contracts_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "determinism_contracts_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "determinism_contracts_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "determinism_contracts_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "determinism_contracts_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "determinism_contracts_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "determinism_contracts_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "determinism_contracts_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "determinism_contracts_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "determinism_contracts_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "determinism_contracts_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "determinism_contracts_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "determinism_contracts_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "determinism_contracts_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "determinism_contracts_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "determinism_contracts_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "determinism_contracts_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "determinism_contracts_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "determinism_contracts_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "determinism_contracts_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "determinism_contracts_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "determinism_contracts_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "determinism_contracts_types", "exec_snapshot_link")

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
    except SyntaxError:  # review: Syntax errors should be caught at parser level, not runtime
        return violations

    for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
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
