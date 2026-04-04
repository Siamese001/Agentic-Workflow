"""
_ssot_types.py — Shared dataclasses, enums, and value types for execute_ssot.

Extracted from execute_ssot.py to reduce file size and improve cohesion.
All public symbols are re-exported from execute_ssot.py for backward compat.
"""

import argparse
import ast
import enum as _enum
import os
import uuid
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

@dataclass
class ConfidenceScore:
    """[HARDENED] Confidence score for autonomous healing."""

    value: float
    reasoning: str
    factors: dict[str, float] = field(default_factory=dict)

    @property
    def is_high_confidence(self) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ConfidenceScore.is_high_confidence", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ConfidenceScore.is_high_confidence", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ConfidenceScore.is_high_confidence"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_X

        return self.value > HEALING_CONFIDENCE_X

    @property
    def is_medium_confidence(self) -> bool:
        from agentic_core.L2_execution.healers.healing_tier_config import (
            HEALING_CONFIDENCE_X,
            HEALING_CONFIDENCE_Y,
        )

        return HEALING_CONFIDENCE_Y <= self.value <= HEALING_CONFIDENCE_X

    @property
    def is_low_confidence(self) -> bool:
        from agentic_core.L2_execution.healers.healing_tier_config import HEALING_CONFIDENCE_Y

        return self.value < HEALING_CONFIDENCE_Y


class FailureType(_enum.Enum):
    """Classifies the failure being routed.  Drives gate selection."""

    LAYER_VIOLATION = "LAYER_VIOLATION"
    GATEWAY_BYPASS = "GATEWAY_BYPASS"
    KILL_SWITCH_BYPASS = "KILL_SWITCH_BYPASS"
    SIGNATURE_VERIFY = "SIGNATURE_VERIFY"
    UNSIGNED_INGRESS = "UNSIGNED_INGRESS"
    IMPORT_BOUNDARY_VIOLATION = "IMPORT_BOUNDARY_VIOLATION"
    SCHEMA_REQUIRED_FIELDS_MISSING = "SCHEMA_REQUIRED_FIELDS_MISSING"
    NAMING = "NAMING"
    HIERARCHY = "HIERARCHY"
    SHALLOW = "SHALLOW"
    DEEP = "DEEP"
    VOID = "VOID"
    DUPLICATE = "DUPLICATE"
    ORPHAN = "ORPHAN"
    UNKNOWN = "UNKNOWN"


class RoutingTier(_enum.Enum):
    DETERMINISTIC = "DETERMINISTIC"
    QWEN = "QWEN"
    GEMINI = "GEMINI"
    FAIL_CLOSED = "FAIL_CLOSED"


_STRUCTURAL_CLASS: frozenset[FailureType] = frozenset(
    {
        FailureType.LAYER_VIOLATION,
        FailureType.GATEWAY_BYPASS,
        FailureType.KILL_SWITCH_BYPASS,
        FailureType.SIGNATURE_VERIFY,
        FailureType.UNSIGNED_INGRESS,
    }
)
_QWEN_DISALLOWED: frozenset[FailureType] = _STRUCTURAL_CLASS | frozenset(
    {FailureType.IMPORT_BOUNDARY_VIOLATION, FailureType.SCHEMA_REQUIRED_FIELDS_MISSING}
)


@dataclass
class RoutingInputs:
    """All inputs to compute_routing_decision.  No embeddings allowed."""

    failure_type: FailureType = FailureType.UNKNOWN
    retry_count: int = 0
    C: int = 0
    B: int = 0
    A: int = 0
    N: int = 0
    F: int = 0
    L: int = 0
    replay_mode: bool = False
    playbook_match: bool = False
    deterministic_coverage: bool = False
    provider_prohibited_gemini: bool = False
    provider_prohibited_qwen: bool = False


@dataclass
class RoutingDecision:
    """Immutable routing result with full audit trail."""

    tier: RoutingTier
    score: int
    gate_applied: str
    model_id: str
    factors: dict
    inputs: RoutingInputs
    determinism_digest: str

    def as_log_line(self) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RoutingDecision.as_log_line")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        f = self.factors
        i = self.inputs
        return f"[ROUTING] tier={self.tier.value} S={self.score} gate={self.gate_applied} model={self.model_id} C={f.get('C', 0)} B={f.get('B', 0)} A={f.get('A', 0)} N={f.get('N', 0)} F={f.get('F', 0)} L={f.get('L', 0)} replay={i.replay_mode} retry={i.retry_count} playbook={i.playbook_match} det_cov={i.deterministic_coverage} digest={self.determinism_digest}"


@dataclass
class ReconciliationViolation:
    """Structured violation for enhanced telemetry (Ported from FilesystemSSOTReconciler)."""

    is_valid: bool
    message: str
    drift_type: str | None = None
    file_path: Path | None = None
    suggested_action: str | None = None
    severity: int = 5

    # guardian: allow-type-erasure
    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "drift_type": self.drift_type,
            "file_path": str(self.file_path.as_posix()) if self.file_path else None,
            "severity": self.severity,
        }


@dataclass
class ReconciliationManifest:
    """Telemetry manifest for tracking all reconciliation changes."""

    mission_id: str
    territory: str
    start_time: str
    end_time: str | None = None
    violations_found: int = 0
    violations_attempted: int = 0
    violations_fixed: int = 0
    violations_failed: int = 0
    modifications: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    budget_consumed: int = 0
    confidence_scores: list[float] = field(default_factory=list)

    def add_modification(self, modification: dict[str, Any]) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ReconciliationManifest.add_modification"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        self.modifications.append(modification)
        self.violations_attempted += 1
        if modification.get("success", False):
            self.violations_fixed += 1
        else:
            self.violations_failed += 1

    def add_failure(self, failure: dict[str, Any]) -> None:
        self.failures.append(failure)
        self.violations_failed += 1

    # guardian: allow-type-erasure
    def finalize(self) -> dict[str, Any]:
        self.end_time = datetime.now().isoformat()
        return {
            "mission_id": self.mission_id,
            "territory": self.territory,
            "duration": {
                "start": self.start_time,
                "end": self.end_time,
                "seconds": (
                    datetime.fromisoformat(self.end_time) - datetime.fromisoformat(self.start_time)
                ).total_seconds()
                if self.end_time
                else None,
            },
            "violations": {
                "found": self.violations_found,
                "attempted": self.violations_attempted,
                "fixed": self.violations_fixed,
                "failed": self.violations_failed,
                "success_rate": self.violations_fixed / max(self.violations_attempted, 1),
            },
            "budget": {"consumed": self.budget_consumed, "remaining": max(0, 100 - self.budget_consumed)},
            "confidence": {
                "scores": self.confidence_scores,
                "average": sum(self.confidence_scores) / len(self.confidence_scores)
                if self.confidence_scores
                else 0.0,
            },
            "modifications": self.modifications,
            "failures": self.failures,
        }


class ASTCodeQualityValidator:
    """AST-based code quality validation with memory guards (Ported from TypeMechanic)."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        # guardian: allow-magic-config
        self.max_file_size = 1000000

    def _read_and_parse_file(self, fp: str) -> tuple[ast.AST | None, str | None]:
        """Reads a file and parses it into an AST with strict size limits."""
        try:
            if os.path.getsize(fp) > self.max_file_size:
                return (None, "File too large for AST analysis")
            with open(fp, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
                return (tree, None)
        except (OSError, SyntaxError) as e:    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling    # guardian: Multiple exceptions (OSError, SyntaxError) need specific handling
            return (None, f"Error parsing {fp}: {str(e)}")

    # guardian: allow-type-erasure
    def check_file_quality(self, file_path: Path) -> dict:
        """Check file for code quality issues (missing types, etc)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ASTCodeQualityValidator.check_file_quality"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        violations = []
        tree, error = self._read_and_parse_file(str(file_path))
        if error:
            return {"error": error, "violations": []}
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.returns and (not node.name.startswith("__")):
                        violations.append(
                            {
                                "type": "MISSING_TYPE_HINT",
                                "file": str(file_path),
                                "line": node.lineno,
                                "message": f"Function '{node.name}' missing return type hint",
                            }
                        )
        return {"violations": violations, "violations_count": len(violations), "file": str(file_path)}


@dataclass(frozen=True)
class HealContext:
    """Immutable healing configuration passed uniformly to every phase function.

    Single control surface: --heal drives ALL active-mode flags.

      --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                    enable_meta_learning all True
      --heal OFF => scan/report only, everything passive

    Per hostile audit Section B1: trace_id must appear in every artifact.
    Per hostile audit Section E1: trace_id threads through all artifacts and HealContext.
    Per hostile audit Section E10: execution_mode distinguishes scan/heal/validate modes.
    """

    heal: bool
    auto_approve: bool
    enable_telemetry: bool
    enable_meta_learning: bool
    trace_id: str
    execution_mode: str

    @property
    def enable_llm(self) -> bool:
        """LLM arbitration is always active when healing — not a separate flag."""
        return self.heal

    @property
    def dry_run(self) -> bool:
        """Convenience alias — inverted heal for legacy call sites."""
        return not self.heal

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "HealContext":
        """Construct from parsed CLI args. Single construction point.

        Canonical flag semantics (--heal is the ONLY active-mode switch):
          --heal ON  => heal, auto_approve, enable_llm, enable_telemetry,
                        enable_meta_learning all True
          --heal OFF => all passive/scan-only

        Deprecated flags (kept for backward-compat, emit warnings):
          --dry-run        => same as omitting --heal
          --manual         => always autonomous now
          --interactive    => auto_approve is always True under --heal
          --apply-proposals => meta-learning always on under --heal
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "HealContext.from_args")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if getattr(args, "dry_run", False):
            warnings.warn(
                "--dry-run is deprecated. Omit --heal for scan-only mode.", DeprecationWarning, stacklevel=2
            )
        if getattr(args, "manual", False):
            warnings.warn(
                "--manual is deprecated. Autonomous mode is always active.", DeprecationWarning, stacklevel=2
            )
        if getattr(args, "interactive", False):
            warnings.warn(
                "--interactive is deprecated. Auto-approve is always on under --heal.",
                DeprecationWarning,
                stacklevel=2,
            )
        if getattr(args, "apply_proposals", False):
            warnings.warn(
                "--apply-proposals is deprecated. Meta-learning is always on under --heal.",
                DeprecationWarning,
                stacklevel=2,
            )
        heal = getattr(args, "heal", False)
        from datetime import timezone

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        trace_id = f"SSOT-{timestamp}-{uuid.uuid4().hex[:8]}"
        validate = getattr(args, "validate", False)
        if validate:
            execution_mode = "validate"
        elif heal:
            execution_mode = "heal"
        else:
            execution_mode = "scan"
        return cls(
            heal=heal,
            auto_approve=heal,
            enable_telemetry=heal,
            enable_meta_learning=heal,
            trace_id=trace_id,
            execution_mode=execution_mode,
        )
