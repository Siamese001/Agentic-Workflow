from __future__ import annotations

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

emit_replay_key("p0", "agentic_constants_util")
emit_determinism_digest("p0", "agentic_constants_util")

_emit_dispatches_healing_run("p1", "agentic_constants_util", "L1")
_emit_routes_through("p1", "agentic_constants_util", "L1")
_emit_escalates_to_human("p1", "agentic_constants_util", "L1")
_emit_reads_policy_state("p1", "agentic_constants_util", "L1")

_emit_snapshots_state("p0", "agentic_constants_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "agentic_constants_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "agentic_constants_util")
_emit_authorize_and_execute("p2", "agentic_constants_util", "execution_auth")
_emit_validates_capability("p2", "agentic_constants_util", "capability_check")
_emit_routes_to_capability("p2", "agentic_constants_util", "capability_route")
_emit_writes_via_uwg("p2", "agentic_constants_util", "uwg_write")
_emit_blocks_direct_write("p2", "agentic_constants_util", "direct_write_block")
_emit_records_tool_invocation("p2", "agentic_constants_util", "tool_invocation")
_emit_captures_execution_output("p2", "agentic_constants_util", "exec_output")
_emit_dispatches_agent("p3", "agentic_constants_util", "agent_dispatch")
_emit_coordinates_agents("p3", "agentic_constants_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "agentic_constants_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "agentic_constants_util", "healing_outcome")
_emit_escalates_failure("p3", "agentic_constants_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "agentic_constants_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agentic_constants_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "agentic_constants_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "agentic_constants_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agentic_constants_util", "eval_metric")
_emit_stores_embedding("p4", "agentic_constants_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "agentic_constants_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agentic_constants_util", "exec_snapshot_link")

"\nConstants for the Agentic Core system.\n[SSOT] Structural constants derived from structure_blueprint.py\n\nContains all shared constants used across the agentic framework.\n"
from typing import Any

from agentic_core.L0_routing.config import ROOT_PROTECTED_FILES

max_complexity: Any = 10
max_func_lines: Any = 50
max_nesting_spaces: Any = 40
allowed_root_files: Any = ROOT_PROTECTED_FILES
few_shot_strategic: Any = '\nYou are the StrategicPlannerAgent, an expert in mission planning and coordination.\n\nYour role is to:\n1. Generate comprehensive mission plans\n2. Coordinate agent execution order\n3. Allocate resources efficiently\n4. Anticipate potential issues\n\nMission Plan Structure:\n{\n    "mission_id": "unique_identifier",\n    "cycle_id": 1,\n    "priority": "HIGH|MEDIUM|LOW",\n    "objective": "Clear mission objective",\n    "phases": [...],\n    "risk_assessment": {...}\n}\n'
few_shot_sherlock: Any = "\nYou are Sherlock, the debugging specialist.\n\nYour role is to:\n1. Analyze code issues systematically\n2. Identify root causes\n3. Propose targeted fixes\n4. Verify fix effectiveness\n\nDebugging Process:\n1. Gather evidence (logs, stack traces)\n2. Formulate hypotheses\n3. Test hypotheses\n4. Implement solution\n"
few_shot_concurrency: Any = "\nYou are the ConcurrencyGuardianAgent, an expert in managing concurrent operations.\n\nYour role is to:\n1. Prevent race conditions\n2. Manage resource locks\n3. Detect deadlocks\n4. Ensure thread safety\n\nLock Usage Pattern:\n1. Acquire lock with timeout\n2. Execute critical section\n3. Always release in finally block\n4. Use async/await for I/O operations\n"
max_phase_time: Any = 300
memory_threshold_mb: Any = 100
performance_degradation_threshold: Any = 0.5
default_lock_timeout: Any = 30
max_retry_attempts: Any = 3
retry_delay: Any = 0.5
max_snapshots: Any = 100
benchmark_history_size: Any = 1000
max_alerts_per_type: Any = 50
canon_remote_repo: Any = "CANON_REMOTE_REPO"
google_api_key: Any = "GOOGLE_API_KEY"
enable_fuzz: Any = "ENABLE_FUZZ"
additional_repo_roots: Any = "ADDITIONAL_REPO_ROOTS"
memory_dir: Any = "observability/memory"
alerts_dir: Any = "observability/alerts"
cache_dir: Any = "observability/cache"
