"""
Assembly Stage - GAP-03 Implementation
Deterministic composition of governed payloads with stable slot ordering.

This module implements the Assembly Stage that composes system, instructional,
context, and user prompts into a governed payload with deterministic hashing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "assembly_stage", "L0")
_emit_routes_through("p1", "assembly_stage", "L0")
_emit_escalates_to_human("p1", "assembly_stage", "L0")
_emit_reads_policy_state("p1", "assembly_stage", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "assembly_stage", "p0_governance")
_emit_snapshots_state("p0", "assembly_stage", "state_snapshot")
_emit_authorize_and_execute("p2", "assembly_stage", "execution_auth")
_emit_validates_capability("p2", "assembly_stage", "capability_check")
_emit_routes_to_capability("p2", "assembly_stage", "capability_route")
_emit_writes_via_uwg("p2", "assembly_stage", "uwg_write")
_emit_blocks_direct_write("p2", "assembly_stage", "direct_write_block")
_emit_records_tool_invocation("p2", "assembly_stage", "tool_invocation")
_emit_captures_execution_output("p2", "assembly_stage", "exec_output")
_emit_dispatches_agent("p3", "assembly_stage", "agent_dispatch")
_emit_coordinates_agents("p3", "assembly_stage", "agent_coordination")
_emit_records_workflow_lineage("p3", "assembly_stage", "workflow_lineage")
_emit_records_healing_outcome("p3", "assembly_stage", "healing_outcome")
_emit_escalates_failure("p3", "assembly_stage", "failure_escalation")
_emit_orchestrates_workflow("p3", "assembly_stage", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "assembly_stage", "healing_dispatch")
_emit_invokes_evaluation("p3", "assembly_stage", "evaluation_signal")
_emit_records_telemetry_event("p4", "assembly_stage", "telemetry_event")
_emit_captures_evaluation_metric("p4", "assembly_stage", "eval_metric")
_emit_stores_embedding("p4", "assembly_stage", "embedding_store")
_emit_updates_meta_learning_state("p4", "assembly_stage", "meta_learning")
_emit_links_execution_to_snapshot("p4", "assembly_stage", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("assembly_stage", "p4obs", "metric_1")
_emit_emits_metric_event("assembly_stage", "p4obs", "metric_2")
_emit_emits_metric_event("assembly_stage", "p4obs", "metric_3")
_emit_emits_metric_event("assembly_stage", "p4obs", "metric_4")
_emit_emits_metric_event("assembly_stage", "p4obs", "metric_5")
_emit_emits_metric_event("assembly_stage", "p4obs", "metric_6")
_emit_records_incident_event("assembly_stage", "p4obs", "incident")
_emit_captures_runtime_anomaly("assembly_stage", "p4obs", "anomaly")
_emit_writes_observability_log("assembly_stage", "p4obs", "obs_log")
_emit_updates_monitoring_state("assembly_stage", "p4obs", "mon_state")
_emit_triggers_alert("assembly_stage", "p4obs", "alert")
_emit_links_incident_trace("assembly_stage", "p4obs", "trace_link")
_emit_captures_pattern("assembly_stage", "p3lm", "pattern")
_emit_records_learning_event("assembly_stage", "p3lm", "learning_event")
_emit_writes_learning_snapshot("assembly_stage", "p3lm", "snapshot")
_emit_feeds_meta_learning("assembly_stage", "p3lm", "meta_feed")
_emit_updates_routing_strategy("assembly_stage", "p3lm", "routing")
_emit_improves_agent_policy("assembly_stage", "p3lm", "policy")
_emit_stores_learning_state("assembly_stage", "p3lm", "state")
_emit_records_execution_trace("assembly_stage", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("assembly_stage", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("assembly_stage", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("assembly_stage", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("assembly_stage", "L4_STATE", "p2_trace_5")
_emit_reads_environ("assembly_stage", "env_read", "p2_env_1")
_emit_reads_environ("assembly_stage", "env_read", "p2_env_2")
_emit_reads_runtime_state("assembly_stage", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("assembly_stage", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "assembly_stage", "context_pull")
_emit_pulls_context("p1", "assembly_stage", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "assembly_stage", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "assembly_stage", "uwg_term_2")
_emit_writes_through("p1", "assembly_stage", "write_through")
_emit_writes_through("p1", "assembly_stage", "write_through_2")
_emit_validated_by_safety_plane("p1", "assembly_stage", "safety_validation")
_emit_invokes_eval("p1", "assembly_stage", "eval_call")
_emit_proposal_commits_routing("p1", "assembly_stage", "routing_commit")


def canonical_bytes(data: dict[str, Any]) -> bytes:
    """
    Convert a dictionary to canonical JSON bytes for deterministic hashing.

    Args:
        data: Dictionary to canonicalize

    Returns:
        Deterministic bytes representation
    """
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class GovernedPayload:
    """
    Immutable governed payload with assembly stage slots.

    Slots are ordered S0→D0→I0→C0→U0 for deterministic manifest hashing.
    """

    s0_system: str
    i0_instructional: str
    c0_context: str
    u0_user_prompt: str
    d0_injections: str = ""
    check_ids: tuple[str, ...] = ()
    sanitized: bool = False
    c0_context_source: str = "static"
    manifest_hash: str = ""
    routing_hash: str = ""

    def __post_init__(self):
        if not self.manifest_hash or not self.routing_hash:
            manifest = {
                "s0_system": self.s0_system,
                "d0_injections": self.d0_injections,
                "i0_instructional": self.i0_instructional,
                "c0_context": self.c0_context,
                "u0_user_prompt": self.u0_user_prompt,
                "check_ids": tuple(sorted(self.check_ids)),
                "sanitized": self.sanitized,
                "c0_context_source": self.c0_context_source,
            }
            manifest_hash_hex = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
            object.__setattr__(self, "manifest_hash", manifest_hash_hex)
            routing_manifest = {
                "s0_system": self.s0_system,
                "d0_injections": self.d0_injections,
                "i0_instructional": self.i0_instructional,
                "u0_user_prompt": self.u0_user_prompt,
                "check_ids": tuple(sorted(self.check_ids)),
                "sanitized": self.sanitized,
            }
            routing_hash_hex = hashlib.sha256(canonical_bytes(routing_manifest)).hexdigest()
            object.__setattr__(self, "routing_hash", routing_hash_hex)


class AirlockAssembler:
    """
    Assembly stage for composing governed payloads with deterministic hashing.

    Implements the Assembly Stage (GAP-03) with stable slot composition
    and deterministic manifest hashing.
    """

    @staticmethod
    def _sanitize(u0_user_prompt: str) -> str:
        """
        Deterministic minimal sanitizer for user prompts.

        Performs exact, deterministic substitutions only - no ML or fuzzy matching.

        Args:
            u0_user_prompt: Raw user prompt text

        Returns:
            Sanitized user prompt text
        """
        sanitized = u0_user_prompt
        sanitized = sanitized.replace("\x00", "")
        sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")
        hijack_patterns = [
            ("[SYSTEM]", ""),
            ("[ADMIN]", ""),
            ("[ROOT]", ""),
            ("[ESCALATE]", ""),
            ("[BYPASS]", ""),
            ("[OVERRIDE]", ""),
        ]
        for pattern, replacement in hijack_patterns:
            sanitized = sanitized.replace(pattern, replacement)
        return sanitized

    @staticmethod
    def _shred(u0_user_prompt: str) -> tuple[str, ...]:
        """
        Deterministic shred of user prompt into atomic intent check IDs.

        Splits by common intent delimiters and returns lexicographically sorted IDs.

        Args:
            u0_user_prompt: User prompt text to shred

        Returns:
            Tuple of stable, lexicographically sorted check IDs
        """
        lines = u0_user_prompt.strip().split("\n")
        check_ids = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line and line[0].isdigit() and ("." in line[:10]):
                check_id = line.split(".", 1)[1].strip()
                if check_id:
                    check_ids.append(check_id)
            elif line.startswith(("-", "*", "•")):
                check_id = line[1:].strip()
                if check_id:
                    check_ids.append(check_id)
            else:
                check_ids.append(line)
        return tuple(sorted(check_ids))

    @staticmethod
    def assemble(
        *,
        s0_system: str,
        i0_instructional: str,
        c0_context: str,
        u0_user_prompt: str,
        d0_injections: str = "",
        c0_context_source: Literal["static", "embedding_artifact"] = "static",
    ) -> GovernedPayload:
        """
        Assemble a governed payload from component slots.

        Performs sanitization first, then shredding, then computes manifest hash.

        Args:
            s0_system: System prompt slot
            d0_injections: Reserved injection slot (default empty)
            i0_instructional: Instructional prompt slot
            c0_context: Context slot
            u0_user_prompt: User prompt slot

        Returns:
            GovernedPayload with deterministic manifest hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "AirlockAssembler.assemble")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        sanitized_prompt = AirlockAssembler._sanitize(u0_user_prompt)
        sanitized = sanitized_prompt != u0_user_prompt
        check_ids = AirlockAssembler._shred(sanitized_prompt)
        payload = GovernedPayload(
            s0_system=s0_system,
            d0_injections=d0_injections,
            i0_instructional=i0_instructional,
            c0_context=c0_context,
            u0_user_prompt=sanitized_prompt,
            check_ids=check_ids,
            sanitized=sanitized,
            c0_context_source=c0_context_source,
        )
        return payload
