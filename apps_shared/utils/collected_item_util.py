"""
base_collector.py - Collector Module

Domain: metrics
Generated: 2025-12-07T12:07:59.846192
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "collected_item_util", "p0_governance")
_emit_reads_policy_state("p0", "collected_item_util", "policy_binding")
_emit_snapshots_state("p0", "collected_item_util", "state_snapshot")
emit_replay_key("p0", "collected_item_util")
emit_determinism_digest("p0", "collected_item_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "collected_item_util", "execution_auth")
_emit_validates_capability("p2", "collected_item_util", "capability_check")
_emit_routes_to_capability("p2", "collected_item_util", "capability_route")
_emit_writes_via_uwg("p2", "collected_item_util", "uwg_write")
_emit_blocks_direct_write("p2", "collected_item_util", "direct_write_block")
_emit_records_tool_invocation("p2", "collected_item_util", "tool_invocation")
_emit_captures_execution_output("p2", "collected_item_util", "exec_output")
_emit_dispatches_agent("p3", "collected_item_util", "agent_dispatch")
_emit_coordinates_agents("p3", "collected_item_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "collected_item_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "collected_item_util", "healing_outcome")
_emit_escalates_failure("p3", "collected_item_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "collected_item_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "collected_item_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "collected_item_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "collected_item_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "collected_item_util", "eval_metric")
_emit_stores_embedding("p4", "collected_item_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "collected_item_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "collected_item_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class CollectedItem:
    """A collected item."""

    source: str
    data: Any
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class BaseCollector:
    """Collector for metrics domain."""

    def __init__(self, config: dict[str, object] | None = None):
        self.config = config or {}
        self.items: dict[str, list[CollectedItem]] = defaultdict(list)
        self.max_items = self.config.get("max_items", 1000)
        logger.info(f"Initialized {self.__class__.__name__}")

    def collect(self, source: str, data: object) -> None:
        """Collect data from source."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaseCollector.collect")

        item = CollectedItem(source=source, data=data)
        self.items[source].append(item)
        if len(self.items[source]) > self.max_items:
            self.items[source] = self.items[source][-self.max_items :]
        logger.debug(f"Collected item from {source}")

    def get_items(self, source: str | None = None) -> list[CollectedItem]:
        """Get collected items."""
        if source:
            return self.items.get(source, [])
        return [item for items in self.items.values() for item in items]

    def flush(self, source: str | None = None) -> list[CollectedItem]:
        """Flush and return items."""
        if source:
            items = self.items.pop(source, [])
        else:
            items = self.get_items()
            self.items.clear()
        return items


_collector = BaseCollector()


def collect(source: str, data: object) -> None:
    """Collect data to global collector."""
    _collector.collect(source, data)


def get_collected(source: str | None = None) -> list[CollectedItem]:
    """Get items from global collector."""
    return _collector.get_items(source)
