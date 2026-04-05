"""Runtime ADG materializer — converts drained OTel spans into a RuntimeADGSnapshot.

Pipeline:
    tracer.drain_completed_spans()   →  list[dict]
    RuntimeADGMaterializer.materialize(spans, mission)  →  RuntimeADGSnapshot

Node extraction:
    Each span dict becomes one RuntimeADGNode.

Edge extraction:
    parent_child   — span with non-empty parent_span_id gets an edge from parent.
    temporal_sequence — consecutive spans (by ts_utc) within the same trace get
                        an ordered edge so the execution path is reconstructable.

Validation:
    Input validation, span structure validation, and graceful error recovery
    ensure robust operation even with malformed or incomplete span data.
"""

from __future__ import annotations

import json
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    RuntimeADGSnapshot,
    attributes_to_json,
    create_runtime_adg_snapshot,
)

emit_determinism_digest("runtime_adg_materializer", "runtime_adg_materializer_digest")
record_execution_trace("runtime_adg_materializer", "runtime_adg_materializer_trace")

_ROOT_SENTINEL = "__root__"


def _extract_node(span: dict[str, Any]) -> RuntimeADGNode | None:
    """Extract RuntimeADGNode from span dict with validation and safe defaults.

    Returns None if span lacks required span_id field.
    """
    # Validate required span_id
    span_id = span.get("span_id", "")
    if not span_id or not isinstance(span_id, str):
        return None

    raw_attrs = span.get("attributes", {})
    if isinstance(raw_attrs, str):
        try:
            raw_attrs = json.loads(raw_attrs)
        except (ValueError, TypeError):
            raw_attrs = {}

    # Safely extract and validate timestamp
    try:
        ts_utc = int(span.get("ts_utc", 0))
    except (ValueError, TypeError):
        ts_utc = 0

    # Safely extract and validate duration
    try:
        duration_ms = float(span.get("duration_ms", 0.0))
        if duration_ms < 0:
            duration_ms = 0.0
    except (ValueError, TypeError):
        duration_ms = 0.0

    # Validate status is one of allowed values
    status = str(span.get("status", "ok"))
    if status not in ("ok", "error"):
        status = "ok"

    return RuntimeADGNode(
        node_id=span_id,
        name=str(span.get("name", ""))[:256],  # Limit name length
        kind=str(span.get("kind", "unknown"))[:64],
        layer=str(span.get("layer", ""))[:8],  # L0-L6 format
        component=str(span.get("component", ""))[:128],
        started_at_utc=ts_utc,
        duration_ms=duration_ms,
        status=status,
        attributes_json=attributes_to_json(raw_attrs if isinstance(raw_attrs, dict) else {}),
    )


def _extract_parent_child_edges(spans: list[dict[str, Any]]) -> list[RuntimeADGEdge]:
    """Extract parent-child edges from spans with validation.

    Each span with a valid span_id gets a parent_child edge:
    - If parent_span_id is present and valid: edge from parent to child
    - Otherwise: edge from __root__ sentinel to child
    """
    edges: list[RuntimeADGEdge] = []
    seen_span_ids: set[str] = set()

    for span in spans:
        span_id = str(span.get("span_id", ""))
        if not span_id:
            continue

        # Skip duplicate span_ids (keep first occurrence)
        if span_id in seen_span_ids:
            continue
        seen_span_ids.add(span_id)

        parent_id = str(span.get("parent_span_id", ""))
        # Use parent if valid and exists in seen spans, otherwise root
        src = parent_id if parent_id and parent_id in seen_span_ids else _ROOT_SENTINEL
        edges.append(RuntimeADGEdge(src_id=src, dst_id=span_id, relation="parent_child"))

    return edges


def _extract_temporal_edges(spans: list[dict[str, Any]]) -> list[RuntimeADGEdge]:
    """Extract temporal sequence edges from spans with validation.

    Orders spans by timestamp and span_id, then creates edges between consecutive spans.
    """
    if len(spans) < 2:
        return []

    def safe_ts_utc(s: dict[str, Any]) -> int:
        """Safely extract timestamp, returning 0 for invalid values."""
        try:
            val = s.get("ts_utc", 0)
            return int(val)
        except (ValueError, TypeError):
            return 0

    ordered = sorted(spans, key=lambda s: (safe_ts_utc(s), str(s.get("span_id", ""))))
    edges: list[RuntimeADGEdge] = []
    for prev, curr in zip(ordered, ordered[1:]):
        src_id = str(prev.get("span_id", ""))
        dst_id = str(curr.get("span_id", ""))
        if src_id and dst_id and src_id != dst_id:
            edges.append(RuntimeADGEdge(src_id=src_id, dst_id=dst_id, relation="temporal_sequence"))
    return edges


# =============================================================================
# Wave 2: Semantic Edge Extraction
# =============================================================================

SEMANTIC_EDGE_RELATIONS = frozenset({
    "actor", "action", "target", "dependency", "read_edge", "write_edge",
    "tool_invocation_edge", "orchestration_handoff_edge", "retry_edge",
    "evaluation_edge", "policy_validation_edge", "human_escalation_edge",
    "failure_propagation_edge", "outcome_edge",
})


def _extract_semantic_edges(spans: list[dict[str, Any]]) -> list[RuntimeADGEdge]:
    """Extract semantic edges based on span attributes and relationships.

    Wave 2: Extracts 13 edge types for comprehensive runtime graph representation:
    - actor: Entity initiating an action
    - action: Action being performed
    - target: Target of an action
    - dependency: Dependency relationship
    - read_edge: Read operation
    - write_edge: Write operation
    - tool_invocation_edge: Tool being invoked
    - orchestration_handoff_edge: Handoff between orchestrators
    - retry_edge: Retry relationship
    - evaluation_edge: Evaluation operation
    - policy_validation_edge: Policy validation
    - human_escalation_edge: Human escalation
    - failure_propagation_edge: Failure propagation
    - outcome_edge: Outcome relationship
    """
    edges: list[RuntimeADGEdge] = []
    span_map: dict[str, dict[str, Any]] = {}

    # Build span lookup map
    for span in spans:
        span_id = str(span.get("span_id", ""))
        if span_id:
            span_map[span_id] = span

    for span in spans:
        span_id = str(span.get("span_id", ""))
        if not span_id:
            continue

        attrs = span.get("attributes", {})
        if isinstance(attrs, str):
            try:
                attrs = json.loads(attrs)
            except (ValueError, TypeError):
                attrs = {}
        if not isinstance(attrs, dict):
            attrs = {}

        # Extract semantic relationships from attributes
        edges.extend(_extract_actor_edges(span_id, attrs, span_map))
        edges.extend(_extract_target_edges(span_id, attrs, span_map))
        edges.extend(_extract_dependency_edges(span_id, attrs, span_map))
        edges.extend(_extract_read_write_edges(span_id, attrs))
        edges.extend(_extract_tool_invocation_edges(span_id, attrs))
        edges.extend(_extract_orchestration_handoff_edges(span_id, attrs, span_map))
        edges.extend(_extract_retry_edges(span_id, attrs, span_map))
        edges.extend(_extract_evaluation_edges(span_id, attrs))
        edges.extend(_extract_policy_validation_edges(span_id, attrs))
        edges.extend(_extract_human_escalation_edges(span_id, attrs))
        edges.extend(_extract_failure_propagation_edges(span_id, attrs, span_map))
        edges.extend(_extract_outcome_edges(span_id, attrs))

    return edges


def _extract_actor_edges(
    span_id: str, attrs: dict[str, Any], span_map: dict[str, dict[str, Any]]
) -> list[RuntimeADGEdge]:
    """Extract actor edges from span attributes."""
    edges: list[RuntimeADGEdge] = []
    actor_id = attrs.get("actor_id") or attrs.get("agent_id") or attrs.get("component")
    if actor_id and isinstance(actor_id, str):
        edges.append(RuntimeADGEdge(
            src_id=str(actor_id)[:128],
            dst_id=span_id,
            relation="actor"
        ))
    return edges


def _extract_target_edges(
    span_id: str, attrs: dict[str, Any], span_map: dict[str, dict[str, Any]]
) -> list[RuntimeADGEdge]:
    """Extract target edges from span attributes."""
    edges: list[RuntimeADGEdge] = []
    target_id = attrs.get("target_id") or attrs.get("destination") or attrs.get("dest")
    if target_id and isinstance(target_id, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=str(target_id)[:128],
            relation="target"
        ))
    return edges


def _extract_dependency_edges(
    span_id: str, attrs: dict[str, Any], span_map: dict[str, dict[str, Any]]
) -> list[RuntimeADGEdge]:
    """Extract dependency edges from span attributes."""
    edges: list[RuntimeADGEdge] = []
    depends_on = attrs.get("depends_on") or attrs.get("dependency")
    if depends_on:
        if isinstance(depends_on, str):
            edges.append(RuntimeADGEdge(
                src_id=str(depends_on)[:128],
                dst_id=span_id,
                relation="dependency"
            ))
        elif isinstance(depends_on, list):
            for dep in depends_on[:10]:  # Limit dependencies
                if isinstance(dep, str):
                    edges.append(RuntimeADGEdge(
                        src_id=str(dep)[:128],
                        dst_id=span_id,
                        relation="dependency"
                    ))
    return edges


def _extract_read_write_edges(span_id: str, attrs: dict[str, Any]) -> list[RuntimeADGEdge]:
    """Extract read and write edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    # Read edges
    reads_from = attrs.get("reads_from") or attrs.get("source")
    if reads_from and isinstance(reads_from, str):
        edges.append(RuntimeADGEdge(
            src_id=str(reads_from)[:128],
            dst_id=span_id,
            relation="read_edge"
        ))

    # Write edges
    writes_to = attrs.get("writes_to") or attrs.get("destination")
    if writes_to and isinstance(writes_to, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=str(writes_to)[:128],
            relation="write_edge"
        ))

    return edges


def _extract_tool_invocation_edges(span_id: str, attrs: dict[str, Any]) -> list[RuntimeADGEdge]:
    """Extract tool invocation edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    # Check for tool invocation attributes
    tool_name = attrs.get("tool_name") or attrs.get("tool")
    span_kind = attrs.get("span_kind", "")

    if span_kind == "tool" and tool_name and isinstance(tool_name, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"tool.{str(tool_name)[:120]}",
            relation="tool_invocation_edge"
        ))

    # Also check explicit tool_invocation attribute
    invoked_tool = attrs.get("tool_invoked") or attrs.get("invoked_tool")
    if invoked_tool and isinstance(invoked_tool, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"tool.{str(invoked_tool)[:120]}",
            relation="tool_invocation_edge"
        ))

    return edges


def _extract_orchestration_handoff_edges(
    span_id: str, attrs: dict[str, Any], span_map: dict[str, dict[str, Any]]
) -> list[RuntimeADGEdge]:
    """Extract orchestration handoff edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    handoff_to = attrs.get("handoff_to") or attrs.get("next_orchestrator")
    if handoff_to and isinstance(handoff_to, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=str(handoff_to)[:128],
            relation="orchestration_handoff_edge"
        ))

    # Check span kind for orchestrator
    span_kind = attrs.get("span_kind", "")
    orchestrator_name = attrs.get("orchestrator_name")
    if span_kind == "orchestrator" and orchestrator_name:
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"orchestrator.{str(orchestrator_name)[:115]}",
            relation="orchestration_handoff_edge"
        ))

    return edges


def _extract_retry_edges(
    span_id: str, attrs: dict[str, Any], span_map: dict[str, dict[str, Any]]
) -> list[RuntimeADGEdge]:
    """Extract retry edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    retry_of = attrs.get("retry_of") or attrs.get("previous_attempt")
    if retry_of and isinstance(retry_of, str):
        edges.append(RuntimeADGEdge(
            src_id=str(retry_of)[:128],
            dst_id=span_id,
            relation="retry_edge"
        ))

    # Check for retry_count indicating this is a retry
    retry_count = attrs.get("retry_count") or attrs.get("attempt")
    if retry_count and int(retry_count) > 0:
        # Link to parent span as retry
        parent_span_id = attrs.get("parent_retry_span")
        if parent_span_id and isinstance(parent_span_id, str):
            edges.append(RuntimeADGEdge(
                src_id=str(parent_span_id)[:128],
                dst_id=span_id,
                relation="retry_edge"
            ))

    return edges


def _extract_evaluation_edges(span_id: str, attrs: dict[str, Any]) -> list[RuntimeADGEdge]:
    """Extract evaluation edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    # Check for evaluation attributes
    evaluated = attrs.get("evaluated") or attrs.get("evaluation_target")
    if evaluated and isinstance(evaluated, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=str(evaluated)[:128],
            relation="evaluation_edge"
        ))

    # Check span kind
    span_kind = attrs.get("span_kind", "")
    if span_kind == "evaluation":
        eval_subject = attrs.get("subject") or attrs.get("eval_subject")
        if eval_subject and isinstance(eval_subject, str):
            edges.append(RuntimeADGEdge(
                src_id=span_id,
                dst_id=str(eval_subject)[:128],
                relation="evaluation_edge"
            ))

    return edges


def _extract_policy_validation_edges(span_id: str, attrs: dict[str, Any]) -> list[RuntimeADGEdge]:
    """Extract policy validation edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    # Check for policy validation attributes
    policy_check = attrs.get("policy_checked") or attrs.get("validated_policy")
    if policy_check and isinstance(policy_check, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"policy.{str(policy_check)[:123]}",
            relation="policy_validation_edge"
        ))

    # Check for guardrail triggers
    guardrail_type = attrs.get("guardrail_type") or attrs.get("guardrail_triggered")
    if guardrail_type and isinstance(guardrail_type, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"guardrail.{str(guardrail_type)[:120]}",
            relation="policy_validation_edge"
        ))

    return edges


def _extract_human_escalation_edges(span_id: str, attrs: dict[str, Any]) -> list[RuntimeADGEdge]:
    """Extract human escalation edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    escalated_to = attrs.get("escalated_to") or attrs.get("human_escalation")
    if escalated_to and isinstance(escalated_to, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"human.{str(escalated_to)[:124]}",
            relation="human_escalation_edge"
        ))

    # Check for escalation reason
    escalation_reason = attrs.get("escalation_reason") or attrs.get("human_override")
    if escalation_reason:
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id="human.escalation",
            relation="human_escalation_edge"
        ))

    return edges


def _extract_failure_propagation_edges(
    span_id: str, attrs: dict[str, Any], span_map: dict[str, dict[str, Any]]
) -> list[RuntimeADGEdge]:
    """Extract failure propagation edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    # Check for error status
    status = attrs.get("status", "")
    error_type = attrs.get("error_type") or attrs.get("exception")

    if status == "error" or error_type:
        # Propagate to parent or dependent spans
        failed_component = attrs.get("component") or attrs.get("failed_agent")
        if failed_component and isinstance(failed_component, str):
            edges.append(RuntimeADGEdge(
                src_id=span_id,
                dst_id=f"failure.{str(failed_component)[:121]}",
                relation="failure_propagation_edge"
            ))

        # Check for affected_by attribute
        affected_by = attrs.get("affected_by") or attrs.get("failure_source")
        if affected_by and isinstance(affected_by, str):
            edges.append(RuntimeADGEdge(
                src_id=str(affected_by)[:128],
                dst_id=span_id,
                relation="failure_propagation_edge"
            ))

    return edges


def _extract_outcome_edges(span_id: str, attrs: dict[str, Any]) -> list[RuntimeADGEdge]:
    """Extract outcome edges from span attributes."""
    edges: list[RuntimeADGEdge] = []

    # Check for outcome attributes
    outcome = attrs.get("outcome") or attrs.get("result")
    if outcome and isinstance(outcome, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"outcome.{str(outcome)[:122]}",
            relation="outcome_edge"
        ))

    # Check for result_status
    result_status = attrs.get("result_status") or attrs.get("status")
    if result_status and isinstance(result_status, str):
        edges.append(RuntimeADGEdge(
            src_id=span_id,
            dst_id=f"outcome.{str(result_status)[:122]}",
            relation="outcome_edge"
        ))

    return edges


class RuntimeADGMaterializer:
    """Converts a list of drained OTel span dicts into a ``RuntimeADGSnapshot``.

    Usage::

        spans = tracer.drain_completed_spans()
        snapshot = RuntimeADGMaterializer().materialize(spans, mission="campaign-run-001")
    """

    def materialize(
        self,
        spans: list[dict[str, Any]],
        mission: str = "",
        trace_id: str = "",
    ) -> RuntimeADGSnapshot:
        """Materialise a ``RuntimeADGSnapshot`` from drained span records.

        Parameters
        ----------
        spans:
            Span dicts as returned by ``OpenTelemetryTracingAdapter.drain_completed_spans()``.
        mission:
            Human-readable mission label. Falls back to root span name if empty.
        trace_id:
            Explicit trace ID. Falls back to first span's trace_id if empty.

        Returns
        -------
        RuntimeADGSnapshot
            Immutable, content-addressed snapshot.

        Validation:
            - Empty spans: returns empty snapshot with zero timestamps
            - Missing fields: safe defaults applied
            - Invalid types: coerced or set to defaults
            - Duplicate span_ids: first occurrence kept
        """
        # Validate and sanitize mission
        mission = str(mission)[:256] if mission else ""

        if not spans:
            return create_runtime_adg_snapshot(
                trace_id=str(trace_id)[:128] if trace_id else "",
                mission=mission,
                started_at_utc=0,
                ended_at_utc=0,
                nodes=(),
                edges=(),
            )

        resolved_trace_id = str(trace_id)[:128] if trace_id else str(spans[0].get("trace_id", ""))[:128]
        resolved_mission = mission or _infer_mission(spans)

        # Extract nodes with validation
        nodes_list: list[RuntimeADGNode] = []
        for span in spans:
            node = _extract_node(span)
            if node is not None:
                nodes_list.append(node)

        nodes = tuple(nodes_list)

        # Extract edges (Wave 2: Added semantic edge extraction)
        parent_child = _extract_parent_child_edges(spans)
        temporal = _extract_temporal_edges(spans)
        semantic = _extract_semantic_edges(spans)  # Wave 2: 13 edge types
        all_edges = tuple(parent_child + temporal + semantic)

        # Calculate time bounds with validation
        if nodes_list:
            started = min(n.started_at_utc for n in nodes_list)
            ended = max(n.started_at_utc + int(n.duration_ms) for n in nodes_list)
        else:
            started = 0
            ended = 0

        return create_runtime_adg_snapshot(
            trace_id=resolved_trace_id,
            mission=resolved_mission,
            started_at_utc=started,
            ended_at_utc=ended,
            nodes=nodes,
            edges=all_edges,
        )


def _infer_mission(spans: list[dict[str, Any]]) -> str:
    root_candidates = [s for s in spans if not s.get("parent_span_id", "")]
    if root_candidates:
        attrs = root_candidates[0].get("attributes", {})
        if isinstance(attrs, dict) and "mission" in attrs:
            return str(attrs["mission"])
        return str(root_candidates[0].get("name", ""))
    return str(spans[0].get("name", "")) if spans else ""
