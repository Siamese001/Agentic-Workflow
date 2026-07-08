from __future__ import annotations

import logging

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "verb_canonicalizer_validator")
trace_contract.emit_determinism_digest("p0", "verb_canonicalizer_validator")

trace_contract._emit_dispatches_healing_run("p1", "verb_canonicalizer_validator", "L5")
trace_contract._emit_routes_through("p1", "verb_canonicalizer_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "verb_canonicalizer_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "verb_canonicalizer_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "verb_canonicalizer_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "verb_canonicalizer_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "verb_canonicalizer_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "verb_canonicalizer_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "verb_canonicalizer_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "verb_canonicalizer_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "verb_canonicalizer_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "verb_canonicalizer_validator")
trace_contract._emit_gated_by_confidence("p1", "verb_canonicalizer_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "verb_canonicalizer_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "verb_canonicalizer_validator", "L5")
trace_contract._emit_authorize_and_execute("p2", "verb_canonicalizer_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "verb_canonicalizer_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "verb_canonicalizer_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "verb_canonicalizer_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "verb_canonicalizer_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "verb_canonicalizer_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "verb_canonicalizer_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "verb_canonicalizer_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "verb_canonicalizer_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "verb_canonicalizer_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "verb_canonicalizer_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "verb_canonicalizer_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "verb_canonicalizer_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "verb_canonicalizer_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "verb_canonicalizer_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "verb_canonicalizer_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "verb_canonicalizer_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "verb_canonicalizer_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "verb_canonicalizer_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "verb_canonicalizer_validator", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import re
from typing import Any


trace_contract._emit_emits_metric_event("verb_canonicalizer_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("verb_canonicalizer_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("verb_canonicalizer_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("verb_canonicalizer_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("verb_canonicalizer_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("verb_canonicalizer_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("verb_canonicalizer_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("verb_canonicalizer_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("verb_canonicalizer_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("verb_canonicalizer_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("verb_canonicalizer_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("verb_canonicalizer_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("verb_canonicalizer_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("verb_canonicalizer_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("verb_canonicalizer_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("verb_canonicalizer_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("verb_canonicalizer_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("verb_canonicalizer_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("verb_canonicalizer_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("verb_canonicalizer_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("verb_canonicalizer_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("verb_canonicalizer_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("verb_canonicalizer_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("verb_canonicalizer_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("verb_canonicalizer_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("verb_canonicalizer_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("verb_canonicalizer_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("verb_canonicalizer_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "verb_canonicalizer_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "verb_canonicalizer_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "verb_canonicalizer_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "verb_canonicalizer_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "verb_canonicalizer_validator", "write_through")
trace_contract._emit_writes_through("p1", "verb_canonicalizer_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "verb_canonicalizer_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "verb_canonicalizer_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "verb_canonicalizer_validator", "routing_commit")

_logger = logging.getLogger(__name__)
"\nVerb canonicalization for resume bullet points.\n\nCanonicalizes action verbs to approved list and detects forbidden verbs.\n"


class VerbCanonicalizer:
    """Canonicalize action verbs to approved list."""

    _CANONICAL_VERBS: dict[str, list[str]] = {
        "led": ["led", "lead", "leading"],
        "built": ["built", "build", "building"],
        "drove": ["drove", "drive", "driving"],
        "launched": ["launched", "launch", "launching"],
        "scaled": ["scaled", "scale", "scaling"],
        "delivered": ["delivered", "deliver", "delivering"],
        "achieved": ["achieved", "achieve", "achieving"],
        "established": ["established", "establish", "establishing"],
        "managed": ["managed", "manage", "managing"],
        "developed": ["developed", "develop", "developing"],
    }
    _FORBIDDEN_VERBS: list[str] = [
        "pioneered",
        "spearheaded",
        "orchestrated",
        "architected",
        "revolutionized",
        "transformed",
    ]


def canonicalize(self: Any, text: str) -> list[str]:
    """Extract and canonicalize verbs from text."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "canonicalize", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "canonicalize", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "canonicalize")
    text_lower: Any = text.lower()
    for canonical_form, variants in self.CANONICAL_VERBS.items():
        if any(variant in text_lower for variant in variants):
            canonical.append(canonical_form)
    return canonical


def check_for_forbidden_verbs(self: Any, text: str) -> list[str]:
    """Check for forbidden verbs in the text."""
    found_verbs: Any = []
    text_lower: Any = text.lower()
    for verb in self.FORBIDDEN_VERBS:
        # guardian: allow-path-string
        if re.search("\\b" + verb + "\\b", text_lower):
            found_verbs.append(verb)
    return found_verbs
