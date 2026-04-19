"""R3: ADG-backed agent registry for indexed agent discovery and capability routing."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Final
from tqdm import tqdm

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine, AgentCapability

_BOOTSTRAP_TELEMETRY_EMITTED = False
_BOOTSTRAP_TELEMETRY_EVENTS: Final[tuple[tuple[str, tuple[object, ...]], ...]] = (
    ("_emit_records_execution_trace", ("p0", "evidence", "adg_backed_registry")),
    ("_emit_applies_guardrail", ("p0", "adg_backed_registry", "p0_governance")),
    ("_emit_reads_policy_state", ("p0", "adg_backed_registry", "policy_binding")),
    ("_emit_snapshots_state", ("p0", "adg_backed_registry", "state_snapshot")),
    ("_emit_emits_metric_event", ("adg_backed_registry", "p4obs", "metric_1")),
    ("_emit_emits_metric_event", ("adg_backed_registry", "p4obs", "metric_2")),
    ("_emit_emits_metric_event", ("adg_backed_registry", "p4obs", "metric_3")),
    ("_emit_emits_metric_event", ("adg_backed_registry", "p4obs", "metric_4")),
    ("_emit_emits_metric_event", ("adg_backed_registry", "p4obs", "metric_5")),
    ("_emit_emits_metric_event", ("adg_backed_registry", "p4obs", "metric_6")),
    ("_emit_records_incident_event", ("adg_backed_registry", "p4obs", "incident")),
    ("_emit_captures_runtime_anomaly", ("adg_backed_registry", "p4obs", "anomaly")),
    ("_emit_writes_observability_log", ("adg_backed_registry", "p4obs", "obs_log")),
    ("_emit_updates_monitoring_state", ("adg_backed_registry", "p4obs", "mon_state")),
    ("_emit_triggers_alert", ("adg_backed_registry", "p4obs", "alert")),
    ("_emit_links_incident_trace", ("adg_backed_registry", "p4obs", "trace_link")),
    ("_emit_captures_pattern", ("adg_backed_registry", "p3lm", "pattern")),
    ("_emit_records_learning_event", ("adg_backed_registry", "p3lm", "learning_event")),
    ("_emit_writes_learning_snapshot", ("adg_backed_registry", "p3lm", "snapshot")),
    ("_emit_feeds_meta_learning", ("adg_backed_registry", "p3lm", "meta_feed")),
    ("_emit_updates_routing_strategy", ("adg_backed_registry", "p3lm", "routing")),
    ("_emit_improves_agent_policy", ("adg_backed_registry", "p3lm", "policy")),
    ("_emit_stores_learning_state", ("adg_backed_registry", "p3lm", "state")),
    ("_emit_records_execution_trace", ("adg_backed_registry", "L0_ROUTING", "p2_trace_1")),
    ("_emit_records_execution_trace", ("adg_backed_registry", "L1_REASONING", "p2_trace_2")),
    ("_emit_records_execution_trace", ("adg_backed_registry", "L2_EXECUTION", "p2_trace_3")),
    ("_emit_records_execution_trace", ("adg_backed_registry", "L3_ORCHESTRATION", "p2_trace_4")),
    ("_emit_records_execution_trace", ("adg_backed_registry", "L4_STATE", "p2_trace_5")),
    ("_emit_reads_environ", ("adg_backed_registry", "env_read", "p2_env_1")),
    ("_emit_reads_environ", ("adg_backed_registry", "env_read", "p2_env_2")),
    ("_emit_reads_runtime_state", ("adg_backed_registry", "runtime_state", "p2_rt_1")),
    ("_emit_reads_runtime_state", ("adg_backed_registry", "runtime_state", "p2_rt_2")),
    ("_emit_pulls_context", ("p1", "adg_backed_registry", "context_pull")),
    ("_emit_pulls_context", ("p1", "adg_backed_registry", "context_pull_2")),
    ("_emit_execution_terminates_at_uwg", ("p1", "adg_backed_registry", "uwg_term")),
    ("_emit_execution_terminates_at_uwg", ("p1", "adg_backed_registry", "uwg_term_2")),
    ("_emit_writes_through", ("p1", "adg_backed_registry", "write_through")),
    ("_emit_writes_through", ("p1", "adg_backed_registry", "write_through_2")),
    ("_emit_validated_by_safety_plane", ("p1", "adg_backed_registry", "safety_validation")),
    ("_emit_invokes_eval", ("p1", "adg_backed_registry", "eval_call")),
    ("_emit_proposal_commits_routing", ("p1", "adg_backed_registry", "routing_commit")),
    ("_emit_escalates_to_human", ("p1", "adg_backed_registry", "human_escalation")),
    ("_emit_routes_through", ("p1", "adg_backed_registry", "route_through")),
    ("_emit_checks_agent_registry", ("p1", "adg_backed_registry", "agent_registry")),
    ("_emit_validates_agent_capability", ("p1", "adg_backed_registry", "capability")),
    ("_emit_dispatches_execution_plan", ("p1", "adg_backed_registry", "exec_plan")),
    ("_emit_agent_executes_agent", ("p1", "adg_backed_registry", "sub_agent")),
    ("_emit_routes_to_agent", ("p1", "adg_backed_registry", "target_agent")),
    ("_emit_verifies_policy", ("p1", "adg_backed_registry", "policy_check")),
    ("_emit_observes_runtime_state", ("p1", "adg_backed_registry", "runtime_state")),
    ("_emit_verifies_boundary", ("p1", "adg_backed_registry", "boundary_check")),
    ("_emit_transcripts_response", ("p1", "adg_backed_registry", "transcript")),
    ("_emit_hard_fails_untranscripted", ("p1", "adg_backed_registry")),
    ("_emit_gated_by_confidence", ("p1", "adg_backed_registry", "confidence_gate")),
    ("emit_replay_key", ("p0", "adg_backed_registry")),
    ("emit_determinism_digest", ("p0", "adg_backed_registry")),
    ("_emit_signs_execution_trace", ("p0", "p0hash", "p0_trace", 0)),
    ("_emit_authorize_and_execute", ("p2", "adg_backed_registry", "execution_auth")),
    ("_emit_validates_capability", ("p2", "adg_backed_registry", "capability_check")),
    ("_emit_routes_to_capability", ("p2", "adg_backed_registry", "capability_route")),
    ("_emit_writes_via_uwg", ("p2", "adg_backed_registry", "uwg_write")),
    ("_emit_blocks_direct_write", ("p2", "adg_backed_registry", "direct_write_block")),
    ("_emit_records_tool_invocation", ("p2", "adg_backed_registry", "tool_invocation")),
    ("_emit_captures_execution_output", ("p2", "adg_backed_registry", "exec_output")),
    ("_emit_dispatches_agent", ("p3", "adg_backed_registry", "agent_dispatch")),
    ("_emit_coordinates_agents", ("p3", "adg_backed_registry", "agent_coordination")),
    ("_emit_records_workflow_lineage", ("p3", "adg_backed_registry", "workflow_lineage")),
    ("_emit_records_healing_outcome", ("p3", "adg_backed_registry", "healing_outcome")),
    ("_emit_escalates_failure", ("p3", "adg_backed_registry", "failure_escalation")),
    ("_emit_orchestrates_workflow", ("p3", "adg_backed_registry", "workflow_orchestration")),
    ("_emit_dispatches_healing_run", ("p3", "adg_backed_registry", "healing_dispatch")),
    ("_emit_invokes_evaluation", ("p3", "adg_backed_registry", "evaluation_signal")),
    ("_emit_records_telemetry_event", ("p4", "adg_backed_registry", "telemetry_event")),
    ("_emit_captures_evaluation_metric", ("p4", "adg_backed_registry", "eval_metric")),
    ("_emit_stores_embedding", ("p4", "adg_backed_registry", "embedding_store")),
    ("_emit_updates_meta_learning_state", ("p4", "adg_backed_registry", "meta_learning")),
    ("_emit_links_execution_to_snapshot", ("p4", "adg_backed_registry", "exec_snapshot_link")),
)


def _emit_bootstrap_telemetry() -> None:
    """Emit lifecycle bootstrap telemetry once, without breaking module import."""
    global _BOOTSTRAP_TELEMETRY_EMITTED

    if _BOOTSTRAP_TELEMETRY_EMITTED:
        return

    try:
        from agentic_core.runtime.contracts import lifecycle_trace_contract as lifecycle
    except ImportError:  # guardian: allow-return-none-swallow -- telemetry bootstrap: lifecycle contract absent, early exit prevents further emission
        logger.debug("Lifecycle trace contract unavailable; skipping ADG registry bootstrap telemetry")
        _BOOTSTRAP_TELEMETRY_EMITTED = True
        return

    for emitter_name, emitter_args in _BOOTSTRAP_TELEMETRY_EVENTS:
        emitter = getattr(lifecycle, emitter_name, None)
        if not callable(emitter):
            logger.debug("Lifecycle emitter %s is unavailable; skipping", emitter_name)
            continue

        try:
            emitter(*emitter_args)
        except Exception:  # guardian: allow-broad-exception allow-log-and-swallow -- lifecycle telemetry emitters are untrusted; failures must never crash module load
            logger.debug("Lifecycle bootstrap emitter %s failed", emitter_name, exc_info=True)

    _BOOTSTRAP_TELEMETRY_EMITTED = True


def _normalize_lookup_value(value: str, field_name: str) -> str:
    """Validate and normalize external lookup values."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a non-empty string")

    return normalized


class ADGBackedAgentRegistry:
    """Agent registry backed by ADG inheritance and composition graph indexes."""

    def __init__(self, query_engine: "ADGRuntimeQueryEngine") -> None:
        _emit_bootstrap_telemetry()

        if query_engine is None:
            raise ValueError("query_engine is required")

        for required_method in ("find_agents_by_base_class", "find_agents_by_capability", "stats"):
            if not callable(getattr(query_engine, required_method, None)):
                raise TypeError(f"query_engine must provide callable '{required_method}'")

        self.query_engine = query_engine
        self._capability_index = self._build_capability_index()

    def _build_capability_index(self) -> dict[str, list["AgentCapability"]]:
        """Build a local capability index from a public or private engine mapping."""
        raw_index = getattr(self.query_engine, "composition_index", None)
        if raw_index is None:
            raw_index = getattr(self.query_engine, "_composition_index", None)

        if raw_index is None:
            logger.debug("Query engine does not expose a composition index; capability cache disabled")
            return {}

        if not isinstance(raw_index, Mapping):
            raise TypeError("query_engine composition index must be a mapping")

        index: dict[str, list["AgentCapability"]] = {}
        for symbol, capabilities in tqdm(raw_index.items(), desc="Processing", unit="item"):
            normalized_symbol = _normalize_lookup_value(str(symbol), "capability symbol")
            if capabilities is None:
                index[normalized_symbol] = []
                continue

            if isinstance(capabilities, (str, bytes)):
                raise TypeError("capability index entries must be iterable collections, not strings")

            try:
                index[normalized_symbol] = list(capabilities)
            except TypeError as exc:
                raise TypeError(
                    f"capability index entry for '{normalized_symbol}' is not iterable",
                ) from exc

        return index

    def refresh(self) -> None:
        """Rebuild the local capability cache from the current query engine state."""
        self._capability_index = self._build_capability_index()

    def find_by_base_class(self, base_class: str) -> list[str]:
        """Lookup ADG module names for subclasses of the supplied base class."""
        normalized_base_class = _normalize_lookup_value(base_class, "base_class")
        result = self.query_engine.find_agents_by_base_class(normalized_base_class)
        return list(result or [])

    def find_by_capability(self, capability: str) -> list["AgentCapability"]:
        """Lookup agent capabilities via the cached index or query-engine fallback."""
        normalized_capability = _normalize_lookup_value(capability, "capability")

        cached = self._capability_index.get(normalized_capability)
        if cached is not None:
            return list(cached)

        result = self.query_engine.find_agents_by_capability(normalized_capability)
        return list(result or [])

    def get_execution_profile(self, agent_id: str) -> Any:
        """Return the canonical execution profile when available."""
        try:
            from agentic_core.agents.types.agent_registry import get_profile
        except ImportError:  # guardian: allow-return-none-swallow -- registry unavailable: non-fatal, caller handles None
            logger.debug("Canonical AGENT_REGISTRY is unavailable; agent_id=%s", agent_id)
            return None

        try:
            return get_profile(agent_id)
        except KeyError:  # guardian: allow-return-none-swallow -- agent not found: non-fatal, caller handles None
            logger.debug("Canonical AGENT_REGISTRY missing agent_id=%s", agent_id)
            return None

    def all_sovereign_agents(self) -> list[str]:
        """Return all known SovereignBaseAgent subclasses via the ADG inheritance graph."""
        return self.find_by_base_class("SovereignBaseAgent")

    def stats(self) -> dict[str, int]:
        """Return registry and query-engine stats, filtering out non-integer values."""
        raw_stats = self.query_engine.stats()
        if raw_stats is None:
            raw_stats = {}
        if not isinstance(raw_stats, dict):
            raise TypeError("query_engine.stats() must return a dict")

        stats: dict[str, int] = {
            "sovereign_agents": len(self.all_sovereign_agents()),
            "capability_symbols": len(self._capability_index),
        }

        for key, value in raw_stats.items():
            if isinstance(value, bool):
                stats[str(key)] = int(value)
            elif isinstance(value, int):
                stats[str(key)] = value
            else:
                logger.debug("Ignoring non-integer query engine stat %s=%r", key, value)

        return stats


def get_adg_registry(repo_root: str | None = None, force_fresh: bool = False) -> ADGBackedAgentRegistry:
    """Factory: build an ADGBackedAgentRegistry from the singleton query engine."""
    _emit_bootstrap_telemetry()
    from agentic_core.adg.runtime.query_engine import get_runtime_query_engine

    engine = get_runtime_query_engine(repo_root=repo_root, force_fresh=force_fresh)
    return ADGBackedAgentRegistry(engine)


__all__ = ["ADGBackedAgentRegistry", "get_adg_registry"]
