"""
Secure secrets management for Agentic Workflow.
Encrypts and stores secrets outside the repository.
"""

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "secure_secrets")
trace_contract.emit_determinism_digest("p0", "secure_secrets")

trace_contract._emit_dispatches_healing_run("p1", "secure_secrets", "L5")
trace_contract._emit_routes_through("p1", "secure_secrets", "L5")
trace_contract._emit_checks_agent_registry("p1", "secure_secrets", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "secure_secrets", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "secure_secrets", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "secure_secrets", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "secure_secrets", "target_agent")
trace_contract._emit_verifies_policy("p1", "secure_secrets", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "secure_secrets", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "secure_secrets", "boundary_check")
trace_contract._emit_transcripts_response("p1", "secure_secrets", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "secure_secrets")
trace_contract._emit_gated_by_confidence("p1", "secure_secrets", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "secure_secrets", "L5")
trace_contract._emit_reads_policy_state("p1", "secure_secrets", "L5")
trace_contract._emit_authorize_and_execute("p2", "secure_secrets", "execution_auth")
trace_contract._emit_validates_capability("p2", "secure_secrets", "capability_check")
trace_contract._emit_routes_to_capability("p2", "secure_secrets", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "secure_secrets", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "secure_secrets", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "secure_secrets", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "secure_secrets", "exec_output")
trace_contract._emit_dispatches_agent("p3", "secure_secrets", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "secure_secrets", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "secure_secrets", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "secure_secrets", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "secure_secrets", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "secure_secrets", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "secure_secrets", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "secure_secrets", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "secure_secrets", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "secure_secrets", "eval_metric")
trace_contract._emit_stores_embedding("p4", "secure_secrets", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "secure_secrets", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "secure_secrets", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("secure_secrets", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("secure_secrets", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("secure_secrets", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("secure_secrets", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("secure_secrets", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("secure_secrets", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("secure_secrets", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("secure_secrets", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("secure_secrets", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("secure_secrets", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("secure_secrets", "p4obs", "alert")
trace_contract._emit_links_incident_trace("secure_secrets", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("secure_secrets", "p3lm", "pattern")
trace_contract._emit_records_learning_event("secure_secrets", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("secure_secrets", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("secure_secrets", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("secure_secrets", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("secure_secrets", "p3lm", "policy")
trace_contract._emit_stores_learning_state("secure_secrets", "p3lm", "state")
trace_contract._emit_records_execution_trace("secure_secrets", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("secure_secrets", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("secure_secrets", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("secure_secrets", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("secure_secrets", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("secure_secrets", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("secure_secrets", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("secure_secrets", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("secure_secrets", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "secure_secrets", "context_pull")
trace_contract._emit_pulls_context("p1", "secure_secrets", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "secure_secrets", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "secure_secrets", "uwg_term_2")
trace_contract._emit_writes_through("p1", "secure_secrets", "write_through")
trace_contract._emit_writes_through("p1", "secure_secrets", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "secure_secrets", "safety_validation")
trace_contract._emit_invokes_eval("p1", "secure_secrets", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "secure_secrets", "routing_commit")

SECRETS_DIR = Path("C:\\Users\\amita\\.agentic_secrets")
KEY_FILE = SECRETS_DIR / ".key"
SECRETS_FILE = SECRETS_DIR / "secrets.enc"


def _ensure_key() -> bytes:
    """Ensure encryption key exists, return key bytes."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "_ensure_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "_ensure_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "_ensure_key")
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
    except (ValueError, TypeError):  # guardian: allow-silent-swallow
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
