"""Shared Active Set Helper — Single Import Point.

Provides a canonical function to enumerate the ACTIVE agent set using
the same pipeline as full_agent_discovery's perform_deep_integrity_scan.

All CI gates that need the ACTIVE set MUST use this helper to prevent
definition divergence.

Usage:
    from ops_scripts.ci.active_set_helper import get_active_set

    result = get_active_set(project_root)
    print(result.count, result.fingerprint)
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_records_execution_trace("p0", "evidence", "active_set_helper")
_emit_applies_guardrail("p0", "active_set_helper", "p0_governance")
_emit_reads_policy_state("p0", "active_set_helper", "policy_binding")
_emit_snapshots_state("p0", "active_set_helper", "state_snapshot")
emit_replay_key("p0", "active_set_helper")
emit_determinism_digest("p0", "active_set_helper")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "active_set_helper", "execution_auth")
_emit_validates_capability("p2", "active_set_helper", "capability_check")
_emit_routes_to_capability("p2", "active_set_helper", "capability_route")
_emit_writes_via_uwg("p2", "active_set_helper", "uwg_write")
_emit_blocks_direct_write("p2", "active_set_helper", "direct_write_block")
_emit_records_tool_invocation("p2", "active_set_helper", "tool_invocation")
_emit_captures_execution_output("p2", "active_set_helper", "exec_output")
_emit_dispatches_agent("p3", "active_set_helper", "agent_dispatch")
_emit_coordinates_agents("p3", "active_set_helper", "agent_coordination")
_emit_records_workflow_lineage("p3", "active_set_helper", "workflow_lineage")
_emit_records_healing_outcome("p3", "active_set_helper", "healing_outcome")
_emit_escalates_failure("p3", "active_set_helper", "failure_escalation")
_emit_orchestrates_workflow("p3", "active_set_helper", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "active_set_helper", "healing_dispatch")
_emit_invokes_evaluation("p3", "active_set_helper", "evaluation_signal")
_emit_records_telemetry_event("p4", "active_set_helper", "telemetry_event")
_emit_captures_evaluation_metric("p4", "active_set_helper", "eval_metric")
_emit_stores_embedding("p4", "active_set_helper", "embedding_store")
_emit_updates_meta_learning_state("p4", "active_set_helper", "meta_learning")
_emit_links_execution_to_snapshot("p4", "active_set_helper", "exec_snapshot_link")

@dataclass(frozen=True)
class ActiveSetResult:
    """Immutable result of active set enumeration."""
    agents: tuple[dict[str, Any], ...]
    agent_ids: tuple[str, ...]
    count: int
    fingerprint: str
    stats: dict[str, int] = field(default_factory=dict)

def _compute_fingerprint(sorted_ids: tuple[str, ...]) -> str:
    """SHA-256 of newline-joined sorted agent IDs."""
    payload = '\n'.join(sorted_ids).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def get_active_set(project_root: Path) -> ActiveSetResult:
    """Return the canonical ACTIVE agent set.

    Pipeline: load_agent_discovery → perform_deep_integrity_scan.
    Identical to discovery_registry_consistency_check.py.
    """
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))
    from agentic_core.L0_routing.scripts.full_agent_discovery import perform_deep_integrity_scan
    from agentic_core.L0_routing.utils.ssot_discovery_util import load_agent_discovery
    raw = load_agent_discovery(project_root, force_reload=True)
    verified, stats = perform_deep_integrity_scan(raw, project_root)
    agent_ids = tuple(sorted(a.get('canonical_class', '') or a.get('class_name', '') for a in verified))
    fingerprint = _compute_fingerprint(agent_ids)
    return ActiveSetResult(agents=tuple(verified), agent_ids=agent_ids, count=len(verified), fingerprint=fingerprint, stats=stats)
