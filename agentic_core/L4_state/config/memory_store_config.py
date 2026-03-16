import os
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "memory_store_config")
emit_determinism_digest("p0", "memory_store_config")

_emit_dispatches_healing_run("p1", "memory_store_config", "L4")
_emit_routes_through("p1", "memory_store_config", "L4")
_emit_escalates_to_human("p1", "memory_store_config", "L4")
_emit_reads_policy_state("p1", "memory_store_config", "L4")

_emit_snapshots_state("p0", "memory_store_config", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "memory_store_config", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "memory_store_config")
_emit_authorize_and_execute("p2", "memory_store_config", "execution_auth")
_emit_validates_capability("p2", "memory_store_config", "capability_check")
_emit_routes_to_capability("p2", "memory_store_config", "capability_route")
_emit_writes_via_uwg("p2", "memory_store_config", "uwg_write")
_emit_blocks_direct_write("p2", "memory_store_config", "direct_write_block")
_emit_records_tool_invocation("p2", "memory_store_config", "tool_invocation")
_emit_captures_execution_output("p2", "memory_store_config", "exec_output")
_emit_dispatches_agent("p3", "memory_store_config", "agent_dispatch")
_emit_coordinates_agents("p3", "memory_store_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "memory_store_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "memory_store_config", "healing_outcome")
_emit_escalates_failure("p3", "memory_store_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "memory_store_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "memory_store_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "memory_store_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "memory_store_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "memory_store_config", "eval_metric")
_emit_stores_embedding("p4", "memory_store_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "memory_store_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "memory_store_config", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


@dataclass
class MemoryStoreConfig:
    """
    L4 Configuration: Memory Storage Parameters.
    Controls the physical and semantic limits of the Sovereign Memory.
    """

    # Vector Database (Pinecone/Chroma)
    VECTOR_DIMENSIONS: int = 1536
    VECTOR_METRIC: str = "cosine"

    # Short-Term Memory (Redis)
    STM_TTL_SECONDS: int = 3600  # 1 hour
    MAX_THOUGHTS_IN_CONTEXT: int = 50

    # Snapshotting
    ENABLE_AUTO_CHECKPOINTS: bool = True
    CHECKPOINT_INTERVAL_SECONDS: int = 300  # 5 minutes
    MAX_SNAPSHOTS_TO_RETAIN: int = 10

    # Paths
    STORAGE_ROOT: str = os.getenv("L4_STORAGE_ROOT", "./data/l4_state")


memory_config = MemoryStoreConfig()
