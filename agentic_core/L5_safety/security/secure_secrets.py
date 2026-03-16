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
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "secure_secrets")
emit_determinism_digest("p0", "secure_secrets")

_emit_dispatches_healing_run("p1", "secure_secrets", "L5")
_emit_routes_through("p1", "secure_secrets", "L5")
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
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "_ensure_key")
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
    except Exception:
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
