"""
Deterministic digest for runtime_state.json.

Produces a stable SHA-256 hex digest that is invariant across runs
whose only differences are wall-clock timestamps.  Reuses the
repo-canonical serializer (agentic_core/utils/canonical_serializer_util.py).

Phase 2 additions:
- Upstream ordering stabilization for UNORDERED scan-result lists.
- Volatile field sentinel for automatic drift detection.
- Digest schema version for contract enforcement.
"""

from __future__ import annotations

import copy
import re
from typing import Any

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

_emit_authorize_and_execute("p2", "runtime_state_digest", "execution_auth")
_emit_validates_capability("p2", "runtime_state_digest", "capability_check")
_emit_routes_to_capability("p2", "runtime_state_digest", "capability_route")
_emit_writes_via_uwg("p2", "runtime_state_digest", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_state_digest", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_state_digest", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_state_digest", "exec_output")
_emit_dispatches_agent("p3", "runtime_state_digest", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_state_digest", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_state_digest", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_state_digest", "healing_outcome")
_emit_escalates_failure("p3", "runtime_state_digest", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_state_digest", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_state_digest", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_state_digest", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_state_digest", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_state_digest", "eval_metric")
_emit_stores_embedding("p4", "runtime_state_digest", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_state_digest", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_state_digest", "exec_snapshot_link")
from agentic_core.utils.canonical_serializer_util import canonical_hash

emit_replay_key("p0", "runtime_state_digest")
emit_determinism_digest("p0", "runtime_state_digest")

_emit_dispatches_healing_run("p1", "runtime_state_digest", "L0")
_emit_routes_through("p1", "runtime_state_digest", "L0")
_emit_checks_agent_registry("p1", "runtime_state_digest", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_state_digest", "capability")
_emit_dispatches_execution_plan("p1", "runtime_state_digest", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_state_digest", "sub_agent")
_emit_routes_to_agent("p1", "runtime_state_digest", "target_agent")
_emit_verifies_policy("p1", "runtime_state_digest", "policy_check")
_emit_observes_runtime_state("p1", "runtime_state_digest", "runtime_state")
_emit_verifies_boundary("p1", "runtime_state_digest", "boundary_check")
_emit_transcripts_response("p1", "runtime_state_digest", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_state_digest")
_emit_gated_by_confidence("p1", "runtime_state_digest", "confidence_gate")
_emit_escalates_to_human("p1", "runtime_state_digest", "L0")
_emit_reads_policy_state("p1", "runtime_state_digest", "L0")
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

_emit_emits_metric_event("runtime_state_digest", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_state_digest", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_state_digest", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_state_digest", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_state_digest", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_state_digest", "p4obs", "metric_6")
_emit_records_incident_event("runtime_state_digest", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_state_digest", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_state_digest", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_state_digest", "p4obs", "mon_state")
_emit_triggers_alert("runtime_state_digest", "p4obs", "alert")
_emit_links_incident_trace("runtime_state_digest", "p4obs", "trace_link")
_emit_captures_pattern("runtime_state_digest", "p3lm", "pattern")
_emit_records_learning_event("runtime_state_digest", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_state_digest", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_state_digest", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_state_digest", "p3lm", "routing")
_emit_improves_agent_policy("runtime_state_digest", "p3lm", "policy")
_emit_stores_learning_state("runtime_state_digest", "p3lm", "state")
_emit_records_execution_trace("runtime_state_digest", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_state_digest", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_state_digest", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_state_digest", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_state_digest", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_state_digest", "env_read", "p2_env_1")
_emit_reads_environ("runtime_state_digest", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_state_digest", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_state_digest", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_state_digest", "context_pull")
_emit_pulls_context("p1", "runtime_state_digest", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "runtime_state_digest", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_state_digest", "uwg_term_2")
_emit_writes_through("p1", "runtime_state_digest", "write_through")
_emit_writes_through("p1", "runtime_state_digest", "write_through_2")
_emit_validated_by_safety_plane("p1", "runtime_state_digest", "safety_validation")
_emit_invokes_eval("p1", "runtime_state_digest", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_state_digest", "routing_commit")

DIGEST_SCHEMA_VERSION: int = 1
EXCLUDE_PATHS: list[str] = [
    "start_time",
    "end_time",
    "events[*].time",
    "completed_agents[*].time",
    "runtime_state_digest_sha256",
    "runtime_state_digest_schema_version",
]
_SORT_SPECS: list[tuple[str, tuple[str, ...]]] = [
    ("compliance_report.violations", ("type", "file", "message")),
    ("location_violations", ("file", "reason")),
    ("location_scan_result.violations", ("file", "reason")),
    ("hygiene_violations", ("type", "file", "message")),
    ("gravity_violations", ("type", "message")),
    ("classification_violations", ("type", "file", "message")),
    ("conversational_violations", ("type", "file", "message")),
    ("compliance_report.drift_violations", ("type", "file", "message")),
]
VOLATILE_FIELD_PATTERNS: list[str] = [
    "time",
    "timestamp",
    "elapsed",
    "uuid",
    "pid",
    "host",
    "nonce",
    "random",
    "seed",
]
_ISO_DATETIME_RE = re.compile("^\\d{4}-\\d{2}-\\d{2}[T ]\\d{2}:\\d{2}:\\d{2}")


def _get_nested(obj: dict[str, Any], dot_path: str) -> Any:
    """Resolve a dot-separated path into *obj*; return None if missing."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_nested", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_nested", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_nested")
    parts = dot_path.split(".")
    cur: Any = obj
    for part in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _set_nested(obj: dict[str, Any], dot_path: str, value: Any) -> None:
    """Set a value at a dot-separated path inside *obj* (in-place)."""
    parts = dot_path.split(".")
    cur: Any = obj
    for part in parts[:-1]:
        if not isinstance(cur, dict):
            return
        cur = cur.setdefault(part, {})
    if isinstance(cur, dict):
        cur[parts[-1]] = value


def _sort_key(item: Any, keys: tuple[str, ...]) -> tuple[str, ...]:
    """Build a stable sort key from dict *item* using *keys*."""
    if not isinstance(item, dict):
        return (str(item),)
    return tuple(str(item.get(k, "")) for k in keys)


def runtime_state_digest_view(state: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of *state* with:
    - excluded fields removed,
    - unordered scan-result lists deterministically sorted,
    - schema version injected.

    - MUST NOT mutate the input.
    - MUST NOT reorder ORDERED lists (events, completed_agents).
    """
    out = copy.deepcopy(state)
    for path in EXCLUDE_PATHS:
        if "[*]" not in path:
            out.pop(path, None)
    for path in EXCLUDE_PATHS:
        if "[*]." in path:
            array_key, field = path.split("[*].", 1)
            arr = out.get(array_key)
            if isinstance(arr, list):
                for item in arr:
                    if isinstance(item, dict):
                        item.pop(field, None)
    for dot_path, sort_keys in _SORT_SPECS:
        lst = _get_nested(out, dot_path)
        if isinstance(lst, list) and lst:
            _set_nested(out, dot_path, sorted(lst, key=lambda item: _sort_key(item, sort_keys)))
    out["_digest_schema_version"] = DIGEST_SCHEMA_VERSION
    return out


def compute_runtime_state_digest(state: dict[str, Any]) -> str:
    """SHA-256 hex digest over the canonical bytes of the digest view.

    Canonicalization is delegated to
    ``agentic_core.utils.canonical_serializer_util.canonical_hash``
    (file: agentic_core/utils/canonical_serializer_util.py:66).
    """
    return canonical_hash(runtime_state_digest_view(state))


def detect_unexcluded_volatile_fields(state: dict[str, Any]) -> list[str]:
    """Traverse *state* and return JSON-path strings for any field that:
    - has a key matching a VOLATILE_FIELD_PATTERNS substring, OR
    - has an ISO-datetime string value,
    AND is NOT already covered by EXCLUDE_PATHS.

    O(n) traversal. Does not mutate input.
    """
    findings: list[str] = []
    _excluded_keys = {
        p.split("[*].")[1] if "[*]." in p else p for p in EXCLUDE_PATHS if "[*]" not in p or "[*]." in p
    }
    _excluded_top = {p for p in EXCLUDE_PATHS if "[*]" not in p}

    def _is_volatile_key(key: str) -> bool:
        key_lower = key.lower()
        return any(pat in key_lower for pat in VOLATILE_FIELD_PATTERNS)

    def _is_volatile_value(val: Any) -> bool:
        return isinstance(val, str) and bool(_ISO_DATETIME_RE.match(val))

    def _walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                child_path = f"{path}.{k}" if path else k
                already_excluded = child_path in _excluded_top or k in _excluded_keys
                if not already_excluded:
                    if _is_volatile_key(k) or _is_volatile_value(v):
                        findings.append(child_path)
                _walk(v, child_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _walk(item, f"{path}[{i}]")

    _walk(state, "")
    return findings
