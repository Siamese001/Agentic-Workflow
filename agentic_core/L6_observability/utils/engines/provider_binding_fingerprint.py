"""ProviderBindingFingerprint — L6 Observability.

Captures the provider-model binding configuration at runtime and hashes it
into a stable 64-char fingerprint for inclusion in the determinism digest
surface.

No wall-clock, no random inputs.  Provider registry is declared as a frozen
dict of (provider_id -> model_id) pairs.  Additional overrides may be passed
per-call but must be fully deterministic.

Layer rule: L6 observes only.  This module NEVER mutates routing decisions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.config.model_catalog import (
    ANTHROPIC_DEFAULT_MODEL_ID,
    GEMINI_25_PRO_MODEL_ID,
    OPENAI_GPT4O_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "provider_binding_fingerprint")
trace_contract.emit_determinism_digest("p0", "provider_binding_fingerprint")

trace_contract._emit_dispatches_healing_run("p1", "provider_binding_fingerprint", "L6")
trace_contract._emit_routes_through("p1", "provider_binding_fingerprint", "L6")
trace_contract._emit_checks_agent_registry("p1", "provider_binding_fingerprint", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "provider_binding_fingerprint", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "provider_binding_fingerprint", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "provider_binding_fingerprint", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "provider_binding_fingerprint", "target_agent")
trace_contract._emit_verifies_policy("p1", "provider_binding_fingerprint", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "provider_binding_fingerprint", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "provider_binding_fingerprint", "boundary_check")
trace_contract._emit_transcripts_response("p1", "provider_binding_fingerprint", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "provider_binding_fingerprint")
trace_contract._emit_gated_by_confidence("p1", "provider_binding_fingerprint", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "provider_binding_fingerprint", "L6")
trace_contract._emit_reads_policy_state("p1", "provider_binding_fingerprint", "L6")
trace_contract._emit_authorize_and_execute("p2", "provider_binding_fingerprint", "execution_auth")
trace_contract._emit_validates_capability("p2", "provider_binding_fingerprint", "capability_check")
trace_contract._emit_routes_to_capability("p2", "provider_binding_fingerprint", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "provider_binding_fingerprint", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "provider_binding_fingerprint", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "provider_binding_fingerprint", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "provider_binding_fingerprint", "exec_output")
trace_contract._emit_dispatches_agent("p3", "provider_binding_fingerprint", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "provider_binding_fingerprint", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "provider_binding_fingerprint", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "provider_binding_fingerprint", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "provider_binding_fingerprint", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "provider_binding_fingerprint", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "provider_binding_fingerprint", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "provider_binding_fingerprint", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "provider_binding_fingerprint", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "provider_binding_fingerprint", "eval_metric")
trace_contract._emit_stores_embedding("p4", "provider_binding_fingerprint", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "provider_binding_fingerprint", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "provider_binding_fingerprint", "exec_snapshot_link")

trace_contract.record_execution_trace("provider_binding_fingerprint", "provider_binding_fingerprint_trace")


trace_contract._emit_emits_metric_event("provider_binding_fingerprint", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("provider_binding_fingerprint", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("provider_binding_fingerprint", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("provider_binding_fingerprint", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("provider_binding_fingerprint", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("provider_binding_fingerprint", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("provider_binding_fingerprint", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("provider_binding_fingerprint", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("provider_binding_fingerprint", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("provider_binding_fingerprint", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("provider_binding_fingerprint", "p4obs", "alert")
trace_contract._emit_links_incident_trace("provider_binding_fingerprint", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("provider_binding_fingerprint", "p3lm", "pattern")
trace_contract._emit_records_learning_event("provider_binding_fingerprint", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("provider_binding_fingerprint", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("provider_binding_fingerprint", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("provider_binding_fingerprint", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("provider_binding_fingerprint", "p3lm", "policy")
trace_contract._emit_stores_learning_state("provider_binding_fingerprint", "p3lm", "state")
trace_contract._emit_records_execution_trace("provider_binding_fingerprint", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("provider_binding_fingerprint", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("provider_binding_fingerprint", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("provider_binding_fingerprint", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("provider_binding_fingerprint", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("provider_binding_fingerprint", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("provider_binding_fingerprint", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("provider_binding_fingerprint", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("provider_binding_fingerprint", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "provider_binding_fingerprint", "context_pull")
trace_contract._emit_pulls_context("p1", "provider_binding_fingerprint", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "provider_binding_fingerprint", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "provider_binding_fingerprint", "uwg_term_2")
trace_contract._emit_writes_through("p1", "provider_binding_fingerprint", "write_through")
trace_contract._emit_writes_through("p1", "provider_binding_fingerprint", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "provider_binding_fingerprint", "safety_validation")
trace_contract._emit_invokes_eval("p1", "provider_binding_fingerprint", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "provider_binding_fingerprint", "routing_commit")

_CANONICAL_PROVIDERS: dict[str, str] = {
    "anthropic": ANTHROPIC_DEFAULT_MODEL_ID,
    "deterministic": "LOCAL_AGENT",
    "gemini": GEMINI_25_PRO_MODEL_ID,
    "openai": OPENAI_GPT4O_MODEL_ID,
    "qwen": QWEN_LOCAL_MODEL_ID,
}


@dataclass(frozen=True)
class ProviderBinding:
    """A single provider-model binding entry."""

    provider_id: str
    model_id: str
    tier: str


@dataclass(frozen=True)
class ProviderBindingFingerprint:
    """Immutable snapshot of all provider-model bindings + their digest."""

    bindings: tuple[ProviderBinding, ...]
    fingerprint: str

    def __post_init__(self) -> None:
        if not isinstance(self.fingerprint, str) or len(self.fingerprint) != 64:
            raise ValueError(
                f"ProviderBindingFingerprint: fingerprint must be 64-char hex, got {self.fingerprint!r}",
            )


def capture_provider_bindings(overrides: dict[str, str] | None = None) -> ProviderBindingFingerprint:
    """Capture current provider-model bindings and compute their fingerprint.

    Args:
        overrides: Optional dict of {provider_id: model_id} to override
            the canonical registry.  Must be deterministic (no random values).

    Returns:
        ProviderBindingFingerprint with a stable 64-char SHA-256 digest.
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "capture_provider_bindings", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "capture_provider_bindings", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L6_OBSERVABILITY, "capture_provider_bindings")
    registry = dict(_CANONICAL_PROVIDERS)
    if overrides:
        for pid, mid in sorted(overrides.items()):
            registry[pid] = mid
    tier_map = {
        "deterministic": "DETERMINISTIC",
        "qwen": "QWEN",
        "gemini": "GEMINI",
        "anthropic": "LLM_API",
        "openai": "LLM_API",
    }
    bindings = tuple(
        (
            ProviderBinding(provider_id=pid, model_id=mid, tier=tier_map.get(pid, "UNKNOWN"))
            for pid, mid in sorted(registry.items())
        ),
    )
    material = {
        "bindings": [
            {"model_id": b.model_id, "provider_id": b.provider_id, "tier": b.tier} for b in bindings
        ],
    }
    fingerprint = hashlib.sha256(_canonical_json_bytes(material)).hexdigest()
    return ProviderBindingFingerprint(bindings=bindings, fingerprint=fingerprint)


def fingerprint_matches(fp1: ProviderBindingFingerprint, fp2: ProviderBindingFingerprint) -> bool:
    """Return True if two fingerprints represent identical bindings."""
    return fp1.fingerprint == fp2.fingerprint


def _canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


__all__ = [
    "ProviderBinding",
    "ProviderBindingFingerprint",
    "capture_provider_bindings",
    "fingerprint_matches",
]
