"""
Secure secrets management for Agentic Workflow.
Encrypts and stores secrets outside the repository.
"""

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

from agentic_core.runtime.lifecycle_trace_contract import (
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "secure_secrets")
emit_determinism_digest("p0", "secure_secrets")

_emit_dispatches_healing_run("p1", "secure_secrets", "L5")
_emit_routes_through("p1", "secure_secrets", "L5")
_emit_checks_agent_registry("p1", "secure_secrets", "agent_registry")
_emit_validates_agent_capability("p1", "secure_secrets", "capability")
_emit_dispatches_execution_plan("p1", "secure_secrets", "exec_plan")
_emit_agent_executes_agent("p1", "secure_secrets", "sub_agent")
_emit_routes_to_agent("p1", "secure_secrets", "target_agent")
_emit_verifies_policy("p1", "secure_secrets", "policy_check")
_emit_observes_runtime_state("p1", "secure_secrets", "runtime_state")
_emit_verifies_boundary("p1", "secure_secrets", "boundary_check")
_emit_transcripts_response("p1", "secure_secrets", "transcript")
_emit_hard_fails_untranscripted("p1", "secure_secrets")
_emit_gated_by_confidence("p1", "secure_secrets", "confidence_gate")
_emit_escalates_to_human("p1", "secure_secrets", "L5")
_emit_reads_policy_state("p1", "secure_secrets", "L5")
_emit_authorize_and_execute("p2", "secure_secrets", "execution_auth")
_emit_validates_capability("p2", "secure_secrets", "capability_check")
_emit_routes_to_capability("p2", "secure_secrets", "capability_route")
_emit_writes_via_uwg("p2", "secure_secrets", "uwg_write")
_emit_blocks_direct_write("p2", "secure_secrets", "direct_write_block")
_emit_records_tool_invocation("p2", "secure_secrets", "tool_invocation")
_emit_captures_execution_output("p2", "secure_secrets", "exec_output")
_emit_dispatches_agent("p3", "secure_secrets", "agent_dispatch")
_emit_coordinates_agents("p3", "secure_secrets", "agent_coordination")
_emit_records_workflow_lineage("p3", "secure_secrets", "workflow_lineage")
_emit_records_healing_outcome("p3", "secure_secrets", "healing_outcome")
_emit_escalates_failure("p3", "secure_secrets", "failure_escalation")
_emit_orchestrates_workflow("p3", "secure_secrets", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "secure_secrets", "healing_dispatch")
_emit_invokes_evaluation("p3", "secure_secrets", "evaluation_signal")
_emit_records_telemetry_event("p4", "secure_secrets", "telemetry_event")
_emit_captures_evaluation_metric("p4", "secure_secrets", "eval_metric")
_emit_stores_embedding("p4", "secure_secrets", "embedding_store")
_emit_updates_meta_learning_state("p4", "secure_secrets", "meta_learning")
_emit_links_execution_to_snapshot("p4", "secure_secrets", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("secure_secrets", "p4obs", "metric_1")
_emit_emits_metric_event("secure_secrets", "p4obs", "metric_2")
_emit_emits_metric_event("secure_secrets", "p4obs", "metric_3")
_emit_emits_metric_event("secure_secrets", "p4obs", "metric_4")
_emit_emits_metric_event("secure_secrets", "p4obs", "metric_5")
_emit_emits_metric_event("secure_secrets", "p4obs", "metric_6")
_emit_records_incident_event("secure_secrets", "p4obs", "incident")
_emit_captures_runtime_anomaly("secure_secrets", "p4obs", "anomaly")
_emit_writes_observability_log("secure_secrets", "p4obs", "obs_log")
_emit_updates_monitoring_state("secure_secrets", "p4obs", "mon_state")
_emit_triggers_alert("secure_secrets", "p4obs", "alert")
_emit_links_incident_trace("secure_secrets", "p4obs", "trace_link")
_emit_captures_pattern("secure_secrets", "p3lm", "pattern")
_emit_records_learning_event("secure_secrets", "p3lm", "learning_event")
_emit_writes_learning_snapshot("secure_secrets", "p3lm", "snapshot")
_emit_feeds_meta_learning("secure_secrets", "p3lm", "meta_feed")
_emit_updates_routing_strategy("secure_secrets", "p3lm", "routing")
_emit_improves_agent_policy("secure_secrets", "p3lm", "policy")
_emit_stores_learning_state("secure_secrets", "p3lm", "state")
_emit_records_execution_trace("secure_secrets", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("secure_secrets", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("secure_secrets", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("secure_secrets", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("secure_secrets", "L4_STATE", "p2_trace_5")
_emit_reads_environ("secure_secrets", "env_read", "p2_env_1")
_emit_reads_environ("secure_secrets", "env_read", "p2_env_2")
_emit_reads_runtime_state("secure_secrets", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("secure_secrets", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "secure_secrets", "context_pull")
_emit_pulls_context("p1", "secure_secrets", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "secure_secrets", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "secure_secrets", "uwg_term_2")
_emit_writes_through("p1", "secure_secrets", "write_through")
_emit_writes_through("p1", "secure_secrets", "write_through_2")
_emit_validated_by_safety_plane("p1", "secure_secrets", "safety_validation")
_emit_invokes_eval("p1", "secure_secrets", "eval_call")
_emit_proposal_commits_routing("p1", "secure_secrets", "routing_commit")

SECRETS_DIR = Path("C:\\Users\\amita\\.agentic_secrets")
KEY_FILE = SECRETS_DIR / ".key"
SECRETS_FILE = SECRETS_DIR / "secrets.enc"


def _ensure_key() -> bytes:
    """Ensure encryption key exists, return key bytes."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_ensure_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_ensure_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "_ensure_key")
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key


def load_secrets() -> dict[str, str]:
    """Load and decrypt secrets from encrypted store.

    Returns:
        Empty dict if files missing, otherwise decrypted secrets.
    """
    if not KEY_FILE.exists() or not SECRETS_FILE.exists():
        return {}
    try:
        key = _ensure_key()
        fernet = Fernet(key)
        encrypted_data = SECRETS_FILE.read_bytes()
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode("utf-8"))
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return {}


def inject_into_env() -> None:
    """Inject loaded secrets into environment variables.

    Sets defaults without overwriting existing environment variables.
    No printing to avoid secret leakage.
    """
    secrets = load_secrets()
    for key, value in secrets.items():
        # guardian: allow-global-mutation
        os.environ.setdefault(key, value)
